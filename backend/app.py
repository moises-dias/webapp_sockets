from flask import Flask, request, current_app
from flask_socketio import SocketIO, emit
# from shadow import get_shadow_point_list
from shadow_v2 import get_shadows

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
    global movements
    global users
    with app.test_request_context('/'):
        while True:
            if movements:
                for sid, keys in movements.items():
                    usr = next((u for u in users if u['id'] == sid), None)
                    if usr is None:
                        continue
                    for key in keys:
                        usr['y'] -= 10 if key == 87 else 0 # w
                        usr['y'] += 10 if key == 83 else 0 # s
                        usr['x'] -= 10 if key == 65 else 0 # a
                        usr['x'] += 10 if key == 68 else 0 # d

                        usr['shadow'] = get_shadows((usr['x'], usr['y']))
                        socketio.emit('update_shadow', usr['shadow'], room=sid)
                # TODO check if the user moved before calling update shadow and sending a message to frontend
                # TODO check which users are visible and stop sending every user to everybody
                socketio.emit('update_users', users)
                print_red("emited")
                socketio.sleep(0.05)
            else:
                print("empty")
                socketio.sleep(0.05)


@socketio.on('connect')
def handle_connect():
    global users
    name = request.args.get('name')
    new_user = {'id': request.sid, 'user': name, 'x': 0, 'y': 0, 'shadow': [], 'angle': 0}
    users.append(new_user)
    emit('update_users', users, broadcast=True)
    print_green(f"A client with id {request.sid} connected with name {name}")
    new_user['shadow'] = get_shadows((new_user['x'], new_user['y']))
    emit('update_shadow', new_user['shadow'], room=request.sid)


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
            emit('update_users', users, broadcast=True)

@socketio.on('start_moving')
def handle_start_moving(data):
    global movements
    global thread

    if not request.sid in movements:
        movements[request.sid] = [data['direction']]
    elif data['direction'] not in movements[request.sid]:
        movements[request.sid].append(data['direction'])
        
    if not thread:
        _app = current_app._get_current_object()
        thread = socketio.start_background_task(target=background_thread, app=_app)
    print_green("START MOVE")
    print_green(movements)

@socketio.on('stop_movement')
def handle_stop_movement(data):
    global movements

    if request.sid in movements:
        if data['direction'] in movements[request.sid]:
            movements[request.sid].remove(data['direction'])
            if not movements[request.sid]:
                del movements[request.sid]

        
    print_red("FINISHED MOVE")
    print_red(movements)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)