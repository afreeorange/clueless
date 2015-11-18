from datetime import datetime
from itertools import cycle
import logging
import random
from uuid import uuid4

from .exceptions import (
    BlockedSpace,
    BoardIsFull,
    GameOver,
    InsufficientPlayers,
    InvalidHallway,
    InvalidRoom,
    InvalidSpace,
    InvalidSpaceForSuggestion,
    InvalidSuspect,
    InvalidTargetSpace,
    InvalidWeapon,
    MoveCompleted,
    NotPlayersTurn,
    PlayerAlreadyMappedToSuspect,
    UnfinishedMove,
    )


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

from .game_elements import *
log = logging.getLogger(__name__)

class Board:
    def __init__(self):
        self.id = uuid4()
        self.time_started = '{}Z'.format(str(datetime.utcnow().isoformat()))

        self.__state = {
            # The Board is a 5x5 grid with four holes
            'map': [
                [STUDY, STUDY_TO_HALL, HALL, HALL_TO_LOUNGE, LOUNGE],
                [STUDY_TO_LIBRARY, None, HALL_TO_BILLIARD, None, LOUNGE_TO_DINING],
                [LIBRARY, LIBRARY_TO_BILLIARD, BILLIARD_ROOM, BILLIARD_TO_DINING, DINING_ROOM],
                [LIBRARY_TO_CONSERVATORY, None, BILLIARD_TO_BALLROOM, None, DINING_TO_KITCHEN],
                [CONSERVATORY, CONSERVATORY_TO_BALLROOM, BALLROOM, BALLROOM_TO_KITCHEN, KITCHEN]
            ],

            # Create the confidential case file
            # 'confidential_file': [
            #     random.choice(LIST_OF_ROOMS),
            #     random.choice(LIST_OF_SUSPECTS),
            #     random.choice(LIST_OF_WEAPONS),
            # ],

            'confidential_file': [
                CONSERVATORY,
                PLUM,
                CANDLESTICK
            ],

            # Make a map of suspects to players
            'player_map': dict.fromkeys(LIST_OF_SUSPECTS, None),

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
        self.__deck = [_ for _ in GAME_DECK
                       if _ not in self.__state['confidential_file']]
        random.shuffle(self.__deck)
        self.__deck = iter(self.__deck)

        # Use to yield the next player
        self.__suspect_looper = cycle(LIST_OF_SUSPECTS)

        # These are the holes in the board
        self.__bad_coordinates = [(1, 1), (1, 3), (3, 1), (3, 3)]

        # These are valid deltas when subtracting coordinates to
        # validate a move between spaces on the board
        self.__valid_coord_deltas = [(1, 0), (0, 1), (-1, 0), (0, -1),
                                     (4, 4), (4, -4), (-4, 4), (-4, -4),
                                     (0, 0)]

        log.info('Started game')
        log.info('Confidential file contains "{}"'.format(
                    '", "'.join([_.name for _ in self.confidential_file])
                    ))

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

        log.info('Added player {} as {}'.format(
                player.name,
                player.suspect.name
            ))

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
        if suspect not in LIST_OF_SUSPECTS:
            raise InvalidSuspect('Invalid suspect')

        return True

    def __valid_weapon(self, weapon):
        if weapon not in LIST_OF_WEAPONS:
            raise InvalidWeapon('Invalid weapon')

        return True

    def __valid_room(self, room):
        if room not in LIST_OF_ROOMS:
            raise InvalidRoom('Invalid room')

        return True

    def __valid_hallway(self, hallway):
        if hallway not in LIST_OF_HALLWAYS:
            raise InvalidHallway('Invalid hallway')

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
            raise InvalidSpaceForSuggestion('{} ({}) must be in a room to suggest; currently in {}'.format(
                        self.current_player.name,
                        self.current_suspect.name,
                        space.name
                    ))

    @property
    def confidential_file(self):
        return self.__state['confidential_file']

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
        """
        This will keep looping!
        """
        while True:
            next_suspect = next(self.__suspect_looper)
            next_player = self.__get_player_mapped_to(next_suspect)

            if next_player.in_the_game is False:
                log.warning('{} ({}) is not in the game; skipping'.format(
                        next_player.name,
                        next_suspect.name
                    ))
            else:
                return next_suspect

    def move_player(self, space=None):
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
                     for _ in LIST_OF_SPACES
                     if suspect in _.suspects_present
                     ][0]
        new_space = old_space if not space else space

        self.__valid_target_space(old_space, new_space)

        old_space.remove_suspect(suspect)
        new_space.add_suspect(suspect)

        self.__state['current_turn']['moved'] = True

        if old_space == new_space:
            log.info('{} ({}) stayed in {}'.format(player.name, suspect.name, old_space.name))
        else:
            log.info('{} ({}) moved to {}'.format(player.name, suspect.name, new_space.name))

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

        log.info('{} ({}) suggested that {} ({}) did it with a {} in {}'.format(
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

        log.info('Moved {} ({}) from {} to {}'.format(
                    self.__get_player_mapped_to(suspect).name,
                    suspect.name,
                    suspect_space.name,
                    player_room.name
                    ))

        # End the game if the suggestion is in the game file
        if [player_room, suspect, weapon] == self.__state['confidential_file']:
            self.__state['game_over'] = True

            log.info('{} ({})\'s suggestion was correct. Game Over!'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

        return True

    def make_accusation(self, suspect, weapon, room):
        """
        * Players can make accusation any time. No need to move or
          suggest beforehand.
        * Player is out of game if the accusation is incorrect.
        * The game ends if the accusation is correct.
        """
        self.__valid_board_state()
        self.__valid_player_turn(self.current_player)
        self.__valid_suspect(suspect)
        self.__valid_weapon(weapon)
        self.__valid_room(room)

        player_room = self.__get_space_for(self.current_player)

        log.info('{} ({}) accused {} ({}) of doing it with a {} in {}'.format(
                    self.current_player.name,
                    self.current_suspect.name,
                    self.__get_player_mapped_to(suspect).name,
                    suspect.name,
                    weapon.name,
                    player_room.name
                ))

        # End the game if the suggestion is in the game file
        if [player_room, suspect, weapon] == self.__state['confidential_file']:
            self.__state['game_over'] = True
            log.info('{} ({})\'s accusation was correct. Game Over!'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

        # Kick the player out of the game if incorrect
        else:
            self.current_player.in_the_game = False
            log.info('{} ({}) is now out of the game due to a wrong accusation'.format(
                        self.current_player.name,
                        self.current_suspect.name,
                    ))
            self.end_turn(force=True)

        return True

    def get_nearest_disprover(self):
        self.__valid_board_state()
        self.__valid_player_turn(self.current_player)

        if not self.__state['current_turn']['suggested']:
            raise UnfinishedMove('{} ({}) must make a suggestion before getting a card to disprove it'.format(
                    self.current_player.name,
                    self.current_suspect.name,
                ))

        # Need to cycle through the list of suspects clockwise
        suspect_index = LIST_OF_SUSPECTS.index(self.current_suspect)
        bottom = LIST_OF_SUSPECTS[suspect_index + 1:]
        top = LIST_OF_SUSPECTS[:suspect_index]

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

                log.info('{} ({}) showed {} ({}) "{}"'.format(
                    self.__get_player_mapped_to(suspect).name,
                    suspect.name,
                    self.current_player.name,
                    self.current_suspect.name,
                    random_card
                    ))

                return random_card

    def end_turn(self, force=False):
        self.__valid_board_state()

        if not force:
            # Can only end turn if moved and suggested
            if not self.__state['current_turn']['moved']:
                raise UnfinishedMove('Cannot end turn: {} ({}) must make a move'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

            if not self.__state['current_turn']['suggested']:
                raise UnfinishedMove('Cannot end turn: {} ({}) must make a suggestion'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

        # Reset the turn tracker
        for key in self.__state['current_turn']:
            self.__state['current_turn'][key] = False

        log.info('Ended turn of {} ({})'.format(self.current_player.name, self.current_suspect.name))

        # Check if everyone's out of the game!
        players_status = set([
                self.__get_player_mapped_to(suspect).in_the_game
                for suspect
                in LIST_OF_SUSPECTS
            ])

        if players_status == {False}:
            raise GameOver('No players available. Game Over.')

        # Get the next suspect's player and mark them current
        self.__state['current_player'] = self.__get_player_mapped_to(self.__get_next_suspect())
