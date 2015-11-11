# Will be the job of the API to globals()['scarlet'] etc

# Six player objects are associated with, and mutate a single Board object
# Add logging
# Type checking in globals()
# Any 'public' methods always use names
# These are turned into the objects with those names for all private methods
# Players and suspect mappings are taken care of by the API

from collections import defaultdict
import json
import random
import arrow
# import logging
from uuid import uuid4

# logger = logging.getLogger(__name__)


class InvalidSpace(Exception):
    pass

class SameTargetSpace(Exception):
    pass

class InvalidTargetSpace(Exception):
    pass
 
class UnfinishedTurn(Exception):
    pass

class PlayerAlreadyMappedToSuspect(Exception):
    pass

class BoardIsFull(Exception):
    pass

class Space:
    def __init__(self, name):
        self.name = name
        self.max_allowed_suspects = 1
        self.has_secret_passageway = False
        self.passage_way_to = None
        self.suspects_present = set([])


class Room(Space):
    def __init__(self, name):
        super().__init__(name)
        self.max_allowed_suspects = 6


class Hallway(Space):
    def __init__(self, name):
        super().__init__(name)


class Suspect:
    def __init__(self, name):
        self.name = name


class Weapon:
    def __init__(self, name):
        self.name = name

class Player:
    def __init__(self, board, name, suspect):
        try:
            board.add_player(self, suspect)
        except Exception:
            raise

        self.__board = board
        self.__name = name
        self.__suspect = suspect
        self.__cards = board.get_cards_for(self)
        self.__in_the_game = True

    @property
    def name(self):
        return self.__name

    @property
    def state(self):
        return {
            'name': self.__name,
            'suspect': self.__suspect.name,
            'cards': [
                {type(c).__name__: c.name}
                for c in self.__cards
            ],
            'in_the_game': self.__in_the_game
        }

    # @property
    # def cards(self):
    #     return [
    #         {type(c).__name__: c.name}
    #         for c in self.__cards
    #     ]

    # @property
    # def suspect(self):
    #     return self.__suspect.name
    

# Create the weapons
rope = Weapon('rope')
knife = Weapon('knife')
lead_pipe = Weapon('lead_pipe')
wrench = Weapon('wrench')
revolver = Weapon('revolver')
candlestick = Weapon('candlestick')

list_of_weapons = [
    rope,
    knife,
    lead_pipe,
    wrench,
    revolver,
    candlestick
    ]

# Create the Suspects
scarlet = Suspect('scarlet')
mustard = Suspect('mustard')
white = Suspect('white')
green = Suspect('green')
peacock = Suspect('peacock')
plum = Suspect('plum')

# Used to iterate over suspects/turns
list_of_suspects = (
    scarlet,
    mustard,
    white,
    green,
    peacock,
    plum,
    )

# Start creating the spaces
study = Room('study')
hall = Room('hall')
lounge = Room('lounge')
library = Room('library')
billiard_room = Room('billiard_room')
dining_room = Room('dining_room')
conservatory = Room('conservatory')
ballroom = Room('ballroom')
kitchen = Room('kitchen')

study_to_hall = Hallway('study_to_hall')
hall_to_lounge = Hallway('hall_to_lounge')
study_to_library = Hallway('study_to_library')
hall_to_billiard = Hallway('hall_to_billiard')
lounge_to_dining = Hallway('lounge_to_dining')
library_to_billiard = Hallway('library_to_billiard')
billiard_to_dining = Hallway('billiard_to_dining')
library_to_conservatory = Hallway('library_to_conservatory')
billiard_to_ballroom = Hallway('billiard_to_ballroom')
dining_to_kitchen = Hallway('dining_to_kitchen')
conservatory_to_ballroom = Hallway('conservatory_to_ballroom')
ballroom_to_kitchen = Hallway('ballroom_to_kitchen')

# Define the spaces a little more
study.has_secret_passageway = True
study.passage_way_to = kitchen

lounge.has_secret_passageway = True
lounge.passage_way_to = conservatory

conservatory.has_secret_passageway = True
conservatory.passage_way_to = lounge

kitchen.has_secret_passageway = True
kitchen.passage_way_to = study

# Add the suspects
hall_to_lounge.suspects_present = [scarlet]
study_to_library.suspects_present = [plum]
lounge_to_dining.suspects_present = [mustard]
library_to_conservatory.suspects_present = [peacock]
conservatory_to_ballroom.suspects_present = [green]
ballroom_to_kitchen.suspects_present = [white]

# Add the spaces
list_of_rooms = [
    study,
    hall,
    lounge,
    library,
    billiard_room,
    dining_room,
    conservatory,
    ballroom,
    kitchen
    ]

list_of_hallways = [
    study_to_hall,
    hall_to_lounge,
    study_to_library,
    hall_to_billiard,
    lounge_to_dining,
    library_to_billiard,
    billiard_to_dining,
    library_to_conservatory,
    billiard_to_ballroom,
    dining_to_kitchen,
    conservatory_to_ballroom,
    ballroom_to_kitchen
    ]

list_of_spaces = list_of_rooms + list_of_hallways

# Now make an ordered deck
deck_of_cards = list_of_weapons + list(list_of_suspects) + list_of_rooms

class Board:
    def __init__(self):
        self.id = uuid4()
        self.time_started = str(arrow.now())

        self.__state = {
            # The Board is a 5x5 grid with four holes
            'map': [
                [study, study_to_hall, hall, hall_to_lounge, lounge],
                [study_to_library, None, hall_to_billiard, None, lounge_to_dining],
                [library, library_to_billiard, billiard_room, billiard_to_dining, dining_room],
                [library_to_conservatory, None, billiard_to_ballroom, None, dining_to_kitchen],
                [conservatory, conservatory_to_ballroom, ballroom, ballroom_to_kitchen, kitchen]
            ],

            # Create the confidential case file
            'confidential_file': [
                random.choice(list_of_rooms),
                random.choice(list_of_suspects),
                random.choice(list_of_weapons),
            ],

            'player_map': dict.fromkeys(list_of_suspects, None)
        }

        # Now that the confidential envelope is set up, shuffle the 
        # remaining deck. Make it an iterable so cards can be distributed
        # to players
        self.__deck = [_
                       for _ in deck_of_cards
                       if _ not in self.__state['confidential_file']
                    ]
        random.shuffle(self.__deck)
        self.__deck = iter(self.__deck)

        # These are the holes in the board
        self.__bad_coordinates = [(1,1), (1,3), (3,1), (3,3)]

        # These are valid deltas when subtracting coordinates to validate a move
        self.__valid_coord_deltas = [(1,0), (0,1), (-1,0), (0,-1)]

    def add_player(self, player, suspect):
        if self.cannot_add_more_players():
            raise BoardIsFull('All players mapped to suspects on this board')

        if self.__state['player_map'][suspect]:
            raise PlayerAlreadyMappedToSuspect('{} <-> {}'.format(
                            self.__state['player_map'][suspect].name,
                            suspect.name
                            ))

        self.__state['player_map'][suspect] = player

    def cannot_add_more_players(self):
        if None in set(self.__state['player_map'].values()):
            return False
        return True

    def get_suspect_mapped_to(self, player):
        for k, v in self.__state['player_map'].items():
            if v == player:
                return k

    def get_cards_for(self, player):
        return [next(self.__deck), next(self.__deck), next(self.__deck)]

    def __coordinates_of(self, space):
        return [(i, _.index(space))
                for i, _ in enumerate(self.__state['map'])
                if space in _
                ][0]

    def __valid_destination_space(self, old_space, new_space):
        if new_space in self.__bad_coordinates:
            raise InvalidSpace('Cannot move to holes')

        osc = self.__coordinates_of(old_space)
        nsc = self.__coordinates_of(new_space)

        if osc == nsc:
            raise SameTargetSpace('Destination space same as target')

        if tuple(x - y for x, y in zip(osc, nsc)) not in self.__valid_coord_deltas:
            raise InvalidTargetSpace('Cannot move to destination space')

        return True

    @property
    def confidential_file(self):
        return [
            {type(c).__name__: c.name}
            for c
            in self.__state['confidential_file']
        ]

if __name__ == '__main__':
    b = Board()

    print('Started game {}\nat {}'.format(b.id, b.time_started))
    print('Confidential file contains {}'.format(b.confidential_file))

    p1 = Player(board=b, name='Nikhil', suspect=scarlet)
    p2 = Player(board=b, name='Deepu', suspect=white)
    p3 = Player(board=b, name='Madhu', suspect=mustard)
    p4 = Player(board=b, name='Dawn', suspect=green)
    p5 = Player(board=b, name='Tony', suspect=peacock)
    p6 = Player(board=b, name='BOOBOO', suspect=plum)

    # print(p1.state)
    # print(p2.state)
    # print(p3.state)
    # print(p4.state)
    # print(p5.state)
    # print(p6.state)

    # p1 = Player('Nikhil')
    # p2 = Player('Deepu')
    # p3 = Player('Madhu')
    # p4 = Player('Dawn')
    # p5 = Player('Tony')
    # p6 = Player('Fraulein')
    # p7 = Player('Frauleina')

    # b.add_player(p1, 'scarlet')
    # b.add_player(p2, 'white')
    # b.add_player(p3, 'mustard')
    # b.add_player(p4, 'green')
    # b.add_player(p5, 'peacock')
    # b.add_player(p6, 'plum')

    # print([_.name for _ in p1.cards])
    # print([_.name for _ in p2.cards])
    # print([_.name for _ in p3.cards])
    # print([_.name for _ in p4.cards])
    # print([_.name for _ in p5.cards])
    # print([_.name for _ in p6.cards])

    # p1.move(space='hall_to_lounge')

    # b.move_suspect(name='scarlet', room='study')
    # b.make_suggestion(suggestor='scarlet',
    #                   suggested='scarlet',
    #                   room='study',
    #                   weapon='')
    # b.make_accusation(accuser='scarlet',
    #                   accused='scarlet',
    #                   room='study',
    #                   weapon='')



