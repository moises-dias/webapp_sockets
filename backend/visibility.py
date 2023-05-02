from shadow_v2 import is_point_in_triangle

def set_visibility(user, moving_user):
    # if is visible: update
    # if its not visible and it was not visible: pass
    # if its not visible and it was visible: remove
    pass

def is_usr_visible(stopped_user, usr):
    usr_position = [usr['x'], usr['y']]
    for shadow in stopped_user['shadow']:
        triangle_1 = shadow[:-1]
        triangle_2 = [shadow[0], shadow[2], shadow[3]]
        if is_point_in_triangle(usr_position, triangle_1) or is_point_in_triangle(usr_position, triangle_2):
            return False
    return True