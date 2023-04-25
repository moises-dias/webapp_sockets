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
        print(e)
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

    wall1 = (20, 360)
    wall2 = (30, 380)
    
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

        print(f"user={user}, dest={w}")
        print(f"Angulo: {angle_in_degrees}")
        print(f"intercepta x={limit_x} em y={y}")

        x = get_x_from_y(limit_y, angle, user)
        
        print(f"intercepta y={limit_y} em x={x}")
        print()
        if 0 <= y <= canvas[1]:
            wall_limit = (limit_x, y)
            print(f"will be used the {limit_x},{y}")
        else:
            wall_limit = (x, limit_y)
            print(f"will be used the {x},{limit_y}")
        print()

        wall_info.append(
            {
                "coord": w,
                "limit": wall_limit,
                "angle": angle_in_degrees
            } 
        )

    print(wall_info)
    canvas_angles = get_canvas_edges_angles(user, canvas)
    print(canvas_angles)

    # se diferença maior de 180 printa algo arruma dpois
    upper_angle_limit = max([w['angle'] for w in wall_info])
    lower_angle_limit = min([w['angle'] for w in wall_info])

    if upper_angle_limit - lower_angle_limit >= 180:
        print("-------------------TRATAR ESSE CASO------------------")
    
    edges_to_add_on_shadow = []
    for canvas_info in canvas_angles:
        if lower_angle_limit < canvas_info["angle"] < upper_angle_limit:
            edges_to_add_on_shadow.append(canvas_info)
    
    print(edges_to_add_on_shadow)

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

    print("---------------")
    print(shadow_points)



user = (200, 200)
get_shadows(user)