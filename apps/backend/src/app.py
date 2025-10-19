import asyncio
import time
import socketio
from aiohttp import web
from typing import Any, Dict


# from model import DQN
from game import Game;


sio = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)


# TODO: Create a SocketIO server instance with CORS settings to allow connections from frontend
sio = socketio.AsyncServer(cors_allowed_origins="*")

# TODO: Create a web application instance
app = web.Application()

# TODO: Attach the socketio server to the web app
sio.attach(app)


# Basic health check endpoint - keep this for server monitoring
async def handle_ping(request: Any) -> Any:
    """Simple ping endpoint to keep server alive and check if it's running"""
    return web.json_response({"message": "pong"})


# TODO: Create a socketio event handler for when clients connect
@sio.event
async def connect(sid: str, environ: Dict[str, Any]) -> None:
    """Handle client connections - called when a frontend connects to the server"""
    # TODO: Print a message showing which client connected
    # TODO: You might want to initialize game state here
    print(f"[CONNECT] Client connected: sid={sid}")
    await sio.save_session(sid, {"game": None, "agent": None, "active": False})
    await sio.emit("connected", {"message": "Connected to server!"}, to=sid)


# TODO: Create a socketio event handler for when clients disconnect
@sio.event
async def disconnect(sid: str) -> None:
    """Handle client disconnections - cleanup any resources"""
    # TODO: Print a message showing which client disconnected
    # TODO: Clean up any game sessions or resources for this client
    print(f"[DISCONNECT] Client disconnected: sid={sid}")
    try:
        session = await sio.get_session(sid)
        if session:
            session["active"] = False
            await sio.save_session(sid, session)
    except Exception as e:
        print(f"[ERROR][disconnect] sid={sid} -> {e}")


# TODO: Create a socketio event handler for starting a new game
@sio.event
async def start_game(sid: str, data: Dict[str, Any]) -> None:
    """Initialize a new game when the frontend requests it"""
    # TODO: Extract game parameters from data (grid_width, grid_height, starting_tick)
    # TODO: Create a new Game instance and configure it
    # TODO: If implementing AI, create an agent instance here
    # TODO: Save the game state in the session using sio.save_session()
    # TODO: Send initial game state to the client using sio.emit()
    # TODO: Start the game update loop
    print(f"[START_GAME] sid={sid}, data={data}")
    session = await sio.get_session(sid)

    try:
        # You can optionally allow frontend to override grid sizes/tick
        grid_width = data.get("grid_width")
        grid_height = data.get("grid_height")
        tick = data.get("game_tick")

        game = Game()

        if grid_width:
            game.grid_width = grid_width
        if grid_height:
            game.grid_height = grid_height
        if tick:
            game.game_tick = tick

        session["game"] = game
        session["active"] = True
        await sio.save_session(sid, session)

        # Send initial state
        await sio.emit("game_started", game.to_dict(), to=sid)

        # Run update loop in background
        asyncio.create_task(update_game(sid))

    except Exception as e:
        print(f"[ERROR][start_game] sid={sid} -> {e}")
        await sio.emit("error", {"message": str(e)}, to=sid)


# TODO: Optional - Create event handlers for saving/loading AI models


# TODO: Implement the main game loop
async def update_game(sid: str) -> None:
    """Main game loop - runs continuously while the game is active"""
    # TODO: Create an infinite loop
    # TODO: Check if the session still exists (client hasn't disconnected)
    # TODO: Get the current game and agent state from the session
    # TODO: Implement AI agentic decisions
    # TODO: Update the game state (move snake, check collisions, etc.)
    # TODO: Save the updated session
    # TODO: Send the updated game state to the client
    # TODO: Wait for the appropriate game tick interval before next update
    print(f"[LOOP] Starting game loop for sid={sid}")

    try:
        while True:
            session = await sio.get_session(sid)
            if not session or not session.get("active"):
                print(f"[LOOP] Ending game loop for sid={sid} (inactive session)")
                break

            game: Game = session.get("game")
            if not game:
                print(f"[LOOP] No active game for sid={sid}")
                break

            # Step the game forward
            game.step()

            # Send updated state to frontend
            await sio.emit("game_update", game.to_dict(), to=sid)

            # If the game ended, notify and stop
            if not game.running:
                await sio.emit("game_over", {"score": game.score}, to=sid)
                print(f"[GAME_OVER] sid={sid} - Final Score: {game.score}")
                session["active"] = False
                await sio.save_session(sid, session)
                break

            await asyncio.sleep(game.game_tick)

    except Exception as e:
        print(f"[ERROR][update_game] sid={sid} -> {e}")
        await sio.emit("error", {"message": str(e)}, to=sid)


# TODO: Helper function for AI agent interaction with game
async def update_agent_game_state(game: Game, agent: Any) -> None:
    """Handle AI agent decision making and training"""
    # TODO: Get the current game state for the agent
    # TODO: Have the agent choose an action (forward, turn left, turn right)
    # TODO: Convert the agent's action to a game direction
    # TODO: Apply the direction change to the game
    # TODO: Step the game forward one frame
    # TODO: Calculate the reward for this action
    # TODO: Get the new game state after the action
    # TODO: Train the agent on this experience (short-term memory)
    # TODO: Store this experience in the agent's memory
    # TODO: If the game ended:
    #   - Train the agent's long-term memory
    #   - Update statistics (games played, average score)
    #   - Reset the game for the next round
    pass


# TODO: Main server startup function
async def main() -> None:
    """Start the web server and socketio server"""
    # TODO: Add the ping endpoint to the web app router
    # TODO: Create and configure the web server runner
    # TODO: Start the server on the appropriate host and port
    # TODO: Print server startup message
    # TODO: Keep the server running indefinitely
    # TODO: Handle any errors gracefully
    app.router.add_get("/ping", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8765)
    print("[SERVER] Starting on http://localhost:8765")
    await site.start()

    while True:
        await asyncio.sleep(3600)  # keep alive
    


if __name__ == "__main__":
    asyncio.run(main())
