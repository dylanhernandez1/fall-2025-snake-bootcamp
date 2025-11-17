import asyncio
import time
import socketio
from aiohttp import web
from typing import Any, Dict

from agent import DQN
from game import Game


# Create SocketIO server with CORS settings
sio = socketio.AsyncServer(cors_allowed_origins="*")

# Create web application
app = web.Application()

# Attach socketio to the app
sio.attach(app)


# Basic health check endpoint
async def handle_ping(request: Any) -> Any:
    """Simple ping endpoint to keep server alive and check if it's running"""
    return web.json_response({"message": "pong"})


@sio.event
async def connect(sid: str, environ: Dict[str, Any]) -> None:
    """Handle client connections - called when a frontend connects to the server"""
    print(f"[CONNECT] Client connected: sid={sid}")
    
    # Initialize session with game and agent as None, not active yet
    await sio.save_session(sid, {
        "game": None, 
        "agent": None, 
        "active": False,
        "prev_state": None,
        "prev_action": None
    })
    
    # Send confirmation to client
    await sio.emit("connected", {"message": "Connected to server!"}, to=sid)


@sio.event
async def disconnect(sid: str) -> None:
    """Handle client disconnections - cleanup any resources"""
    print(f"[DISCONNECT] Client disconnected: sid={sid}")
    
    try:
        session = await sio.get_session(sid)
        if session:
            # Mark session as inactive to stop game loop
            session["active"] = False
            await sio.save_session(sid, session)
    except Exception as e:
        print(f"[ERROR][disconnect] sid={sid} -> {e}")


@sio.event
async def start_game(sid: str, data: Dict[str, Any]) -> None:
    """Initialize a new game when the frontend requests it"""
    print(f"[START_GAME] sid={sid}, data={data}")
    
    try:
        session = await sio.get_session(sid)
        
        # Extract optional game parameters
        grid_width = data.get("grid_width")
        grid_height = data.get("grid_height")
        tick = data.get("game_tick")
        
        # Create new game instance
        game = Game()
        
        # Override defaults if provided
        if grid_width:
            game.grid_width = grid_width
        if grid_height:
            game.grid_height = grid_height
        if tick:
            game.game_tick = tick
        
        # Create DQN agent
        agent = DQN()
        
        # Update session
        session["game"] = game
        session["agent"] = agent
        session["active"] = True
        session["prev_state"] = None
        session["prev_action"] = None
        await sio.save_session(sid, session)
        
        # Send initial game state to client
        await sio.emit("game_started", game.to_dict(), to=sid)
        
        # Start the game update loop in background
        asyncio.create_task(update_game(sid))
        
    except Exception as e:
        print(f"[ERROR][start_game] sid={sid} -> {e}")
        await sio.emit("error", {"message": str(e)}, to=sid)


@sio.event
async def save_model(sid: str, data: Dict[str, Any]) -> None:
    """Save the current AI model to disk"""
    try:
        session = await sio.get_session(sid)
        agent = session.get("agent")
        
        if agent:
            agent.model.save()
            await sio.emit("model_saved", {"message": "Model saved successfully"}, to=sid)
        else:
            await sio.emit("error", {"message": "No active agent to save"}, to=sid)
            
    except Exception as e:
        print(f"[ERROR][save_model] sid={sid} -> {e}")
        await sio.emit("error", {"message": str(e)}, to=sid)


@sio.event
async def load_model(sid: str, data: Dict[str, Any]) -> None:
    """Load a previously saved AI model"""
    try:
        session = await sio.get_session(sid)
        agent = session.get("agent")
        file_name = data.get("file_name")
        
        if agent and file_name:
            agent.model.load(file_name)
            await sio.emit("model_loaded", {"message": f"Model {file_name} loaded successfully"}, to=sid)
        else:
            await sio.emit("error", {"message": "Agent or filename not provided"}, to=sid)
            
    except Exception as e:
        print(f"[ERROR][load_model] sid={sid} -> {e}")
        await sio.emit("error", {"message": str(e)}, to=sid)


async def update_game(sid: str) -> None:
    """Main game loop - runs continuously while the game is active"""
    print(f"[LOOP] Starting game loop for sid={sid}")
    
    try:
        while True:
            # Check if session still exists
            session = await sio.get_session(sid)
            if not session or not session.get("active"):
                print(f"[LOOP] Ending game loop for sid={sid} (inactive session)")
                break
            
            game: Game = session.get("game")
            agent: DQN = session.get("agent")
            
            if not game or not agent:
                print(f"[LOOP] No active game or agent for sid={sid}")
                break
            
            # Get current state
            current_state = agent.get_state(game)
            
            # Get action from agent
            action = agent.get_action(current_state)
            
            # Convert action to direction change
            # [1,0,0] = straight, [0,1,0] = right, [0,0,1] = left
            await apply_action(game, action)
            
            # Step the game forward
            game.step()
            
            # Get new state after action
            new_state = agent.get_state(game)
            
            # Calculate reward
            done = not game.running
            reward = agent.calculate_reward(game, done)
            
            # Train short memory (immediate learning)
            agent.train_short_memory(current_state, action, reward, new_state, done)
            
            # Remember this experience
            agent.remember(current_state, action, reward, new_state, done)
            
            # Send updated state to frontend
            game_state = game.to_dict()
            game_state["agent_stats"] = {
                "games": agent.n_games,
                "record": agent.record,
                "epsilon": agent.epsilon
            }
            await sio.emit("game_update", game_state, to=sid)
            
            # If game ended, train long memory and reset
            if done:
                # Update statistics
                agent.n_games += 1
                if game.score > agent.record:
                    agent.record = game.score
                
                # Train long memory (batch learning)
                agent.train_long_memory()
                
                # Send game over notification
                await sio.emit("game_over", {
                    "score": game.score,
                    "games": agent.n_games,
                    "record": agent.record
                }, to=sid)
                
                print(f"[GAME_OVER] sid={sid} - Game {agent.n_games} - Score: {game.score} - Record: {agent.record}")
                
                # Reset game for next round
                game.reset()
                agent.prev_distance = None
                agent.prev_length = 1
                
                # Small delay before next game
                await asyncio.sleep(0.5)
            
            # Wait for game tick
            await asyncio.sleep(game.game_tick)
            
    except Exception as e:
        print(f"[ERROR][update_game] sid={sid} -> {e}")
        await sio.emit("error", {"message": str(e)}, to=sid)


async def apply_action(game: Game, action: list) -> None:
    """
    Convert agent action to game direction change.
    
    Actions: [1,0,0] = straight, [0,1,0] = right, [0,0,1] = left
    """
    current_direction = game.snake.direction
    
    # action[0] = straight (no change)
    if action[1] == 1:  # Turn right
        if current_direction == (0, -1):  # UP -> RIGHT
            game.queue_change("RIGHT")
        elif current_direction == (1, 0):  # RIGHT -> DOWN
            game.queue_change("DOWN")
        elif current_direction == (0, 1):  # DOWN -> LEFT
            game.queue_change("LEFT")
        elif current_direction == (-1, 0):  # LEFT -> UP
            game.queue_change("UP")
    elif action[2] == 1:  # Turn left
        if current_direction == (0, -1):  # UP -> LEFT
            game.queue_change("LEFT")
        elif current_direction == (-1, 0):  # LEFT -> DOWN
            game.queue_change("DOWN")
        elif current_direction == (0, 1):  # DOWN -> RIGHT
            game.queue_change("RIGHT")
        elif current_direction == (1, 0):  # RIGHT -> UP
            game.queue_change("UP")
    # If action[0] == 1, continue straight (do nothing)


async def main() -> None:
    """Start the web server and socketio server"""
    # Add ping endpoint
    app.router.add_get("/ping", handle_ping)
    
    # Create and configure server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8765)
    
    print("[SERVER] Starting on http://localhost:8765")
    print("[SERVER] DQN Snake AI ready to train!")
    await site.start()
    
    # Keep server running
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())