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
from uuid import uuid4

import arrow
from engine import Board, Player
from engine.constants import *
from engine.exceptions import *
from engine.models import Room, Hallway, Weapon, Suspect
from flask import Flask, render_template, request
from flask_restful import Api, Resource
# from flask_socketio import SocketIO, emit, send

STUB_TO_SUSPECT_MAP = {
    'scarlet': SCARLET,
    'mustard': MUSTARD,
    'white': WHITE,
    'green': GREEN,
    'peacock': PEACOCK,
    'plum': PLUM,
}
SUSPECT_TO_STUB_MAP = {v: k for k, v in STUB_TO_SUSPECT_MAP.items()}

STUB_TO_SPACE_MAP = {
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
SPACE_TO_STUB_MAP = {v: k for k, v in STUB_TO_SPACE_MAP.items()}

STUB_TO_WEAPON_MAP = {
    'rope': ROPE,
    'knife': KNIFE,
    'lead_pipe': LEAD_PIPE,
    'wrench': WRENCH,
    'revolver': REVOLVER,
    'candlestick': CANDLESTICK,
}
WEAPON_TO_STUB_MAP = {v: k for k, v in STUB_TO_WEAPON_MAP.items()}


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
        print('Socket HAndler', record)
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
        print('JSON HAndler', record)
        self.json_object.append({
                'timestamp': str(arrow.now()),
                'level': record.levelname,
                'message': record.msg,
            })


class BoardService:

    def __init__(self, board, test_mode=False):
        self.__board = board
        self.__game_log = []
        self.__token_to_player_map = {}
        self.__player_to_token_map = {}

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))
        self.engine_log = logging.getLogger('engine')
        self.engine_log.setLevel(logging.INFO)
        self.engine_log.addHandler(handler)
        self.engine_log.addHandler(JSONHandler(self.__game_log))

        # For testing only!
        self.__test_mode = test_mode
        self.__uuid_pool = iter([
            '7708cdac-30ad-4b09-9e8f-1d53c41bb50f',
            'c4b8c5c1-4ac0-496b-bdff-e5b5e1569754',
            'ec240d35-2d5f-49a2-8266-f3f1c3d7b3b1',
            'af522c0c-4abc-4f1f-b6e1-d87892aadcd8',
            '08ac64a9-80c5-49d4-8f75-3c743c61a31d',
            'a3989584-79c9-43b8-b174-bbab582a1e8b',
            ])

    # ------ Board Interactions ------

    def add_player(self, name, suspect):
        # Add player
        p = Player(name=name, suspect=self.__get_suspect_from_stub(suspect))
        self.__board.add_player(p)

        # Generate a token and map it to the player object
        player_token = self.__make_player_token()
        self.__map_token_to_player(player_token, p)

        return player_token

    def move_player(self, player_token, space):
        self.__board.move_player(
                player=self.__get_player_with_token(player_token),
                space=self.__get_space_from_stub(space),
                )

        return True

    def make_suggestion(self, player_token, suspect, weapon):
        player = self.__get_player_with_token(player_token)

        self.__board.make_suggestion(
                player=player,
                suspect=self.__get_suspect_from_stub(suspect),
                weapon=self.__get_weapon_from_stub(weapon),
                )

        if not self.__board.game_over:
            return self.disprove_suggestion(player_token)

    def disprove_suggestion(self, player_token):
        player = self.__get_player_with_token(player_token)
        disprover, disprover_suspect, disprover_card = self.__board.disprove_suggestion(player)

        if type(disprover_card) is Room:
            card = self.__get_stub_from_space(disprover_card)
        elif type(disprover_card) is Weapon:
            card = self.__get_stub_from_weapon(disprover_card)
        elif type(disprover_card) is Suspect:
            card = self.__get_stub_from_suspect(disprover_card)

        return {
                'disprover': disprover.name,
                'suspect': disprover_suspect.name,
                'card': card
            }

    def end_turn(self, player_token):
        self.__board.end_turn(
                player=self.__get_player_with_token(player_token)
                )

    # ------ Private Helpers ------

    def __get_player_with_token(self, player_token):
        return self.__token_to_player_map.get(player_token, None)

    # Go from a shortname/stub to an object

    def __get_suspect_from_stub(self, stub):
        if not stub:
            raise InvalidSuspectStub('Must specify a suspect shortname')

        elif stub not in STUB_TO_SUSPECT_MAP:
            raise InvalidSuspectStub('{} is not a valid suspect shortname'.format(stub))

        return STUB_TO_SUSPECT_MAP.get(stub)

    def __get_space_from_stub(self, stub):
        if not stub:
            raise InvalidSpaceStub('Must specify a space shortname')

        elif stub not in STUB_TO_SPACE_MAP:
            raise InvalidSpaceStub('{} is not a valid space shortname'.format(stub))

        return STUB_TO_SPACE_MAP.get(stub)

    def __get_weapon_from_stub(self, stub):
        if not stub:
            raise InvalidWeaponStub('Must specify a weapon shortname')

        elif stub not in STUB_TO_WEAPON_MAP:
            raise InvalidWeaponStub('{} is not a valid weapon shortname'.format(stub))

        return STUB_TO_WEAPON_MAP.get(stub)

    # Go from an object to a shortname/stub

    def __get_stub_from_suspect(self, suspect):
        if suspect not in SUSPECT_TO_STUB_MAP:
            raise InvalidSuspect('Invalid suspect')

        return SUSPECT_TO_STUB_MAP[suspect]

    def __get_stub_from_space(self, space):
        if space not in SPACE_TO_STUB_MAP:
            raise InvalidSpace('Invalid space')

        return SPACE_TO_STUB_MAP[space]

    def __get_stub_from_weapon(self, weapon):
        if weapon not in WEAPON_TO_STUB_MAP:
            raise InvalidWeapon('Invalid weapon')

        return WEAPON_TO_STUB_MAP[weapon]

    def __make_player_token(self):
        if self.__test_mode:
            return next(self.__uuid_pool)
        return str(uuid4())

    def __map_token_to_player(self, player_token, player_object):
        self.__token_to_player_map[player_token] = player_object
        self.__player_to_token_map[player_object] = player_token

    # ------ Public Helpers ------

    def player_cards(self, player_token):
        player = self.__get_player_with_token(player_token)

    def get_player(self, player_token):
        return self.__get_player_with_token(player_token)

    # ------ Board Properties ------

    @property
    def state(self):
        return {
            'id': str(self.__board.id),
            'game_started': self.__board.game_started,
            'game_over': self.__board.game_over,
            'winner': None,
            'time_started': self.__board.time_started,
            'players': self.players,
            'current_player': {
                'name': self.__board.current_player.name if self.__board.current_player else None,
                'suspect': SUSPECT_TO_STUB_MAP[self.__board.current_player.suspect] if self.__board.current_player else None,
            },
            'shortname_map': {get_shortname(_): _.name for _ in GAME_DECK}
        }

    @property
    def players(self):
        return [{
                    'name': player_object.name if player_object else None,
                    'suspect': SUSPECT_TO_STUB_MAP[suspect]
                }
                for suspect, player_object
                in self.__board.suspect_to_player_map.items()]

    @property
    def map(self):

        for row in self.__board.map:
            for space in row:
                if space:
                    print(SPACE_TO_STUB_MAP[space], ':', [SUSPECT_TO_STUB_MAP[suspect] for suspect in space.suspects_present])

        return '[]'

    @property
    def log(self):
        return self.__game_log


app = Flask(__name__, template_folder='./', static_folder='./__misc')
app.debug = True
api = Api(app)

b = Board()
bs = BoardService(b, test_mode=True)


def get_shortname(board_object):
    return SPACE_TO_STUB_MAP[board_object] \
            if type(board_object) is Room or type(board_object) is Hallway \
            else WEAPON_TO_STUB_MAP[board_object] \
                if type(board_object) is Weapon \
            else SUSPECT_TO_STUB_MAP[board_object] \
                if type(board_object) is Suspect \
            else None


class CluelessLog(Resource):
    def get(self):
        return bs.log


class CluelessPlayer(Resource):
    def get(self, player_token):
        player = bs.get_player(player_token)

        if not player:
            return {'error': 'Couldn\'t find that player'}, 404

        player_cards = [get_shortname(_) for _ in player.cards]
        player_suggestions = [
                    {
                        k: get_shortname(v)
                        for k, v in _.items()
                    }
                    for _ in player.suggestions
                ]
        game_sheet = {
                    'rooms': {
                            get_shortname(k): v
                            for k, v in player.game_sheet.items()
                            if type(k) is Room
                        },
                    'suspects': {
                            get_shortname(k): v
                            for k, v in player.game_sheet.items()
                            if type(k) is Suspect
                        },
                    'weapons': {
                            get_shortname(k): v
                            for k, v in player.game_sheet.items()
                            if type(k) is Weapon
                        },
                }

        return {
                'name': player.name,
                'suspect': SUSPECT_TO_STUB_MAP[player.suspect],
                'cards': player_cards,
                'suggestions': player_suggestions,
                'game_sheet': game_sheet,
                'in_the_game': player.in_the_game,
            }


class CluelessPlayers(Resource):
    def get(self):
        return bs.players

    def post(self):
        try:
            player_token = bs.add_player(
                                name=request.json.get('name'),
                                suspect=request.json.get('suspect'),
                                )
        except Exception as e:
            return {'error': str(e)}, 400
        else:
            return {
                'data': {
                    'player_token': player_token
                }
            }


class CluelessEndTurn(Resource):
    def put(self):
        try:
            bs.end_turn(player_token=request.json.get('token'))
        except Exception as e:
            return {'error': str(e)}, 400


class CluelessMakeSuggestion(Resource):
    def put(self):
        try:
            disprover = bs.make_suggestion(
                player_token=request.json.get('token'),
                suspect=request.json.get('suspect'),
                weapon=request.json.get('weapon'),
                )
        except Exception as e:
            return {'error': str(e)}, 400
        else:
            return disprover


class CluelessDisproveSuggestion(Resource):
    def get(self):
        pass
        

class CluelessMove(Resource):
    def put(self):
        try:
            bs.move_player(
                player_token=request.json.get('token'),
                space=request.json.get('space'),
                )
        except Exception as e:
            return {'error': str(e)}, 400


class Clueless(Resource):
    def get(self):
        return bs.state


api.add_resource(CluelessLog, '/api/log')
api.add_resource(CluelessPlayer, '/api/players/<string:player_token>')
api.add_resource(CluelessPlayers, '/api/players')
api.add_resource(CluelessMove, '/api/move')
api.add_resource(CluelessMakeSuggestion, '/api/make_suggestion')
api.add_resource(CluelessEndTurn, '/api/end_turn')
api.add_resource(Clueless, '/api')


@app.route('/test')
def test():
    return bs.map


@app.route('/')
def client_interface():
    return render_template('socket_client.html')




# if __name__ == '__main__':
#     socketio.run(app)



# @app.route('/test')
# def test():
#     board.add_player(Player(name='Nikhil', suspect=SCARLET))
#     socketio.emit('client channel', {
#             'data': 'alksjdlkasjdlkasj'
#         })
#     return 'Done!'



#     def move_player(self, space):
#         try:
#             self.__board.move_player(space=STUB_TO_SPACE_MAP[space])
#         except KeyError as e:
#             self.engine_log.error('{} is not a valid space shortname'.format(space))
#         except Exception as e:
#             self.engine_log.error(str(e))

#     def end_turn(self):
#         try:
#             self.__board.end_turn()
#         except UnfinishedMove as e:
#             self.engine_log.error(str(e))
#         except GameOver as e:
#             self.engine_log.error(str(e))

#     # ------ Entity Representations ------

#     @property
#     def list_of_suspects(self):
#         return STUB_TO_SUSPECT_MAP.keys()

#     @property
#     def list_of_spaces(self):
#         return STUB_TO_SPACE_MAP.keys()

#     @property
#     def board(self):
#         return self.__board

#     @property
#     def current_player(self):
#         return {
#             'name': self.__board.current_player.name,
#             'suspect': {
#                 'name': self.__board.current_suspect.name,
#                 'shortname': SUSPECT_TO_STUB_MAP[self.__board.current_suspect],
#             },
#             # 'space': {
#             #     'name': self.__board.get_space_for(self.__board.current_player).name,
#             #     'shortname': SPACE_TO_STUB_MAP[self.__board.get_space_for(self.__board.current_player)]
#             # }
#         }

#     def board(self):
#         state = {
#             'spaces': [
#                 {
#                     'name': 'hall',
#                     'players': [
#                         {
#                             'name': None,
#                             'suspect': None,
#                         },
#                         {
#                             'name': None,
#                             'suspect': None,
#                         }
#                     ]
#                 }
#             ],
#             'current_player': None
#         }




# b = Board()
# bs = BoardService(b)

# bs.add_player(name='', suspect='scarlet')
# bs.add_player(name='Anand', suspect='scarlet')
# bs.add_player(name='Dawn', suspect='white')
# bs.add_player(name='Madhu', suspect='mustard')
# bs.add_player(name='Deepu', suspect='green')
# bs.add_player(name='Catherine', suspect='peacock')
# bs.add_player(name='Tony', suspect='plum')

# # jprint(bs.current_player)

# bs.move_player('hall')
# bs.end_turn()

# jprint(bs.game_log)
# # jprint(bs.list_of_suspects)
# # jprint(bs.last_log)
# engine_log.addHandler(SocketIOLoggingHandler(socketio, 'broadcast channel'))
# socketio = SocketIO(app)