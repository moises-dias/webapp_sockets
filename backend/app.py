from flask import Flask, request, current_app
from flask_socketio import SocketIO
from shadow_v2 import get_shadows

import math
import time

from entities import Entities

from collections import deque

from threading import Lock
changes_lock = Lock()

def print_green(text):
    print(f'\033[1;32m{text}\033[0m')

def print_red(text):
    print(f'\033[1;31m{text}\033[0m')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

all_entities = Entities()

thread = None
# TODO create another file just to store the walls for
# the shadow file and here (to use on the bullets too)
walls = [
    [[80, 80], [130, 290]],
    [[130, 80], [80, 290]],
    [[250, 150], [330, 180]],
    [[330, 150], [250, 180]]
]

def background_thread(app=None):
    execution_times = deque(maxlen=30)
    execution_times_with_code_logic = deque(maxlen=30)

    send_update = False

    global all_entities
    global walls
    with app.test_request_context('/'):
        while True:
            # TODO instead of waiting 30ms + time of the update variables,
            # update the variables and wait 30ms - time of the update and then send the
            # updates, this way the player always receive in 30ms the updates.
            socketio.sleep(0.03)
            send_update = False
            with changes_lock:
                start_time = time.time()
                # TODO send only changes to frontend, not always all the users
                # eg, send only who moved or who disconnected, and frontend update its user list
                for player in reversed(all_entities.players_backend):
                    if player['action']:
                        send_update = True
                    for action, values in list(player['action'].items()):
                        if action == 'movement':
                            for key in values:
                                player['info']['y'] -= 5 if key == 87 else 0 # w
                                player['info']['y'] += 5 if key == 83 else 0 # s
                                player['info']['x'] -= 5 if key == 65 else 0 # a
                                player['info']['x'] += 5 if key == 68 else 0 # d
                            player['info']['shadow'] = get_shadows((player['info']['x'], player['info']['y']))
                        elif action == 'disconnect':
                            all_entities.remove_entity('player', player) # if the iteration is not reversed this will break the code
                        else:
                            del player['action'][action]
                
                if all_entities.bullets_backend:
                    send_update = True
                for bullet in reversed(all_entities.bullets_backend):
                    bullet['info']['x'] += bullet['ite_x']
                    bullet['info']['y'] += bullet['ite_y']

                    if not (0 <= bullet['info']['x'] <= 400 and 0 <= bullet['info']['y'] <= 400):
                        all_entities.remove_entity('bullet', bullet) # if the iteration is not reversed this will break the code
                    else:
                        # TODO define when creating the bullet, the wall that it can collide, there is only one
                        # instead of comparing with all the walls
                        # try to intersect the line of the bullet and the lines of the walls, 
                        # compare only with the wall it can colide
                        # CAREFUL shot on edges (add 1 to extremities of walls? or check if the bullet intersect the extremity THIS IS IMPORTANT)
                        for wall in walls:
                            x1, y1 = wall[0]
                            x2, y2 = wall[1]

                            if x1 <= bullet['info']['x'] <= x2 and y1 <= bullet['info']['y'] <= y2:
                                all_entities.remove_entity('bullet', bullet) # if the iteration is not reversed this will break the code                

                for bullet in reversed(all_entities.bullets_backend):
                    for player in all_entities.players_backend:
                        # TODO instead of comparing with all the players
                        # check when creating the bullet which players cannot be hit
                        # (the ones on the back of the bullet and the player that shoot cannot be hit)
                        # use back of the bullet or trace a line of the bullet +-30 degrees and compare only to 
                        # players in the sight? 
                        if player['info']['alive'] == 'yes':
                            x1, y1 = player['info']["x"] - 15, player['info']["y"] - 15
                            x2, y2 = player['info']["x"] + 15, player['info']["y"] + 15

                            if x1 <= bullet['info']['x'] <= x2 and y1 <= bullet['info']['y'] <= y2:
                                print_red("HIT!!!!!!!!!!!!!")
                                player['info']['alive'] = 'no'
                                all_entities.remove_entity('bullet', bullet) # if the iteration is not reversed this will break the code 

                if send_update:
                    socket_start_time = time.time()
                    socketio.emit('update_entities', all_entities.frontend_entities)
                    socket_end_time = time.time()
                    execution_times.append(socket_end_time - socket_start_time)
                    formatted_time = "{:.1f} ms".format((sum(execution_times) / len(execution_times)) * 1000)
                    print_red(f"SEND MESSAGE TIME: {formatted_time}")

                
                end_time = time.time()
                execution_times_with_code_logic.append(end_time - start_time)
                formatted_time = "{:.1f} ms".format((end_time - start_time) * 1000)
                print_red(f"MESSAGE AND LOGIC: {formatted_time}")



@socketio.on('connect')
def handle_connect():
    global all_entities
    global thread

    name = request.args.get('name')
    
    info = {'name': name, 'x': 0, 'y': 0, 'shadow': [], 'angle': 0, 'alive': 'yes'}
    new_user = {'id': request.sid, 'action': {'connect': ''}, 'info': info}
    new_user['info']['shadow'] = get_shadows((new_user['info']['x'], new_user['info']['y']))
    with changes_lock:
        all_entities.add('player', new_user)
    print_green(f"A client with id {request.sid} connected with name {name}")
    if not thread:
        _app = current_app._get_current_object()
        thread = socketio.start_background_task(target=background_thread, app=_app)

@socketio.on('disconnect')
def handle_disconnect():
    global all_entities

    with changes_lock:
        player = next((p for p in all_entities.players_backend if p['id'] == request.sid), None)
        if player is not None:
            player['action']['disconnect'] = ''
    print_green(f"{request.sid} disconnected")

@socketio.on('respawn')
def handle_respawn(data):
    global all_entities

    with changes_lock:
        player = next((p for p in all_entities.players_backend if p['id'] == request.sid), None)
        if player is not None:
            player['info']['alive'] = 'yes'
            player['info']['x'] = 50
            player['info']['y'] = 50
            player['info']['shadow'] = get_shadows((player['info']['x'], player['info']['y']))
            player['action']['respawn'] = ''
    print_green(f"{request.sid} respawn -----------------")


@socketio.on('mouse_out')
def handle_mouse_out(data):
    global all_entities

    with changes_lock:
        player = next((p for p in all_entities.players_backend if p['id'] == request.sid), None)
        if player is not None:
            if 'movement' in player['action']:
                del player['action']['movement']
            # TODO when shooting be an action like movement (press and hold)
            # remove shooting here too
    print_green(f"{request.sid} stop movement XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx")


@socketio.on('update_angle')
def handle_update_angle(data):
    global all_entities

    with changes_lock:
        player = next((p for p in all_entities.players_backend if p['id'] == request.sid), None)
        if player is not None:
            player['action']['update_angle'] = ''
            player['info']['angle'] = data['angle']


@socketio.on('left_click')
def handle_left_click(data):
    global all_entities

    ite_x = math.cos(data['angle'])
    ite_y = math.sin(data['angle'])
    info = {'x': data['x'] + ite_x * 15, 'y': data['y'] + ite_y * 15, 'angle': data['angle']}
    new_bullet = {'ite_x': ite_x * 30, 'ite_y': ite_y * 30, "info": info}
    with changes_lock:
        all_entities.add('bullet', new_bullet)

@socketio.on('start_moving')
def handle_start_moving(data):
    global all_entities


    with changes_lock:
        player = next((p for p in all_entities.players_backend if p['id'] == request.sid), None)
        if player is not None:
            print("moving")
            if 'movement' not in player['action']:
                player['action']['movement'] = [data['direction']]
            elif data['direction'] not in player['action']['movement']:
                player['action']['movement'].append(data['direction'])
        
@socketio.on('stop_movement')
def handle_stop_movement(data):
    global all_entities

    with changes_lock:
        player = next((p for p in all_entities.players_backend if p['id'] == request.sid), None)
        if player is not None:
            if 'movement' in player['action']:
                if data['direction'] in player['action']['movement']:
                    player['action']['movement'].remove(data['direction'])
                if not player['action']['movement']:
                    del player['action']['movement']


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)