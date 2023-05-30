from flask import Flask, request, current_app
from flask_socketio import SocketIO

from threading import Lock
lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

thread = None

moving = False

def background_thread(app=None):
    global moving
    with app.test_request_context('/'):
        while True:
            socketio.sleep(1)
            with lock:
                if moving:
                    print("------------- MOVING -------------")
                    socketio.emit('update_entities', [])
            print("-------------------- DEFAULT ------")
                

@socketio.on('connect')
def handle_connect():
    global moving
    global thread
    if not thread:
        _app = current_app._get_current_object()
        thread = socketio.start_background_task(target=background_thread, app=_app)

@socketio.on('start_moving')
def handle_start_moving(data):
    global moving
    with lock:
        moving = True
        
@socketio.on('stop_movement')
def handle_stop_movement(data):
    global moving
    with lock:
        moving = False


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)


