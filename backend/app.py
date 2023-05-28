from flask import Flask, request, current_app
from flask_socketio import SocketIO, emit
from shadow_v2 import get_shadows

from threading import Lock
changes_lock = Lock()

def print_green(text):
    print(f'\033[1;32m{text}\033[0m')

def print_red(text):
    print(f'\033[1;31m{text}\033[0m')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

entities = []
changes = []
thread = None

def background_thread(app=None):
    global changes
    global entities
    with app.test_request_context('/'):
        while True:
            socketio.sleep(0.03)
            with changes_lock:
                for change in changes:
                    if change['type'] == 'movement':
                        usr = next((u for u in entities if u['id'] == change['id']), None)
                        if usr is None:
                            print_red("USER IS NONE")
                            continue
                        for key in change['values']:
                            usr['y'] -= 5 if key == 87 else 0 # w
                            usr['y'] += 5 if key == 83 else 0 # s
                            usr['x'] -= 5 if key == 65 else 0 # a
                            usr['x'] += 5 if key == 68 else 0 # d
                        
                        usr['shadow'] = get_shadows((usr['x'], usr['y']))

                if changes:
                    socketio.emit('update_entities', entities)
                else:
                    print("empty")


@socketio.on('connect')
def handle_connect():
    global entities
    global thread
    name = request.args.get('name')
    new_user = {'id': request.sid, 'name': name, 'x': 0, 'y': 0, 'shadow': [], 'angle': 0, 'type': 'user'}
    new_user['shadow'] = get_shadows((new_user['x'], new_user['y']))
    # TODO changes.add new user or something like that
    entities.append(new_user)
    emit('update_entities', entities, broadcast=True)
    print_green(f"A client with id {request.sid} connected with name {name}")
    if not thread:
        _app = current_app._get_current_object()
        thread = socketio.start_background_task(target=background_thread, app=_app)

@socketio.on('disconnect')
def handle_disconnect():
    global entities
    # TODO improve this logic
    entities = [usr for usr in entities if usr['id'] != request.sid]
    emit('update_entities', entities, broadcast=True)
    print_green(f"{request.sid} disconnected")


@socketio.on('update_angle')
def handle_update_angle(data):
    for usr in entities:
        if usr['id'] == request.sid:
            usr['angle'] = data['angle']
            # TODO do not send message here, just update the angle on the movements dict and
            # let the thread send the message
            emit('update_entities', entities, broadcast=True)

@socketio.on('start_moving')
def handle_start_moving(data):
    global changes

    with changes_lock:
        user_movements = next((d for d in changes if d['type'] == 'movement' and d['id'] == request.sid), None)
        if user_movements:
            if not data['direction'] in user_movements['values']:
                user_movements['values'].append(data['direction'])
        else:
            user_movements = {'id': request.sid, 'type': 'movement', 'values': [data['direction']]}
            changes.append(user_movements)
        
@socketio.on('stop_movement')
def handle_stop_movement(data):
    global movements

    with changes_lock:
        user_movements = next((d for d in changes if d['type'] == 'movement' and d['id'] == request.sid), None)
        if user_movements:
            if data['direction'] in user_movements['values']:
                user_movements['values'].remove(data['direction'])
                if not user_movements['values']:
                    changes.remove(user_movements)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)