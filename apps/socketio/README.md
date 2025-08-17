# Snake Game SocketIO Backend

This is the Python backend for the Snake game, using SocketIO for real-time communication.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the backend server:

   ```bash
   python src/app.py
   ```

## Files

- Main entrypoint: `src/app.py`
- Game logic: `src/game.py`, `src/snake.py`, `src/food.py`, `src/agent.py`, `src/model.py`
- Model weights: `model/model-*.pth`

## Notes

- Make sure the model file exists in `model/` if required by the backend.
- The backend should be running before starting the Next.js frontend for full functionality.
