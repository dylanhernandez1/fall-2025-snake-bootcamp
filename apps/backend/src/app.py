import asyncio
import time
import socketio
from aiohttp import web
from agent import DQN
from game import Game
from typing import Any, Dict

sio: Any = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)


# for keeping server alive
async def handle_ping(request: web.Request) -> web.Response:
    return web.json_response({"message": "pong"})


@sio.event
async def connect(sid: str, environ: Dict[str, Any]) -> None:
    print(f"client connected: {sid}")


@sio.event
async def disconnect(sid: str) -> None:
    print(f"disconnected: {sid}")


@sio.event
async def start_game(sid: str, data: Dict[str, Any]) -> None:
    grid_width: int = data["grid_width"]
    grid_height: int = data["grid_height"]
    starting_tick: float = data["starting_tick"]
    game = Game()
    game.grid_width = grid_width
    game.grid_height = grid_height
    game.game_tick = starting_tick
    agent = DQN()
    await sio.save_session(sid, {"game": game, "agent": agent})
    state = game.to_dict()
    await sio.emit("update", state, room=sid)
    await update_game(sid)


# @sio.event
# async def save_model(sid):
#     session = await sio.get_session(sid)
#     agent = session['agent']
#     agent.model.save()


# @sio.event
# async def load_model(sid, data):
#     session = await sio.get_session(sid)
#     game = session['game']
#     agent = session['agent']
#     agent.model.load(data['file_name'])
#     await sio.save_session(sid, {'game': game, 'agent': agent})


@sio.event
async def change_delay(sid: str, delay: Dict[str, Any]) -> None:
    session = await sio.get_session(sid)
    game = session["game"]
    agent = session["agent"]
    game.game_tick = float(delay["delay"])
    await sio.save_session(sid, {"game": game, "agent": agent})
    global starting_game_tick
    starting_game_tick = float(delay["delay"])


async def update_game(sid: str) -> None:
    while True:
        if not await sio.get_session(sid):
            print(f"session {sid} not found")
            break

        session = await sio.get_session(sid)
        game = session["game"]
        agent = session["agent"]
        await update_agent_game_state(game, agent)

        await sio.save_session(sid, {"game": game, "agent": agent})
        await sio.emit("update", game.to_dict(), room=sid)

        elapsed = time.time() - game.last_tick
        wait_time = max(0, game.game_tick - elapsed)
        await asyncio.sleep(wait_time)


async def update_agent_game_state(game: Game, agent: DQN) -> None:
    state = agent.get_state(game)
    action = agent.get_action(state)

    current_direction = game.snake.direction
    if action[0] == 1:
        new_direction = current_direction
    elif action[1] == 1:
        if current_direction == (0, -1):
            new_direction = (-1, 0)
        elif current_direction == (-1, 0):
            new_direction = (0, 1)
        elif current_direction == (0, 1):
            new_direction = (1, 0)
        else:
            new_direction = (0, -1)
    else:
        if current_direction == (0, -1):
            new_direction = (1, 0)
        elif current_direction == (1, 0):
            new_direction = (0, 1)
        elif current_direction == (0, 1):
            new_direction = (-1, 0)
        else:
            new_direction = (0, -1)

    if new_direction == (0, -1):
        game.queue_change("UP")
    elif new_direction == (0, 1):
        game.queue_change("DOWN")
    elif new_direction == (-1, 0):
        game.queue_change("LEFT")
    else:
        game.queue_change("RIGHT")

    game.step()
    done = not game.running
    reward = agent.calculate_reward(game, done)
    next_state = agent.get_state(game)

    agent.train_short_memory(state, action, reward, next_state, done)
    agent.remember(state, action, reward, next_state, done)

    if done:
        agent.train_long_memory()
        agent.n_games += 1
        agent.avg_score = (
            (agent.avg_score * (agent.n_games - 1)) + game.score
        ) / agent.n_games
        print(
            f"game: {agent.n_games}, score: {game.score}, average score: {agent.avg_score:.2f}"
        )
        game.reset()


async def main() -> None:
    app.router.add_get("/ping", handle_ping)
    runner = web.AppRunner(app)
    try:
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8765)
        print("server running at http://0.0.0.0:8765")
        await site.start()
        await asyncio.Event().wait()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
