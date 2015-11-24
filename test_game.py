import logging
import sys
import json

from engine import Board, Player
from engine.constants import *

handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))

engine_logger = logging.getLogger('engine')
engine_logger.setLevel(logging.INFO)
engine_logger.addHandler(handler)

logger = logging.getLogger('game')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger.info('Initializing board...')
board = Board()

p1 = Player(name='Nikhil', suspect=SCARLET)
p2 = Player(name='Dawn', suspect=WHITE)
p3 = Player(name='Madhu', suspect=MUSTARD)
p4 = Player(name='Deepu', suspect=GREEN)
p5 = Player(name='Catherine', suspect=PEACOCK)
p6 = Player(name='Tony', suspect=PLUM)

board.add_player(p1)
board.add_player(p2)
board.add_player(p3)
board.add_player(p4)
board.add_player(p5)
board.add_player(p6)

logger.info('Current player is {} ({})'.format(board.current_player.name, board.current_suspect.name))
board.move_player(p1, space=LOUNGE)
board.make_suggestion(player=p1, suspect=PLUM, weapon=ROPE)
disprover = board.disprove_suggestion(p1)
board.end_turn(p1)

for _ in p1.cards:
    print('Card:', _.name)

print()

for k, v in p1.deduction_book.items():
    if v is False:
        print(k.name, v)

print(p1.suggestions)

# logger.info('Current player is {} ({})'.format(board.current_player.name, board.current_suspect.name))
# board.move_player(space=LOUNGE)
# board.make_suggestion(suspect=PLUM, weapon=ROPE)
# board.disprove_suggestion()
# board.end_turn()
