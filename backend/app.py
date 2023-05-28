from flask import Flask, request, current_app
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import flask_socketio
from shadow_v2 import get_shadows

from threading import Lock
changes_lock = Lock()

def print_green(text):
    print(f'\033[1;32m{text}\033[0m')

def print_red(text):
    print(f'\033[1;31m{text}\033[0m')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
socketio = SocketIO(app, cors_allowed_origins="*")

users = []
movements = {}
thread = None

def background_thread(app=None):
    # TODO remove user id from message to frontend
    # TODO remove other users shadow from message to frontend
    # TODO check if the user moved before calling update shadow and sending a message to frontend
    # TODO DO NOT SEND SHADOW NOW, SEND IT AFTER WITH THE USER NEW POSITION AND USERS IN SIGHT
    # TODO check which users are visible and stop sending every user to everybody
    global movements
    global users
    with app.test_request_context('/'):
        while True:
            socketio.sleep(0.03)
            with changes_lock:
                if movements:
                    for sid, keys in movements.items():
                        usr = next((u for u in users if u['id'] == sid), None)
                        if usr is None:
                            print_red("USER IS NONE")
                            continue
                        for key in keys:
                            usr['y'] -= 5 if key == 87 else 0 # w
                            usr['y'] += 5 if key == 83 else 0 # s
                            usr['x'] -= 5 if key == 65 else 0 # a
                            usr['x'] += 5 if key == 68 else 0 # d
                        
                        usr['shadow'] = get_shadows((usr['x'], usr['y']))

                    socketio.emit('update_users', users)
                    # join_room("test", sid, "/")
                    # leave_room("test", sid, "/")
                    # socketio.sleep(0.03)
                else:
                    print("empty")
                    # socketio.sleep(0.03)


@socketio.on('connect')
def handle_connect():
    global users
    global thread
    name = request.args.get('name')
    new_user = {'id': request.sid, 'name': name, 'x': 0, 'y': 0, 'shadow': [], 'angle': 0, 'type': 'user'}
    new_user['shadow'] = get_shadows((new_user['x'], new_user['y']))
    users.append(new_user)
    emit('update_users', users, broadcast=True)
    print_green(f"A client with id {request.sid} connected with name {name}")
    # emit('update_shadow', new_user['shadow'], room=request.sid)
    if not thread:
        _app = current_app._get_current_object()
        thread = socketio.start_background_task(target=background_thread, app=_app)

@socketio.on('disconnect')
def handle_disconnect():
    global users
    # TODO improve this logic
    users = [usr for usr in users if usr['id'] != request.sid]
    emit('update_users', users, broadcast=True)
    print_green(f"{request.sid} disconnected")


@socketio.on('update_angle')
def handle_update_angle(data):
    for usr in users:
        if usr['id'] == request.sid:
            usr['angle'] = data['angle']
            # TODO do not send message here, just update the angle on the movements dict and
            # let the thread send the message
            emit('update_users', users, broadcast=True)
    # emit('test_room', [], room="test")

@socketio.on('start_moving')
def handle_start_moving(data):
    global movements
    global thread

    with changes_lock:
        if not request.sid in movements:
            movements[request.sid] = [data['direction']]
        elif data['direction'] not in movements[request.sid]:
            movements[request.sid].append(data['direction'])
        
    # if not thread:
    #     _app = current_app._get_current_object()
    #     thread = socketio.start_background_task(target=background_thread, app=_app)

@socketio.on('stop_movement')
def handle_stop_movement(data):
    global movements

    with changes_lock:
        if request.sid in movements:
            if data['direction'] in movements[request.sid]:
                movements[request.sid].remove(data['direction'])
                if not movements[request.sid]:
                    del movements[request.sid]


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)