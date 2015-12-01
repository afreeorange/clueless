# # i can't hear that lullaby of the midnight train

# Cilent adds player
# server
#     responds with uuid
#     maps client sid to UUID
# client sets it in localstorage
# client must pass it with each REST request
# server can address client by SID <> UUID map

# Client disconnection
#     if Client has UUID in localstorage, pass it upon connect via some special channel ('reconnect channel')
#     get all the messages (REST)
#     server updates SID <> UUID map

# Need a boardservice
# Need a board state

import logging
import sys
import importlib
from uuid import uuid4

import arrow
import engine
from engine import Board, Player
from engine.exceptions import *
from engine.models import Room, Hallway, Weapon, Suspect
from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_restful import Api, Resource
# from flask_socketio import SocketIO, emit, send


class InvalidPlayerToken(Exception):
    pass


class InvalidSpaceStub(Exception):
    pass


class InvalidWeaponStub(Exception):
    pass


class InvalidSuspectStub(Exception):
    pass


class SocketIOLoggingHandler(logging.Handler):

    def __init__(self, socket_io_object, channel):
        super(SocketIOLoggingHandler, self).__init__()
        self.socket_io_object = socket_io_object
        self.channel = channel

    def emit(self, record):
        self.socket_io_object.emit(self.channel, {
                'data': {
                    'timestamp': str(arrow.now()),
                    'level': record.levelname,
                    'message': record.msg,
                }
            })


class JSONHandler(logging.Handler):

    def __init__(self, json_object=[]):
        super(JSONHandler, self).__init__()
        self.json_object = json_object

    def emit(self, record):
        self.json_object.append({
                'timestamp': str(arrow.now()),
                'level': record.levelname,
                'message': record.msg,
            })


class BoardService:

    def __init__(self, board, test_mode=False):
        self.__board = board

        self.STUB_TO_SUSPECT_MAP = {
            'scarlet': self.__board.SCARLET,
            'mustard': self.__board.MUSTARD,
            'white': self.__board.WHITE,
            'green': self.__board.GREEN,
            'peacock': self.__board.PEACOCK,
            'plum': self.__board.PLUM,
        }
        self.SUSPECT_TO_STUB_MAP = {v: k for k, v in self.STUB_TO_SUSPECT_MAP.items()}

        self.STUB_TO_SPACE_MAP = {
            'study': self.__board.STUDY,
            'hall': self.__board.HALL,
            'lounge': self.__board.LOUNGE,
            'library': self.__board.LIBRARY,
            'billiard_room': self.__board.BILLIARD_ROOM,
            'dining_room': self.__board.DINING_ROOM,
            'conservatory': self.__board.CONSERVATORY,
            'ballroom': self.__board.BALLROOM,
            'kitchen': self.__board.KITCHEN,
            'study_to_hall': self.__board.STUDY_TO_HALL,
            'hall_to_lounge': self.__board.HALL_TO_LOUNGE,
            'study_to_library': self.__board.STUDY_TO_LIBRARY,
            'hall_to_billiard': self.__board.HALL_TO_BILLIARD,
            'lounge_to_dining': self.__board.LOUNGE_TO_DINING,
            'library_to_billiard': self.__board.LIBRARY_TO_BILLIARD,
            'billiard_to_dining': self.__board.BILLIARD_TO_DINING,
            'library_to_conservatory': self.__board.LIBRARY_TO_CONSERVATORY,
            'billiard_to_ballroom': self.__board.BILLIARD_TO_BALLROOM,
            'dining_to_kitchen': self.__board.DINING_TO_KITCHEN,
            'conservatory_to_ballroom': self.__board.CONSERVATORY_TO_BALLROOM,
            'ballroom_to_kitchen': self.__board.BALLROOM_TO_KITCHEN,
        }
        self.SPACE_TO_STUB_MAP = {v: k for k, v in self.STUB_TO_SPACE_MAP.items()}

        self.STUB_TO_WEAPON_MAP = {
            'rope': self.__board.ROPE,
            'knife': self.__board.KNIFE,
            'lead_pipe': self.__board.LEAD_PIPE,
            'wrench': self.__board.WRENCH,
            'revolver': self.__board.REVOLVER,
            'candlestick': self.__board.CANDLESTICK,
        }
        self.WEAPON_TO_STUB_MAP = {v: k for k, v in self.STUB_TO_WEAPON_MAP.items()}

        self.__game_log = []
        self.__token_to_player_map = {}
        self.__player_to_token_map = {}

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))
        handler.setLevel(logging.DEBUG)
        self.engine_log = logging.getLogger('engine')
        self.engine_log.setLevel(logging.DEBUG)
        self.engine_log.addHandler(handler)
        self.engine_log.addHandler(JSONHandler(self.__game_log))

        # For testing only!
        self.__test_mode = test_mode
        self.__id_pool = iter([
            'a',
            'b',
            'c',
            'd',
            'e',
            'f',
            ])

    # ------ Board Interactions ------

    def add_player(self, name, suspect):
        # Add player
        p = Player(name=name, suspect=self.get_suspect_from_stub(suspect))
        self.__board.add_player(p)

        # Generate a token and map it to the player object
        player_token = self.__make_player_token()
        self.__map_token_to_player(player_token, p)

        return self.get_player(player_token)

    def move_player(self, player_token, space):
        self.__board.move_player(
                player=self.get_player_with_token(player_token),
                space=self.get_space_from_stub(space),
                )

        return True

    def make_suggestion(self, player_token, suspect, weapon):
        player = self.get_player_with_token(player_token)

        self.__board.make_suggestion(
                player=player,
                suspect=self.get_suspect_from_stub(suspect),
                weapon=self.get_weapon_from_stub(weapon),
                )

        if not self.__board.game_over:
            return {
                    'suspect': self.get_stub(player.suggestions[-1]['disprove']['suspect']),
                    'player': player.suggestions[-1]['disprove']['player'].name,
                    'card': self.get_stub(player.suggestions[-1]['disprove']['card']),
                }

    def make_accusation(self, player_token, suspect, weapon, room):
        player = self.get_player_with_token(player_token)

        self.__board.make_accusation(
                player=player,
                suspect=self.get_suspect_from_stub(suspect),
                weapon=self.get_weapon_from_stub(weapon),
                room=self.get_space_from_stub(room) if room else None
                )

    def end_turn(self, player_token):
        self.__board.end_turn(
                player=self.get_player_with_token(player_token)
                )

    # ------ Helpers ------

    def get_player_with_token(self, player_token):
        return self.__token_to_player_map.get(player_token, None)

    def get_player(self, player_token):
        player = self.get_player_with_token(player_token)

        if not player:
            raise InvalidPlayerToken('Couldn\'t find that player')

        return {
            'player_token': player_token,
            'name': player.name,
            'in_the_game': player.in_the_game,
            'is_current_turn': True if self.__board.current_player == player else False,
            'suspect': self.get_stub(player.suspect),
            'cards': [self.get_stub(_) for _ in player.cards],
            'game_sheet': {
                    'rooms': {
                            bs.get_stub(k): v
                            for k, v in player.game_sheet.items()
                            if type(k) is Room
                        },
                    'suspects': {
                            bs.get_stub(k): v
                            for k, v in player.game_sheet.items()
                            if type(k) is Suspect
                        },
                    'weapons': {
                            bs.get_stub(k): v
                            for k, v in player.game_sheet.items()
                            if type(k) is Weapon
                        },
                },
            'suggestions': [
                    {
                        'disprove': {
                            k: bs.get_stub(v) if type(v) is not Player else v.name
                            for k, v in _['disprove'].items()
                        },
                        'suggestion': {
                            k: bs.get_stub(v)
                            for k, v in _['suggestion'].items()
                        }
                    }
                    for _ in player.suggestions
                ],
            'turn': player.turn
        }

    # Go from a shortname/stub to an object

    def get_suspect_from_stub(self, stub):
        if not stub:
            raise InvalidSuspectStub('Must specify a suspect shortname')

        elif stub not in self.STUB_TO_SUSPECT_MAP:
            raise InvalidSuspectStub('{} is not a valid suspect shortname'.format(stub))

        return self.STUB_TO_SUSPECT_MAP.get(stub)

    def get_space_from_stub(self, stub):
        if not stub:
            raise InvalidSpaceStub('Must specify a space shortname')

        elif stub not in self.STUB_TO_SPACE_MAP:
            raise InvalidSpaceStub('{} is not a valid space shortname'.format(stub))

        return self.STUB_TO_SPACE_MAP.get(stub)

    def get_weapon_from_stub(self, stub):
        if not stub:
            raise InvalidWeaponStub('Must specify a weapon shortname')

        elif stub not in self.STUB_TO_WEAPON_MAP:
            raise InvalidWeaponStub('{} is not a valid weapon shortname'.format(stub))

        return self.STUB_TO_WEAPON_MAP.get(stub)

    # Go from an object to a shortname/stub

    def get_stub_from_suspect(self, suspect):
        if suspect not in self.SUSPECT_TO_STUB_MAP:
            raise InvalidSuspect('Invalid suspect')

        return self.SUSPECT_TO_STUB_MAP[suspect]

    def get_stub_from_space(self, space):
        if space not in self.SPACE_TO_STUB_MAP:
            raise InvalidSpace('Invalid space')

        return self.SPACE_TO_STUB_MAP[space]

    def get_stub_from_weapon(self, weapon):
        if weapon not in self.WEAPON_TO_STUB_MAP:
            raise InvalidWeapon('Invalid weapon')

        return self.WEAPON_TO_STUB_MAP[weapon]

    def get_stub(self, board_object):
        return self.get_stub_from_space(board_object) \
                if type(board_object) is Room or type(board_object) is Hallway \
                else self.get_stub_from_weapon(board_object) \
                    if type(board_object) is Weapon \
                else self.get_stub_from_suspect(board_object) \
                    if type(board_object) is Suspect \
                else None

    # Player name and objects

    def get_player_object_from_suspect(self, suspect):
        if self.__board.get_player_mapped_to(suspect):
            return self.__board.get_player_mapped_to(suspect)

        return None

    def get_player_name_from_suspect(self, suspect):
        if self.__board.get_player_mapped_to(suspect):
            return self.__board.get_player_mapped_to(suspect).name

        return None

    def __make_player_token(self):
        if self.__test_mode:
            return next(self.__id_pool)

        return str(uuid4())

    def __make_player_from_suspect(self, suspect):
        return {
            'name': self.get_player_name_from_suspect(suspect),
            'suspect': self.get_stub_from_suspect(suspect),
            'in_the_game': self.get_player_object_from_suspect(suspect).in_the_game if self.get_player_object_from_suspect(suspect) else None
        }

    def __map_token_to_player(self, player_token, player_object):
        self.__token_to_player_map[player_token] = player_object
        self.__player_to_token_map[player_object] = player_token

    # ------ Board Properties ------

    @property
    def state(self):
        return {
            'id': str(self.__board.id),
            'time_started': self.__board.time_started,
            'game_started': self.__board.game_started,
            'game_over': self.__board.game_over,
            'winner': {
                'name': self.__board.winner.name if self.__board.winner else None,
                'suspect': self.get_stub_from_suspect(self.__board.winner.suspect) if self.__board.winner else None
            },
            'suspect_to_player': {
                self.get_stub_from_suspect(suspect): player_object.name if player_object else None
                for suspect, player_object
                in self.__board.suspect_to_player_map.items()
            },
            'players': [{
                            'name': player_object.name if player_object else None,
                            'suspect': self.get_stub_from_suspect(suspect),
                        }
                        for suspect, player_object
                        in self.__board.suspect_to_player_map.items()],
            'current_player': {
                'name': self.__board.current_player.name if self.__board.current_player else None,
                'suspect': self.get_stub_from_suspect(self.__board.current_player.suspect) if self.__board.current_player else None,
                'suspect_fullname': self.__board.current_player.suspect.name if self.__board.current_player else None,
            },
            'unmapped_suspects': [
                {
                    'suspect': self.get_stub_from_suspect(_),
                    'suspect_fullname': _.name,
                }
                for _ in self.__board.unmapped_suspects
            ],
            'map': self.map
        }

    @property
    def metadata(self):
        return {
            'shortname_map': {self.get_stub(_): _.name for _ in self.__board.GAME_DECK + self.__board.LIST_OF_HALLWAYS},
            'organized_shortname_map': {
                    'rooms': {self.get_stub(_): _.name for _ in self.__board.LIST_OF_ROOMS},
                    'hallways': {self.get_stub(_): _.name for _ in self.__board.LIST_OF_HALLWAYS},
                    'spaces': {self.get_stub(_): _.name for _ in self.__board.LIST_OF_SPACES},
                    'suspects': {self.get_stub(_): _.name for _ in self.__board.LIST_OF_SUSPECTS},
                    'weapons': {self.get_stub(_): _.name for _ in self.__board.LIST_OF_WEAPONS},
                },
        }

    @property
    def map(self):
        flatmap = [space
                   for row in self.__board.map
                   for space in row if space is not None
                   ]

        return {
            self.get_stub_from_space(space): {                    
                    'players': [
                        self.__make_player_from_suspect(suspect)
                        for suspect in space.suspects_present
                    ]
                }
                for space in flatmap
            }

    @property
    def log(self):
        return self.__game_log

    @property
    def confidential_file(self):
        return [self.get_stub(_) for _ in self.__board.confidential_file]



app = Flask(__name__)
app.debug = True
api = Api(app)


# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


b = Board()
bs = BoardService(b, test_mode=True)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))
handler.setLevel(logging.INFO)

log = logging.getLogger('CluelessService')
log.setLevel(logging.INFO)
log.addHandler(handler)

class CluelessLog(Resource):
    def get(self):
        return bs.log


class CluelessPlayer(Resource):
    def get(self, player_token):
        try:
            return bs.get_player(player_token)
        except Exception as e:
            return {'message': str(e)}, 404


class CluelessPlayers(Resource):
    def get(self):
        return bs.players

    def post(self):
        try:
            return bs.add_player(
                        name=request.json.get('name'),
                        suspect=request.json.get('suspect'),
                        )
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessEndTurn(Resource):
    def put(self):
        try:
            bs.end_turn(player_token=request.json.get('token'))
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessMakeSuggestion(Resource):
    def put(self):
        try:
            return bs.make_suggestion(
                        player_token=request.json.get('token'),
                        suspect=request.json.get('suspect'),
                        weapon=request.json.get('weapon'),
                        )
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessMakeAccusation(Resource):
    def put(self):
        try:
            bs.make_accusation(
                player_token=request.json.get('token'),
                suspect=request.json.get('suspect'),
                weapon=request.json.get('weapon'),
                room=request.json.get('room'),
                )
        except Exception as e:
            return {'message': str(e)}, 400
        else:
            return {}


class CluelessMove(Resource):
    def put(self):
        try:
            bs.move_player(
                player_token=request.json.get('token'),
                space=request.json.get('space'),
                )
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessMetadata(Resource):
    def get(self):
        return bs.metadata


class CluelessConfidentialFile(Resource):
    def get(self):
        return bs.confidential_file


class Clueless(Resource):
    def get(self):
        return bs.state


api.add_resource(CluelessPlayer, '/api/players/<string:player_token>')
api.add_resource(CluelessPlayers, '/api/players')
api.add_resource(CluelessMove, '/api/move')
api.add_resource(CluelessMakeSuggestion, '/api/suggest')
api.add_resource(CluelessMakeAccusation, '/api/accuse')
api.add_resource(CluelessEndTurn, '/api/end_turn')
api.add_resource(CluelessLog, '/api/logs')
api.add_resource(CluelessMetadata, '/api/meta')
api.add_resource(CluelessConfidentialFile, '/api/confidential_file')
api.add_resource(Clueless, '/api')


@app.route('/new')
def new_game():
    global bs
    bs = BoardService(Board(), test_mode=True)
    return jsonify(bs.state)


@app.route('/')
def client_interface():
    return render_template('index.html')



# if __name__ == '__main__':
#     socketio.run(app)
