'''
Service that facilitates 'talking' to the game engine via JSON. Stores all
the logs as well!
'''

# Board ID and User Key

import json
import arrow
import logging
from uuid import uuid4

from engine import Board, Player
from engine.constants import *
from engine.exceptions import *

stub_to_suspect_map = {
    'scarlet': SCARLET,
    'mustard': MUSTARD,
    'white': WHITE,
    'green': GREEN,
    'peacock': PEACOCK,
    'plum': PLUM,
}
suspect_to_stub_map = {v: k for k, v in stub_to_suspect_map.items()}

stub_to_space_map = {
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
space_to_stub_map = {v: k for k, v in stub_to_space_map.items()}


def jprint(obj):
    print(json.dumps(obj, indent=4))


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


class BoardService():

    def __init__(self, board):
        self.__board = board
        self.__game_log = []

        self.engine_log = logging.getLogger('engine')
        self.engine_log.setLevel(logging.INFO)
        self.engine_log.addHandler(JSONHandler(self.__game_log))

    # ------ Board Interactions ------

    def add_player(self, name, suspect):
        try:
            self.__board.add_player(
                        Player(name=name, suspect=stub_to_suspect_map[suspect]
                    ))
        except InvalidPlayerName as e:
            self.engine_log.error(str(e))
        except KeyError as e:
            self.engine_log.error('{} is not a valid suspect shortname'.format(suspect))
        except PlayerAlreadyMappedToSuspect as e:
            self.engine_log.error(str(e))
        except BoardIsFull as e:
            self.engine_log.error(str(e))

    def move_player(self, space):
        try:
            self.__board.move_player(space=stub_to_space_map[space])
        except KeyError as e:
            self.engine_log.error('{} is not a valid space shortname'.format(space))
        except Exception as e:
            self.engine_log.error(str(e))

    def end_turn(self):
        try:
            self.__board.end_turn()
        except UnfinishedMove as e:
            self.engine_log.error(str(e))
        except GameOver as e:
            self.engine_log.error(str(e))

    # ------ Entity Representations ------

    @property
    def list_of_suspects(self):
        return stub_to_suspect_map.keys()

    @property
    def list_of_spaces(self):
        return stub_to_space_map.keys()

    @property
    def board(self):
        return self.__board

    @property
    def current_player(self):
        return {
            'name': self.__board.current_player.name,
            'suspect': {
                'name': self.__board.current_suspect.name,
                'shortname': suspect_to_stub_map[self.__board.current_suspect],
            },
            # 'space': {
            #     'name': self.__board.get_space_for(self.__board.current_player).name,
            #     'shortname': space_to_stub_map[self.__board.get_space_for(self.__board.current_player)]
            # }
        }

    def board(self):
        state = {
            'spaces': [
                {
                    'name': 'hall',
                    'players': [
                        {
                            'name': None,
                            'suspect': None,
                        },
                        {
                            'name': None,
                            'suspect': None,
                        }
                    ]
                }
            ],
            'current_player': None
        }


    # ------ Logs and Miscellanea ------

    @property
    def game_log(self):
        return self.__game_log

    @property
    def last_log(self):
        return self.__game_log[-1]

    def player_info(self):
        pass


b = Board()
bs = BoardService(b)

bs.add_player(name='', suspect='scarlet')
bs.add_player(name='Anand', suspect='scarlet')
bs.add_player(name='Dawn', suspect='white')
bs.add_player(name='Madhu', suspect='mustard')
bs.add_player(name='Deepu', suspect='green')
bs.add_player(name='Catherine', suspect='peacock')
bs.add_player(name='Tony', suspect='plum')

# jprint(bs.current_player)

bs.move_player('hall')
bs.end_turn()

jprint(bs.game_log)
# jprint(bs.list_of_suspects)
# jprint(bs.last_log)








