# test_client.py
import socketio
import time

# ✅ Create a Socket.IO client object
sio = socketio.Client()


# ✅ Handle connection
@sio.event
def connect():
    print("[CLIENT] Connected to server!")
    # Send event to start a new game
    sio.emit("start_game", {})


# ✅ Handle game updates from server
@sio.event
def game_update(data):
    print("[UPDATE] Game state:", data)


# ✅ Optional: handle "game_started" event if your backend emits it
@sio.event
def game_started(data):
    print("[STARTED] Initial game state:", data)
    
# Handle "game_over" event from backend
@sio.event
def game_over(data):
    print("[GAME_OVER] Game has terminated: ", data)
    # Start a new game again (after waiting a few seconds)
    time.sleep(3)
    sio.emit("start_game", {})
    print("[GAME_RESET] Game is Restarting...")


# ✅ Handle disconnection
@sio.event
def disconnect():
    print("[CLIENT] Disconnected from server.")


# ✅ Handle generic errors
@sio.event
def error(data):
    print("[ERROR]", data)


def main():
    # Connect to backend server
    print("[CLIENT] Connecting to server at http://localhost:8765 ...")
    sio.connect("http://localhost:8765")

    # Keep the client running to receive events
    sio.wait()


if __name__ == "__main__":
    main()