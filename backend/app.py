from flask import Flask, request, current_app
from flask_socketio import SocketIO
from shadow_v2 import get_shadows

import math

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
walls = [
    [[80, 80], [130, 290]],
    [[130, 80], [80, 290]],
    [[250, 150], [330, 180]],
    [[330, 150], [250, 180]]
]

def background_thread(app=None):
    global changes
    global entities
    global walls
    changes_to_remove = []
    bullets_to_remove = []
    bullets_to_update = False
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
                    elif change['type'] in ['update_angle', 'connect', 'disconnect', 'left_click']:
                        changes_to_remove.append(change)
                        print_red(change['type'])

                for entity in entities:
                    if entity['type'] == 'bullet':
                        bullets_to_update = True
                        entity['x'] += entity['ite_x']
                        entity['y'] += entity['ite_y']
                        # TODO check if bullet hit players
                        # if bullet hit player the player must stay 5 second stopped and respawn at a random position
                        # backend send the name of who killed the player
                        if not (0 <= entity['x'] <= 400 and 0 <= entity['y'] <= 400):
                            bullets_to_remove.append(entity)
                        else:
                            for wall in walls:
                                x1, y1 = wall[0]
                                x2, y2 = wall[1]

                                if x1 <= entity['x'] <= x2 and y1 <= entity['y'] <= y2:
                                    bullets_to_remove.append(entity)


                if bullets_to_remove:
                    for bullet in bullets_to_remove:
                        entities.remove(bullet)
                    bullets_to_remove = []

                if changes or bullets_to_update:
                    socketio.emit('update_entities', entities)
                    bullets_to_update = False

                if changes_to_remove:
                    for change in changes_to_remove:
                        changes.remove(change)
                        print_green(f"REMOVED {change['type']}")
                    changes_to_remove = []



@socketio.on('connect')
def handle_connect():
    global entities
    global changes
    global thread

    name = request.args.get('name')
    new_user = {'id': request.sid, 'name': name, 'x': 0, 'y': 0, 'shadow': [], 'angle': 0, 'type': 'player'}
    new_user['shadow'] = get_shadows((new_user['x'], new_user['y']))
    with changes_lock:
        entities.append(new_user)
        changes.append({'type': 'connect'})
    print_green(f"A client with id {request.sid} connected with name {name}")
    if not thread:
        _app = current_app._get_current_object()
        thread = socketio.start_background_task(target=background_thread, app=_app)

@socketio.on('disconnect')
def handle_disconnect():
    global entities
    global changes

    # TODO improve this logic
    with changes_lock:
        entities = [usr for usr in entities if usr['id'] != request.sid]
        changes.append({'type': 'disconnect'})
    print_green(f"{request.sid} disconnected")


@socketio.on('update_angle')
def handle_update_angle(data):
    global entities
    global changes

    with changes_lock:
        for usr in entities:
            if usr['id'] == request.sid:
                usr['angle'] = data['angle']
                changes.append({'type': 'update_angle'})


@socketio.on('left_click')
def handle_left_click(data):
    global entities
    global changes
    print("NEW BULLET")
    print(data['x'])
    print(data['angle'])
    ite_x = math.cos(data['angle'])
    ite_y = math.sin(data['angle'])
    new_bullet = {'id': "test", 'x': data['x'], 'y': data['y'], 'angle': data['angle'], 'ite_x': ite_x * 15, 'ite_y': ite_y * 15, 'type': 'bullet'}
    with changes_lock:
        entities.append(new_bullet)
        changes.append({'type': 'left_click'})

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
    global changes

    with changes_lock:
        user_movements = next((d for d in changes if d['type'] == 'movement' and d['id'] == request.sid), None)
        if user_movements:
            if data['direction'] in user_movements['values']:
                user_movements['values'].remove(data['direction'])
                if not user_movements['values']:
                    changes.remove(user_movements)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)