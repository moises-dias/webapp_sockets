from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users = []
points = []

@app.route('/')
def index():
    global users
    users.append(request.sid)

@socketio.on('click')
def handle_click(data):
    global points
    points.append((request.sid, data['x'], data['y']))
    emit('new_point', {'user': request.sid, 'x': data['x'], 'y': data['y']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)