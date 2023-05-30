import math

def is_point_in_triangle(point, triangle):

    for edge in triangle:
        if edge == point:
            return True

    x, y = point
    x1, y1 = triangle[0]
    x2, y2 = triangle[1]
    x3, y3 = triangle[2]
    denominator = (y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)

    if denominator == 0:
        return False

    alpha = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / denominator
    beta = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / denominator
    gamma = 1 - alpha - beta

    if alpha >= 0 and beta >= 0 and gamma >= 0:
        return True
    else:
        return False

def remove_hidden_walls(shadows, walls):
    walls_to_remove = []
    for shadow in shadows:
        for wall in walls:
            first_triangle = shadow[:-1]
            second_triangle = [shadow[0], shadow[2], shadow[3]]
            
            first_wall_point_in_first_triangle = is_point_in_triangle(wall[0], first_triangle)
            first_wall_point_in_second_triangle = is_point_in_triangle(wall[0], second_triangle)
            second_wall_point_in_first_triangle = is_point_in_triangle(wall[1], first_triangle)
            second_wall_point_in_second_triangle = is_point_in_triangle(wall[1], second_triangle)

            if first_wall_point_in_first_triangle or first_wall_point_in_second_triangle:
                if second_wall_point_in_first_triangle or second_wall_point_in_second_triangle:
                    walls_to_remove.append(wall)

    walls = [wall for wall in walls if wall not in walls_to_remove]
    return walls

def add_distance_to_user(user, walls):
    for wall in walls:
        wall_middle_x = (wall[0][0] + wall[1][0]) / 2
        wall_middle_y = (wall[0][1] + wall[1][1]) / 2
        distance = math.sqrt((wall_middle_x - user[0])**2 + (wall_middle_y - user[1])**2)
        wall.append(distance)

def find_point_from_line(a, b, distance):

    ab_vector = [b[0] - a[0], b[1] - a[1]]

    ab_length = math.sqrt(ab_vector[0] ** 2 + ab_vector[1] ** 2)
    if ab_length == 0:
        return [0, 0]

    ab_vector_normalized = [ab_vector[0] / ab_length, ab_vector[1] / ab_length] 

    c = [round(b[0] + ab_vector_normalized[0] * distance), round(b[1] + ab_vector_normalized[1] * distance)]

    return c

def get_shadow_polygon(user, wall):

    distance = 2000
    shadow_polygon = []

    shadow_polygon.append(wall[0])
    shadow_polygon.append(find_point_from_line(user, wall[0], distance))
    shadow_polygon.append(find_point_from_line(user, wall[1], distance))
    shadow_polygon.append(wall[1])

    return shadow_polygon

def get_shadows(user):
    # TODO create condition to check if there
    # is a need for the 2 walls on the X, or 
    # only one is necessary (check if the user is)
    # on the back of the edges
    #  x  
    #      _____
    #     |    /|
    #     |  /  |
    #     |/____|
    # in this case only the diagonal being show is 
    # necessary

    walls = [
        [[80, 80], [130, 290]],
        [[130, 80], [80, 290]],
        [[250, 150], [330, 180]],
        [[330, 150], [250, 180]]
    ]

    add_distance_to_user(user, walls)
    walls.sort(key=lambda x: x[2])

    shadows = []

    while walls:
        wall = walls.pop(0)
        shadows.append(get_shadow_polygon(user, wall))
        walls = remove_hidden_walls(shadows, walls)
    
    print(f"casted {len(shadows)} walls")
    return shadows
