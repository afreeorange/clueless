# Need to show available players in board state

from engine import Board, Player
from engine.constants import *
from flask import Flask, jsonify, abort, request, render_template
from flask_socketio import SocketIO, emit, send
import logging
import sys

app = Flask(__name__, template_folder='./', static_folder='./__misc')
app.debug = True
socketio = SocketIO(app)

# Logging: Add a handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))

# Start logging stuff from the game engine using this handler
engine_logger = logging.getLogger('engine')
engine_logger.setLevel(logging.INFO)
engine_logger.addHandler(handler)

# Start logging stuff from the server using the same handler
app.logger.addHandler(handler)

# Create a new game board with each startup
board = Board()

client_to_player_map = {}

suspect_map = {
    'scarlet': SCARLET,
    'mustard': MUSTARD,
    'white': WHITE,
    'green': GREEN,
    'peacock': PEACOCK,
    'plum': PLUM,
}

space_map = {
    'study': STUDY,
    'hall': HALL,
    'lounge': LOUNGE,
    'library': LIBRARY,
    'billiard_room': BILLIARD_ROOM,
    'dining_room': DINING_ROOM,
    'conservatory': CONSERVATORY,
    'ballroom': BALLROOM,
    'kitchen': KITCHEN,
    'study_to_hall': STUDY_TO_HALL,
    'hall_to_lounge': HALL_TO_LOUNGE,
    'study_to_library': STUDY_TO_LIBRARY,
    'hall_to_billiard': HALL_TO_BILLIARD,
    'lounge_to_dining': LOUNGE_TO_DINING,
    'library_to_billiard': LIBRARY_TO_BILLIARD,
    'billiard_to_dining': BILLIARD_TO_DINING,
    'library_to_conservatory': LIBRARY_TO_CONSERVATORY,
    'billiard_to_ballroom': BILLIARD_TO_BALLROOM,
    'dining_to_kitchen': DINING_TO_KITCHEN,
    'conservatory_to_ballroom': CONSERVATORY_TO_BALLROOM,
    'ballroom_to_kitchen': BALLROOM_TO_KITCHEN,
}


@socketio.on('connect')
def test_connect():
    emit('clueless server response', {'data': 'Connected (ID {})'.format(request.sid)})


@socketio.on('move player')
def move_player(message):
    print(message)
    try:
        board.move_player(space=space_map[message['space']])
    except Exception as e:
        emit('clueless server response', {'data': str(e)})
    else:
        client_to_player_map[request.sid] = p
        emit('clueless server response', {
                'data': 'Moved {} ({}) to {}'.format(
                    board.current_player.name,
                    board.current_suspect.name,
                    request.sid
                    )
                }, broadcast=True)


@socketio.on('board log')
def board_log(message):
    emit('Logger said: {}'.format(message.log))


@socketio.on('touch player')
def touch_player(message):
    print(message['id'])
    emit('clueless server response', {
            'data': 'Hello, {}'.format(message['id'])
            }, room=message['id'])


@socketio.on('add player')
def player_name(message):

    print(suspect_map[message['suspect']].name)

    p = Player(name=message['name'], suspect=suspect_map[message['suspect']])

    try:
        board.add_player(p)
    except Exception as e:
        emit('clueless server response', {'data': str(e)})
    else:
        client_to_player_map[request.sid] = p
        print(client_to_player_map)
        emit('clueless server response', {
                'data': 'Added {} as {} (ID {})'.format(
                    p.name,
                    p.suspect.name,
                    request.sid
                    )
                }, broadcast=True)


# @app.route('/suspect_map')
# def suspect_map():
#     print(board.current_player)
#     return jsonify({})


@app.route('/')
def index():
    return render_template('socket_client.html')


if __name__ == '__main__':
    socketio.run(app)
