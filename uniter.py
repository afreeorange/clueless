import unittest
from engine import Board, Player
from engine.constants import *
from engine.exceptions import *

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


class TestBoard(unittest.TestCase):

    def test_invalid_space_move(self):
        self.assertRaises(InvalidTargetSpace, board.move_player(space=HALL))

    def test_valid_target_space(self):
        self.assertTrue(board.move_player(space=LOUNGE))

if __name__ == '__main__':
    unittest.main()
