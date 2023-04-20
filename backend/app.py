from flask_cors import CORS
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('mousemove')
def handle_mouse_move(data):
    print(data)  # Do something with the mouse position data received from the frontend

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")