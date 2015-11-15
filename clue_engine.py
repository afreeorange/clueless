# Board JSON?
# Split up exceptions
# 

# All objects!
# Six player objects are associated with, and mutate a single Board object
# Add logging
# Type checking in globals()
# Any 'public' methods always use names
# These are turned into the objects with those names for all private methods
# Players and suspect mappings are taken care of by the API

from collections import defaultdict
import json
import random
from datetime import datetime
# import logging
from uuid import uuid4
from itertools import cycle

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

class InsufficientPlayers(Exception):
    pass

class NotPlayersTurn(Exception):
    pass        

class BlockedSpace(Exception):
    pass

class InvalidSpaceForSuggestion(Exception):
    pass

class InvalidSuspect(Exception):
    pass

class InvalidWeapon(Exception):
    pass

class MoveCompleted(Exception):
    pass

class GameOver(Exception):
    pass

class PlayerAlreadyMapped(Exception):
    pass

class Space:
    def __init__(self, name):
        self.name = name
        self.max_allowed_suspects = 1
        self.has_secret_passageway = False
        self.passage_way_to = None
        self.suspects_present = set([])

    def remove_suspect(self, suspect):
        self.suspects_present.remove(suspect)

    def add_suspect(self, suspect):
        # AttributeError thrown if I don't cast this to a set each time :/
        self.suspects_present = set(self.suspects_present)
        self.suspects_present.add(suspect)

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
    #     self.__player = None

    # @property
    # def player(self):
    #     return self.__player

    # @player.setter
    # def player(self, player):
    #     if self.__player:
    #         raise PlayerAlreadyMapped('Player {} already mapped to this suspect'.format(self.player.name))
    #     self.__player = player


class Weapon:
    def __init__(self, name):
        self.name = name

class Player:
    def __init__(self, name, suspect):
        self.__name = name
        self.in_the_game = True
        self.__suspect = suspect
        self.board = None
        self.cards = []
        self.last_suggestion = {
            'weapon': None,
            'suspect': None,
            'room': None,
        }

    def set_last_suggestion(self, room, suspect, weapon):
        self.last_suggestion = {
            'weapon': weapon,
            'suspect': suspect,
            'room': room,
        }

    @property
    def suspect(self):
        return self.__suspect
    
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
                for c in self.cards
            ],
            'in_the_game': self.__in_the_game
        }
    

# Create the weapons
rope = Weapon('rope')
knife = Weapon('knife')
lead_pipe = Weapon('lead pipe')
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
scarlet = Suspect('Miss Scarlet')
mustard = Suspect('Colonel Mustard')
white = Suspect('Mrs. White')
green = Suspect('Mr. Green')
peacock = Suspect('Mrs. Peacock')
plum = Suspect('Professor Plum')

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
study = Room('The Study')
hall = Room('The Hall')
lounge = Room('The Lounge')
library = Room('The Library')
billiard_room = Room('The Billiard Room')
dining_room = Room('The Dining Room')
conservatory = Room('The Conservatory')
ballroom = Room('The Ballroom')
kitchen = Room('The Kitchen')

study_to_hall = Hallway('The Study to Hall Hallway')
hall_to_lounge = Hallway('The Hall to Lounge Hallway')
study_to_library = Hallway('The Study to Library Hallway')
hall_to_billiard = Hallway('The Hall to Billiard Room Hallway')
lounge_to_dining = Hallway('The Lounge to Dining Room Hallway')
library_to_billiard = Hallway('The Library to Billiard Room Hallway')
billiard_to_dining = Hallway('The Billiard Room to Dining Room Hallway')
library_to_conservatory = Hallway('The Library to Conservatory Hallway')
billiard_to_ballroom = Hallway('The Billiard Room to Ballroom Hallway')
dining_to_kitchen = Hallway('The Dining Room to Kitchen Hallway')
conservatory_to_ballroom = Hallway('The Conservatory to Ballroom Hallway')
ballroom_to_kitchen = Hallway('The Ballroom to Kitchen Hallway')

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

# Make a deck
deck_of_cards = list_of_weapons + list(list_of_suspects) + list_of_rooms

class Board:
    def __init__(self):
        self.id = uuid4()
        self.time_started = '{}Z'.format(str(datetime.utcnow().isoformat()))

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
            # 'confidential_file': [
            #     random.choice(list_of_rooms),
            #     random.choice(list_of_suspects),
            #     random.choice(list_of_weapons),
            # ],

            'confidential_file': [
                conservatory,
                plum,
                candlestick
            ],

            # Make a map of suspects to players
            'player_map': dict.fromkeys(list_of_suspects, None),

            # This will be set once all suspects are bound to players
            # Setting this means that the game has begun
            'current_player': None,

            'current_turn': {
                'moved': False,
                'suggested': False,
                'accused': False
            },

            'game_over': False
        }

        # Now that the confidential envelope is set up, shuffle the 
        # remaining deck. Make it an iterable so cards can be distributed
        # to players.
        self.__deck = [_ for _ in deck_of_cards
                         if  _ not in self.__state['confidential_file']]
        random.shuffle(self.__deck)
        self.__deck = iter(self.__deck)

        # Use to yield the next player
        self.__suspect_looper = cycle(list_of_suspects)

        # These are the holes in the board
        self.__bad_coordinates = [(1,1), (1,3), (3,1), (3,3)]

        # These are valid deltas when subtracting coordinates to 
        # validate a move between spaces on the board
        self.__valid_coord_deltas = [(1, 0), (0, 1), (-1, 0), (0, -1),
                                     (4, 4), (4,-4), (-4, 4), (-4,-4),
                                     (0, 0)]

    def add_player(self, player):
        if self.cannot_add_more_players():
            raise BoardIsFull('All players mapped to suspects on this board')

        if self.__state['player_map'][player.suspect]:
            raise PlayerAlreadyMappedToSuspect('{} <-> {}'.format(
                            self.__state['player_map'][suspect].name,
                            suspect.name
                            ))

        self.__state['player_map'][player.suspect] = player
        self.deal_cards_to(player)

        # If this is the last player, start the game
        # The first suspect returned is scarlet
        if self.cannot_add_more_players():
            self.__state['current_player'] = self.__get_player_mapped_to(self.__get_next_suspect())

    def cannot_add_more_players(self):
        if None in set(self.__state['player_map'].values()):
            return False
        return True

    def can_add_more_players(self):
        if None in set(self.__state['player_map'].values()):
            return True
        return False

    def deal_cards_to(self, player):
        # So this is beautiful:
        # [next(self.__deck)] * 3
        # but it will _replicate_ the elements in the list thrice 
        # and won't call __iter__ !
        player.cards = [next(self.__deck),
                        next(self.__deck),
                        next(self.__deck)
                        ]

    def __get_suspect_mapped_to(self, player):
        for k, v in self.__state['player_map'].items():
            if v == player:
                return k

    def __get_player_mapped_to(self, suspect):
        for k, v in self.__state['player_map'].items():
            if k == suspect:
                return v

    def __get_space_for(self, entity):
        suspect = None

        if type(entity) is Suspect:
            suspect = entity
        elif type(entity) is Player:
            suspect = self.__get_suspect_mapped_to(entity)
        else:
            raise ValueError('Must specify either a Player or Suspect object')

        return [_
                for _ in

                # Lists will look like this with the nested comprehensions
                # [[], [<__main__.Hallway object at 0x101f15518>], [], [], []]
                # [[<__main__.Room object at 0x10b617da0>], [], [], [], []]
                [
                    [space
                    for space in row
                    if space is not None and suspect in space.suspects_present
                    ]
                for row in self.__state['map']
                ]

                if _
            ][0][0]

    def __get_coordinates_of(self, space):
        return [(i, _.index(space))
                for i, _ in enumerate(self.__state['map'])
                if space in _
                ][0]

    def __suspects_in_space(self, space):
        return space.suspects_present

    def __valid_target_space(self, old_space, new_space):
        if new_space in self.__bad_coordinates:
            raise InvalidSpace('Cannot move to holes')

        osc = self.__get_coordinates_of(old_space)
        nsc = self.__get_coordinates_of(new_space)

        # Allow the target to be the same as the destination.
        # if osc == nsc:
        #     raise SameTargetSpace('Destination space same as target')

        if tuple(x - y for x, y in zip(osc, nsc)) not in self.__valid_coord_deltas:
            raise InvalidTargetSpace('Cannot teleport to destination space')

        suspects_in_space = [_
                            for _ in self.__suspects_in_space(new_space)
                            if _ != self.__get_suspect_mapped_to(self.__state['current_player'])]

        if self.__get_suspect_mapped_to(self.__state['current_player']) in suspects_in_space:
            raise BlockedSpace('Suspect(s) already in space: {}. Cannot move.'.format(', '.join(suspects)))

        return True

    def __valid_player_turn(self, player):
        current_player = self.__state['current_player']

        if player != current_player:
            raise NotPlayersTurn('Turn belongs to {} ({})'.format(
                        current_player.name,
                        self.__get_suspect_mapped_to(current_player).name,
                    ))

        return True

    def __valid_suspect(self, suspect):
        if suspect not in list_of_suspects:
            raise InvalidSuspect('Invalid suspect')

        return True

    def __valid_weapon(self, weapon):
        if weapon not in list_of_weapons:
            raise InvalidWeapon('Invalid weapon')

        return True

    def __valid_board_state(self):
        if not self.__state['current_player']:
            raise InsufficientPlayers('Not enough players to start the game')

        if self.__state['game_over']:
            raise GameOver('{} ({}) has won the game'.format(self.current_player.name, self.current_suspect.name))

        return True

    def __valid_space_for_suggestion(self):
        """ Player must be in a room to make a suggestion
        """
        space = self.__get_space_for(self.current_player)
        if type(space) is not Room:
            raise InvalidSpaceForSuggestion('Must be in a room to suggest. Currently in {}'.format(space.name))

    @property
    def confidential_file(self):
        return [
            {type(c).__name__: c.name}
            for c
            in self.__state['confidential_file']
        ]

    @property
    def current_player(self):
        return self.__state.get('current_player', None)

    @property
    def current_suspect(self):
        return self.__get_suspect_mapped_to(self.__state.get('current_player', None))

    @property
    def unmapped_suspects(self):
        return [k
                for k, v in self.__state['player_map'].items()
                if v is None
                ]

    def __get_next_suspect(self):
        while True:
            next_suspect = next(self.__suspect_looper)
            next_player = self.__get_player_mapped_to(next_suspect)

            if next_player.in_the_game:
                return next_suspect

    def move_player(self, space):
        player = self.current_player
        suspect = self.current_suspect

        self.__valid_board_state()
        self.__valid_player_turn(player)

        # Update the turn. Throw an error if player already made a move
        if self.__state['current_turn']['moved']:
            raise MoveCompleted('{} ({}) has already moved'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

        old_space = [_
                    for _ in list_of_spaces
                    if suspect in _.suspects_present
                    ][0]
        new_space = space

        self.__valid_target_space(old_space, new_space)

        old_space.remove_suspect(suspect)
        new_space.add_suspect(suspect)

        self.__state['current_turn']['moved'] = True

        if old_space == new_space:
            print('{}:{} stayed in {}'.format(player.name, suspect.name, old_space.name))
        else:
            print('{} ({}) moved to {}'.format(player.name, suspect.name, new_space.name))

    def make_suggestion(self, suspect, weapon):
        self.__valid_board_state()
        self.__valid_player_turn(self.current_player)
        self.__valid_suspect(suspect)
        self.__valid_weapon(weapon)
        self.__valid_space_for_suggestion()

        suspect_space = self.__get_space_for(suspect)
        player_room = self.__get_space_for(self.current_player)

        # Update the turn. Throw an error if player already made a suggestion
        if self.__state['current_turn']['suggested']:
            raise MoveCompleted('{} ({}) has already made a suggestion'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

        self.__state['current_turn']['suggested'] = True
        self.current_player.set_last_suggestion(player_room, suspect, weapon)

        print('{} ({}) suggested that {} ({}) did it with a {} in {}'.format(
                    self.current_player.name,
                    self.current_suspect.name,
                    self.__get_player_mapped_to(suspect).name,
                    suspect.name,
                    weapon.name,
                    player_room.name
                ))

        # First move the suspect into the player's space
        suspect_space.remove_suspect(suspect)
        player_room.add_suspect(suspect)

        print('Moved {} ({}) from {} to {}'.format(
                    self.__get_player_mapped_to(suspect).name,
                    suspect.name,
                    suspect_space.name,
                    player_room.name
                    ))

        # End the game if the suggestion is in the game file
        if [player_room, suspect, weapon] == self.__state['confidential_file']:
            self.__state['game_over'] = True

            print('{} ({})\'s suggestion was correct. Game Over!'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

    def make_accusation(self, suspect, weapon):

        # Suspects don't move

        # Player out of game if wrong

        # End game if right
        pass

    def get_nearest_disprover(self):

        if not self.__state['current_turn']['suggested']:
            raise UnfinishedTurn('Must make a suggestion before getting a card to disprove it')

        # Need to cycle through the list of suspects clockwise
        suspect_index = list_of_suspects.index(self.current_suspect)
        bottom = list_of_suspects[suspect_index + 1:]
        top = list_of_suspects[:suspect_index]

        our_suggestion = self.current_player.last_suggestion.values()
        
        for suspect in bottom + top:
            their_cards = self.__get_player_mapped_to(suspect).cards

            # Cast to list because, for some reason, 
            # 'if not common_cards' doesn't work :/
            common_cards = list(set(their_cards) & set(our_suggestion))

            # If the next player has card(s) to disprove the suggestion,
            # pick one and return it
            if common_cards:
                random_card = random.choice(common_cards).name

                print('{} ({}) showed "{}"'.format(
                    self.__get_player_mapped_to(suspect).name,
                    suspect.name,
                    random_card
                    ))

                return random_card

    def end_turn(self):
        self.__valid_board_state()

        # Can only end turn if moved and suggested
        if not self.__state['current_turn']['moved']:
            raise UnfinishedTurn('Must make a move')

        if not self.__state['current_turn']['suggested']:
            raise UnfinishedTurn('Must make a suggestion')

        # Reset the turn tracker
        for key in self.__state['current_turn']:
            self.__state['current_turn'][key] = False

        # Get the next suspect's player and mark them current
        self.__state['current_player'] = self.__get_player_mapped_to(self.__get_next_suspect())


if __name__ == '__main__':
    board = Board()

    print('Started game {}\nat {}'.format(board.id, board.time_started))
    print('Confidential file contains {}'.format(board.confidential_file))

    p1 = Player(name='Nikki', suspect=scarlet)
    p2 = Player(name='Dawn', suspect=white)
    p3 = Player(name='Madhu', suspect=mustard)
    p4 = Player(name='Deepu', suspect=green)
    p5 = Player(name='Catherine', suspect=peacock)
    p6 = Player(name='Tony', suspect=plum)

    board.add_player(p1)
    board.add_player(p2)
    board.add_player(p3)
    board.add_player(p4)
    board.add_player(p5)
    board.add_player(p6)

    print('>>> Current player is {} ({})'.format(board.current_player.name, board.current_suspect.name))
    board.move_player(space=hall)
    board.make_suggestion(suspect=plum, weapon=rope)
    board.get_nearest_disprover()
    board.end_turn()

    print('>>> Current player is {} ({})'.format(board.current_player.name, board.current_suspect.name))
    board.move_player(space=lounge)
    board.make_suggestion(suspect=white, weapon=candlestick)
    board.get_nearest_disprover()
    board.end_turn()

    print('>>> Current player is {} ({})'.format(board.current_player.name, board.current_suspect.name))
    board.move_player(space=lounge)
    board.make_suggestion(suspect=white, weapon=knife)
    board.get_nearest_disprover()
    board.end_turn()

    print('>>> Current player is {} ({})'.format(board.current_player.name, board.current_suspect.name))
    board.move_player(space=conservatory)
    board.make_suggestion(suspect=plum, weapon=candlestick)
    board.get_nearest_disprover()
    board.end_turn()

