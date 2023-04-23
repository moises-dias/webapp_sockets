from flask import Flask, request
from flask_socketio import SocketIO, emit

def print_green(text):
    print(f'\033[1;32m{text}\033[0m')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users = []

@socketio.on('connect')
def handle_connect():
    global users
    name = request.args.get('name')
    new_user = {'id': request.sid, 'user': name, 'x': 0, 'y': 0}
    users.append(new_user)
    emit('update_users', users, broadcast=True)
    print_green(f"A client with id {request.sid} connected with name {name}")


@socketio.on('disconnect')
def handle_disconnect():
    global users
    # TODO improve this logic
    users = [usr for usr in users if usr['id'] != request.sid]
    emit('update_users', users, broadcast=True)
    print_green(f"{request.sid} disconnected")

@socketio.on('move')
def handle_move(data):
    # TODO frontend should just pass "moving up" once
    # and backend should notify everybody, this way there
    # is no need to a socket message for every 10 pixels
    # the user will move until backend get movement stop
    # but how to get colision using this logic?
    # TODO hide user id from frontend
    print_green(data['direction'])
    print_green(request.sid)
    # TODO improve this logic
    for usr in users:
        if usr['id'] == request.sid:
            if data['direction'] == 87: # w
                usr['y'] -= 10
            elif data['direction'] == 83: # s
                usr['y'] += 10
            elif data['direction'] == 65: # a
                usr['x'] -= 10
            elif data['direction'] == 68: # d
                usr['x'] += 10
            
            emit('update_users', users, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)