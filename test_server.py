# Need to show available players in board state

from engine import Board, Player
from engine.constants import *
from flask import Flask, jsonify, abort, request
import logging
import sys

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))

app = Flask(__name__)
app.debug = True
app.logger.addHandler(handler)

engine_logger = logging.getLogger('engine')
engine_logger.setLevel(logging.INFO)
engine_logger.addHandler(handler)

GAMES = {}
board = None

suspect_map = {
    'scarlet': SCARLET,
    'mustard': MUSTARD,
    'white': WHITE,
    'green': GREEN,
    'peacock': PEACOCK,
    'plum': PLUM,
}

players = []


@app.route('/current_player')
def current_player():
    global board

    return board.current_player.name


@app.route('/players', methods=['GET', 'POST'])
def players():
    global board

    if not board:
        return 'Board not initialized'

    if request.method == 'POST':
        player_name = request.form.get('name')
        suspect = request.form.get('suspect')

        try:
            board.add_player(Player(name=player_name, suspect=suspect_map[suspect]))
        except Exception as e:
            return str(e)

    return 'Added player {} as {}'.format(player_name, suspect_map[suspect].name)


@app.route('/')
def index():
    global board

    if not board:
        board = Board()

    return jsonify({
            'id': board.id,
            'time_started': board.time_started
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
