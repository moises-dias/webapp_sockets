from flask import Flask, request
from flask_socketio import SocketIO, emit
import math

def get_screen_limit_targets(canvas, angle_in_degrees):
    if 0 <= angle_in_degrees < 90:
        limit_x = canvas[0]
        limit_y = canvas[1]
    elif 90 <= angle_in_degrees < 180:
        limit_x = 0
        limit_y = canvas[1]
    elif 180 <= angle_in_degrees < 270:
        limit_x = 0
        limit_y = 0
    elif 270 <= angle_in_degrees < 360:
        limit_x = canvas[0]
        limit_y = 0
    
    return limit_x, limit_y

def get_y_from_x(x, angle, point):
    # Calculate the y-coordinate where the line intersects with target x
    delta_x = x - point[0]
    delta_y = delta_x * math.tan(angle)
    y = round(point[1] + delta_y)
    return y

def get_x_from_y(y, angle, point):
    # Calculate the x-coordinate where the line intersects with target y
    delta_y = y - point[1]
    try:
        delta_x = delta_y / math.tan(angle)
        x = round(point[0] + delta_x)
    except Exception as e:
        x = 1000
    return x

def get_canvas_edges_angles(point, canvas):
    edges = [
        {"coord": (0, 0)},
        {"coord": (canvas[0], 0)},
        {"coord": (0, canvas[1])},
        {"coord": (canvas[0], canvas[1])}
    ]
    for edge in edges:
        dx = edge["coord"][0] - point[0]
        dy = edge["coord"][1] - point[1]
        angle = math.atan2(dy, dx)
        angle_in_degrees = math.degrees(angle)
        angle_in_degrees = (angle_in_degrees + 360.0) % 360.0
        edge["angle"] = angle_in_degrees
    return edges

def get_shadows(user):

    canvas = (400, 400)

    wall1 = (100, 200)
    wall2 = (200, 300)
    
    wall = [wall1, wall2]
    wall_info = []

    for w in wall:
        dx = w[0] - user[0]
        dy = w[1] - user[1]
        angle = math.atan2(dy, dx)
        angle_in_degrees = math.degrees(angle)
        angle_in_degrees = (angle_in_degrees + 360.0) % 360.0

        limit_x, limit_y = get_screen_limit_targets(canvas, angle_in_degrees)

        y = get_y_from_x(limit_x, angle, user)
        x = get_x_from_y(limit_y, angle, user)

        if 0 <= y <= canvas[1]:
            wall_limit = (limit_x, y)
        else:
            wall_limit = (x, limit_y)

        wall_info.append(
            {
                "coord": w,
                "limit": wall_limit,
                "angle": angle_in_degrees
            } 
        )

    canvas_angles = get_canvas_edges_angles(user, canvas)

    # se diferença maior de 180 printa algo arruma dpois
    upper_angle_limit = max([w['angle'] for w in wall_info])
    lower_angle_limit = min([w['angle'] for w in wall_info])

    edges_to_add_on_shadow = []
    if upper_angle_limit - lower_angle_limit < 180:
        for canvas_info in canvas_angles:
            if lower_angle_limit < canvas_info["angle"] < upper_angle_limit:
                edges_to_add_on_shadow.append(canvas_info)
    else:
        for canvas_info in canvas_angles:
            if canvas_info["angle"] < lower_angle_limit or canvas_info["angle"] > upper_angle_limit:
                edges_to_add_on_shadow.append(canvas_info)
    
    shadow_points = []

    first_wall_point = min(wall_info, key=lambda x: x['angle'])
    last_wall_point = max(wall_info, key=lambda x: x['angle'])

    shadow_points.append(first_wall_point['coord'])
    shadow_points.append(first_wall_point['limit'])

    sorted_edges = sorted(edges_to_add_on_shadow, key=lambda x: x['angle'])

    for edge in sorted_edges:
        shadow_points.append(edge['coord'])
    
    shadow_points.append(last_wall_point['limit'])
    shadow_points.append(last_wall_point['coord'])

    return shadow_points



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
    new_user = {'id': request.sid, 'user': name, 'x': 0, 'y': 0, 'shadow': []}
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

@socketio.on('move')
def handle_move(data):
    # TODO frontend should just pass "moving up" once
    # and backend should notify everybody, this way there
    # is no need to a socket message for every 10 pixels
    # the user will move until backend get movement stop
    # but how to get colision using this logic?
    # TODO hide user id from frontend
    # TODO hide user shadow from frontend
    print_green(data['direction'])
    print_green(request.sid)
    # TODO improve this logic
    for usr in users:
        if usr['id'] == request.sid:
            if data['direction'] == 87: # w
                usr['y'] -= 1
            elif data['direction'] == 83: # s
                usr['y'] += 1
            elif data['direction'] == 65: # a
                usr['x'] -= 1
            elif data['direction'] == 68: # d
                usr['x'] += 1
            usr['shadow'] = get_shadows((usr['x'], usr['y']))
            print_green(usr['shadow'])
            
            emit('update_users', users, broadcast=True)
            emit('update_shadow', usr['shadow'], room=request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)