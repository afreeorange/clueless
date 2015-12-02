from datetime import datetime
from itertools import cycle
import logging
import random
from uuid import uuid4

from .exceptions import (
    BadSuggestion,
    BlockedSpace,
    BoardIsFull,
    CardsAlreadyDealt,
    GameOver,
    InsufficientPlayers,
    InvalidHallway,
    InvalidPlayer,
    InvalidPlayerName,
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
        self.__suspect = suspect
        self.__cards = []

        # Keep a list of all suggestions
        self.__suggestions = []

        # Keep track of suggestions and disproves. Start with True
        # since every board entity might be involved in... MURDER!
        # This is now set by the Board
        self.game_sheet = {}

        self.in_the_game = True
        self.board = None
        self.turn = {
                'moved': False,
                'suggested': False,
                'accused': False
            }

    @property
    def cards(self):
        return self.__cards

    @cards.setter
    def cards(self, cards):
        if self.__cards:
            raise CardsAlreadyDealt('Cards have been dealt to this player')
        self.__cards = cards
        for card in cards:
            self.game_sheet[card] = False

    @property
    def suggestion(self):
        return self.__suggestions[-1] if self.__suggestions else []

    @property
    def suggestions(self):
        return self.__suggestions

    @property
    def all_suggestions(self):
        return self.__all_suggestions

    def update_suggestions(self, suggestion, disprove):
        self.__suggestions.append({
                'suggestion': suggestion,
                'disprove': disprove
            })

    @property
    def suspect(self):
        return self.__suspect

    @property
    def name(self):
        return self.__name

    def update_game_sheet(self, card):
        self.game_sheet[card] = False


class Board:

    def __init__(self):

        # Weapons
        self.ROPE = Weapon('Rope')
        self.KNIFE = Weapon('Knife')
        self.LEAD_PIPE = Weapon('Lead Pipe')
        self.WRENCH = Weapon('Wrench')
        self.REVOLVER = Weapon('Revolver')
        self.CANDLESTICK = Weapon('Candlestick')
        self.LIST_OF_WEAPONS = [
            self.ROPE,
            self.KNIFE,
            self.LEAD_PIPE,
            self.WRENCH,
            self.REVOLVER,
            self.CANDLESTICK
            ]

        # Suspects
        self.SCARLET = Suspect('Miss Scarlet')
        self.MUSTARD = Suspect('Colonel Mustard')
        self.WHITE = Suspect('Mrs. White')
        self.GREEN = Suspect('Mr. Green')
        self.PEACOCK = Suspect('Mrs. Peacock')
        self.PLUM = Suspect('Professor Plum')

        self.LIST_OF_SUSPECTS = [
            self.SCARLET,
            self.MUSTARD,
            self.WHITE,
            self.GREEN,
            self.PEACOCK,
            self.PLUM,
            ]

        # Rooms
        self.STUDY = Room('The Study')
        self.HALL = Room('The Hall')
        self.LOUNGE = Room('The Lounge')
        self.LIBRARY = Room('The Library')
        self.BILLIARD_ROOM = Room('The Billiard Room')
        self.DINING_ROOM = Room('The Dining Room')
        self.CONSERVATORY = Room('The Conservatory')
        self.BALLROOM = Room('The Ballroom')
        self.KITCHEN = Room('The Kitchen')

        # Hallways
        self.STUDY_TO_HALL = Hallway('The Study to Hall Hallway')
        self.HALL_TO_LOUNGE = Hallway('The Hall to Lounge Hallway')
        self.STUDY_TO_LIBRARY = Hallway('The Study to Library Hallway')
        self.HALL_TO_BILLIARD = Hallway('The Hall to Billiard Room Hallway')
        self.LOUNGE_TO_DINING = Hallway('The Lounge to Dining Room Hallway')
        self.LIBRARY_TO_BILLIARD = Hallway('The Library to Billiard Room Hallway')
        self.BILLIARD_TO_DINING = Hallway('The Billiard Room to Dining Room Hallway')
        self.LIBRARY_TO_CONSERVATORY = Hallway('The Library to Conservatory Hallway')
        self.BILLIARD_TO_BALLROOM = Hallway('The Billiard Room to Ballroom Hallway')
        self.DINING_TO_KITCHEN = Hallway('The Dining Room to Kitchen Hallway')
        self.CONSERVATORY_TO_BALLROOM = Hallway('The Conservatory to Ballroom Hallway')
        self.BALLROOM_TO_KITCHEN = Hallway('The Ballroom to Kitchen Hallway')

        # Define the spaces a little more
        self.STUDY.has_secret_passageway = True
        self.STUDY.passage_way_to = self.KITCHEN

        self.LOUNGE.has_secret_passageway = True
        self.LOUNGE.passage_way_to = self.CONSERVATORY

        self.CONSERVATORY.has_secret_passageway = True
        self.CONSERVATORY.passage_way_to = self.LOUNGE

        self.KITCHEN.has_secret_passageway = True
        self.KITCHEN.passage_way_to = self.STUDY

        # Add suspects to the spaces
        self.HALL_TO_LOUNGE.suspects_present = [self.SCARLET]
        self.STUDY_TO_LIBRARY.suspects_present = [self.PLUM]
        self.LOUNGE_TO_DINING.suspects_present = [self.MUSTARD]
        self.LIBRARY_TO_CONSERVATORY.suspects_present = [self.PEACOCK]
        self.CONSERVATORY_TO_BALLROOM.suspects_present = [self.GREEN]
        self.BALLROOM_TO_KITCHEN.suspects_present = [self.WHITE]

        self.LIST_OF_ROOMS = [
            self.STUDY,
            self.HALL,
            self.LOUNGE,
            self.LIBRARY,
            self.BILLIARD_ROOM,
            self.DINING_ROOM,
            self.CONSERVATORY,
            self.BALLROOM,
            self.KITCHEN,
            ]

        self.LIST_OF_HALLWAYS = [
            self.STUDY_TO_HALL,
            self.HALL_TO_LOUNGE,
            self.STUDY_TO_LIBRARY,
            self.HALL_TO_BILLIARD,
            self.LOUNGE_TO_DINING,
            self.LIBRARY_TO_BILLIARD,
            self.BILLIARD_TO_DINING,
            self.LIBRARY_TO_CONSERVATORY,
            self.BILLIARD_TO_BALLROOM,
            self.DINING_TO_KITCHEN,
            self.CONSERVATORY_TO_BALLROOM,
            self.BALLROOM_TO_KITCHEN,
            ]

        self.LIST_OF_SPACES = self.LIST_OF_ROOMS + self.LIST_OF_HALLWAYS

        # Make a deck
        self.GAME_DECK = self.LIST_OF_WEAPONS + list(self.LIST_OF_SUSPECTS) + self.LIST_OF_ROOMS

        self.id = uuid4()
        self.__game_started = False
        self.__time_started = None

        # The Board is a 5x5 grid with four holes.
        self.__map = [
                [
                    self.STUDY,
                    self.STUDY_TO_HALL,
                    self.HALL,
                    self.HALL_TO_LOUNGE,
                    self.LOUNGE
                ],
                [
                    self.STUDY_TO_LIBRARY,
                    None,
                    self.HALL_TO_BILLIARD,
                    None,
                    self.LOUNGE_TO_DINING
                ],
                [
                    self.LIBRARY,
                    self.LIBRARY_TO_BILLIARD,
                    self.BILLIARD_ROOM,
                    self.BILLIARD_TO_DINING,
                    self.DINING_ROOM
                ],
                [
                    self.LIBRARY_TO_CONSERVATORY,
                    None,
                    self.BILLIARD_TO_BALLROOM,
                    None,
                    self.DINING_TO_KITCHEN
                ],
                [
                    self.CONSERVATORY,
                    self.CONSERVATORY_TO_BALLROOM,
                    self.BALLROOM,
                    self.BALLROOM_TO_KITCHEN,
                    self.KITCHEN
                ]
            ]

        # These are the holes in the board
        self.__bad_coordinates = [(1, 1), (1, 3), (3, 1), (3, 3)]

        # These are valid deltas when subtracting coordinates to
        # validate a move between spaces on the board
        self.__valid_coord_deltas = [(1, 0), (0, 1), (-1, 0), (0, -1),
                                     (4, 4), (4, -4), (-4, 4), (-4, -4),
                                     (0, 0)]

        # Create the confidential file
        self.__confidential_file = [
                random.choice(self.LIST_OF_ROOMS),
                random.choice(self.LIST_OF_SUSPECTS),
                random.choice(self.LIST_OF_WEAPONS),
            ]

        # Now that the confidential envelope is set up, shuffle the
        # remaining deck. Make it an iterable so cards can be distributed
        # to players.
        self.__deck = [card for card in self.GAME_DECK
                       if card not in self.__confidential_file]
        random.shuffle(self.__deck)
        self.__deck = iter(self.__deck)

        # Maintain a map of Suspect objects to Player objects
        self.__suspect_to_player_map = dict.fromkeys(self.LIST_OF_SUSPECTS, None)

        # Initialize the current player. This will be set once all suspects
        # are bound to players. Setting this means that the game has begun
        self.__current_player = None

        # "GAME _OVER_, MAN :'("
        self.__game_over = False

        # Winner of the game
        self.__winner = None

        # Use to yield the next player
        self.__suspect_looper = cycle(self.LIST_OF_SUSPECTS)

        # Initialize a logger
        self.log = logging.getLogger(__name__)
        self.log.debug('Started game')
        self.log.debug('Confidential file contains "{}"'.format(
                    '", "'.join([_.name for _ in self.confidential_file])
                    ))

    # ------ Board Actions ------

    def add_player(self, player):
        if not player.name or not player.name.strip():
            raise InvalidPlayerName('Player name not specified')

        if self.__cannot_add_more_players():
            raise BoardIsFull('All players mapped to suspects on this board')

        if self.__suspect_to_player_map[player.suspect]:
            raise PlayerAlreadyMappedToSuspect('Player already mapped to suspect: {} <-> {}'.format(
                            self.__suspect_to_player_map[player.suspect].name,
                            player.suspect.name
                        ))

        self.__suspect_to_player_map[player.suspect] = player
        self.deal_cards_to(player)
        player.game_sheet = {_: True for _ in self.GAME_DECK}
        for _ in player.cards:
            player.game_sheet[_] = False

        self.log.info('Added player {} as {}'.format(
                player.name,
                player.suspect.name
            ))

        # If this is the last player, start the game
        # The first suspect returned is scarlet
        if self.__cannot_add_more_players():
            self.__game_started = True
            self.__time_started = '{}Z'.format(str(datetime.utcnow().isoformat()))
            self.current_player = self.get_player_mapped_to(self.__get_next_suspect())

        return player

    def __cannot_add_more_players(self):
        if None in set(self.__suspect_to_player_map.values()):
            return False
        return True

    def move_player(self, player, space=None):
        self.__valid_board_state()
        self.__valid_player(player)
        self.__valid_player_turn(player)
        self.__valid_space(space)

        # Update the turn. Throw an error if player already made a move
        if player.turn['moved']:
            raise MoveCompleted('{} ({}) has already moved'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

        old_space = [_
                     for _ in self.LIST_OF_SPACES
                     if player.suspect in _.suspects_present
                     ][0]
        new_space = old_space if not space else space

        self.__valid_target_space(player, old_space, new_space)

        old_space.remove_suspect(player.suspect)
        new_space.add_suspect(player.suspect)

        player.turn['moved'] = True

        if old_space == new_space:
            self.log.info('{} ({}) stayed in {}'.format(
                    player.name,
                    player.suspect.name,
                    old_space.name
                ))
        else:
            self.log.info('{} ({}) moved from {} to {}'.format(
                    player.name,
                    player.suspect.name,
                    old_space.name,
                    new_space.name
                ))

    def make_suggestion(self, player, suspect, weapon):
        self.__valid_board_state()
        self.__valid_player(player)
        self.__valid_player_turn(player)
        self.__valid_suspect(suspect)
        self.__valid_weapon(weapon)
        self.__valid_space_for_suggestion()

        suspect_space = self.__get_space_for(suspect)
        player_room = self.__get_space_for(player)

        # Update the turn. Throw an error if player already made a suggestion
        if player.turn['suggested']:
            raise MoveCompleted('{} ({}) has already made a suggestion'.format(
                        self.current_player.name,
                        self.current_suspect.name
                    ))

        if suspect in player.cards or weapon in player.cards:
            raise BadSuggestion('Look at your cards, yo...')

        player.turn['suggested'] = True

        suggestion = {
                'weapon': weapon,
                'suspect': suspect,
                'room': player_room,
            }
        disprove = None

        self.log.info('{} ({}) suggested that {} ({}) did it with a {} in {}'.format(
                    player.name,
                    player.suspect.name,
                    self.get_player_mapped_to(suspect).name,
                    suspect.name,
                    weapon.name,
                    player_room.name
                ))

        # First move the suspect into the player's space
        # if the player is active
        if self.get_player_mapped_to(suspect).in_the_game:
            suspect_space.remove_suspect(suspect)
            player_room.add_suspect(suspect)

            self.log.info('{} ({}) moved from {} to {}'.format(
                        self.get_player_mapped_to(suspect).name,
                        suspect.name,
                        suspect_space.name,
                        player_room.name
                        ))

        # End the game if the suggestion is in the game file
        if [player_room, suspect, weapon] == self.__confidential_file:
            self.__game_over = True
            self.__winner = player
            disprove = None

            self.log.info('{} ({})\'s suggestion was correct. Game Over!'.format(
                        player.name,
                        player.suspect.name
                    ))
        else:
            disprove_player, suspect, card = self.disprove_suggestion(player, suggestion)
            disprove = {
                'suspect': suspect,
                'player': disprove_player,
                'card': card,
            }

        player.update_suggestions(suggestion, disprove)

        return True

    def disprove_suggestion(self, player, suggestion):
        self.__valid_board_state()
        self.__valid_player(player)
        self.__valid_player_turn(player)

        if not player.turn['suggested']:
            raise UnfinishedMove('{} ({}) must make a suggestion before getting a card to disprove it'.format(
                    player.name,
                    player.suspect.name,
                ))

        # Need to cycle through the list of suspects clockwise
        suspect_index = self.LIST_OF_SUSPECTS.index(self.current_suspect)
        bottom = self.LIST_OF_SUSPECTS[suspect_index + 1:]
        top = self.LIST_OF_SUSPECTS[:suspect_index]

        our_suggestion = suggestion.values()

        for suspect in bottom + top:
            their_cards = self.get_player_mapped_to(suspect).cards

            # Cast to list because, for some reason,
            # 'if not common_cards' doesn't work :/
            common_cards = list(set(their_cards) & set(our_suggestion))

            # If the next player has card(s) to disprove the suggestion,
            # pick one and return it
            if common_cards:
                random_card = random.choice(common_cards)

                self.log.debug('{} ({}) showed {} ({}) "{}"'.format(
                        self.get_player_mapped_to(suspect).name,
                        suspect.name,
                        player.name,
                        player.suspect.name,
                        random_card.name
                    ))

                player.update_game_sheet(random_card)

                return (self.get_player_mapped_to(suspect),
                        suspect,
                        random_card
                        )

    def make_accusation(self, player, suspect, weapon, room=None):
        '''
        * Players can make accusation any time. No need to move or
          suggest beforehand.
        * Player is out of game if the accusation is incorrect.
        * The game ends if the accusation is correct.
        '''
        self.__valid_board_state()
        self.__valid_player(player)
        self.__valid_player_turn(player)
        self.__valid_suspect(suspect)
        self.__valid_weapon(weapon)

        if room:
            self.__valid_room(room)
            player_room = room
        else:
            player_room = self.__get_space_for(player)

        self.log.info('{} ({}) accused {} ({}) of murder with a {} in {}'.format(
                    player.name,
                    player.suspect.name,
                    self.get_player_mapped_to(suspect).name,
                    suspect.name,
                    weapon.name,
                    player_room.name
                ))

        # End the game if the accusation is in the game file
        if [player_room, suspect, weapon] == self.__confidential_file:
            self.__game_over = True
            self.__winner = player
            self.log.info('{} ({})\'s accusation was correct. Game Over!'.format(
                        player.name,
                        player.suspect.name
                    ))

        # Kick the player out of the game if incorrect
        else:
            player.in_the_game = False
            self.log.info('{} ({}) is now out of the game due to a wrong accusation'.format(
                        player.name,
                        player.suspect.name,
                    ))
            self.end_turn(player, force=True)

        return True

    def end_turn(self, player, force=False):
        self.__valid_board_state()
        self.__valid_player(player)
        self.__valid_player_turn(player)

        if not force:
            # Can only end turn if moved
            if not player.turn['moved']:
                raise UnfinishedMove('Cannot end turn: {} ({}) must make a move'.format(
                        player.name,
                        player.suspect.name
                    ))

            # if not player.turn['suggested']:
            #     raise UnfinishedMove('Cannot end turn: {} ({}) must make a suggestion'.format(
            #             player.name,
            #             player.suspect.name
            #         ))

        # Reset the turn tracker
        for key in player.turn:
            player.turn[key] = False

        self.log.info('{} ({}) ended their turn'.format(self.current_player.name, self.current_suspect.name))

        # Check if everyone's out of the game!
        players_status = set([
                self.get_player_mapped_to(suspect).in_the_game
                for suspect
                in self.LIST_OF_SUSPECTS
            ])

        if players_status == {False}:
            self.__game_over = True
            # self.__winner = player
            message = 'No players available. Game Over.'
            self.log.info(message)
            raise GameOver(message)

        # Get the next suspect's player and mark them current
        self.current_player = self.get_player_mapped_to(self.__get_next_suspect())

    def deal_cards_to(self, player):
        # So this is beautiful:
        # [next(self.__deck)] * 3
        # but it will _replicate_ the elements in the list thrice
        # and won't call __iter__ ! Ha!
        player.cards = [next(self.__deck),
                        next(self.__deck),
                        next(self.__deck)
                        ]

    # ------ Useful helper methods ------

    def __get_next_suspect(self):
        '''
        No guard to see if the game's ended: This will keep looping!
        '''
        while True:
            next_suspect = next(self.__suspect_looper)
            next_player = self.get_player_mapped_to(next_suspect)

            if next_player.in_the_game is False:
                self.log.warning('{} ({}) is not in the game; skipping'.format(
                        next_player.name,
                        next_suspect.name
                    ))
            else:
                return next_suspect

    def get_player_mapped_to(self, suspect):
        for k, v in self.__suspect_to_player_map.items():
            if k == suspect:
                return v
        return None

    def __get_space_for(self, entity):
        suspect = None

        if type(entity) is Suspect:
            suspect = entity
        elif type(entity) is Player:
            suspect = entity.suspect
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
                    for row in self.__map
                ]

                if _
                ][0][0]

    def __get_coordinates_of(self, space):
        return [(i, _.index(space))
                for i, _ in enumerate(self.__map)
                if space in _
                ][0]

    # ------ Validators ------

    def __valid_target_space(self, player, old_space, new_space):
        if new_space in self.__bad_coordinates:
            raise InvalidSpace('Cannot move to holes')

        osc = self.__get_coordinates_of(old_space)
        nsc = self.__get_coordinates_of(new_space)

        # Allow players to stay put
        if osc == nsc:
            return True

        if tuple(x - y for x, y in zip(osc, nsc)) not in self.__valid_coord_deltas:
            raise InvalidTargetSpace(
                'Cannot teleport {} ({}) from {} to {}'.format(
                    player.name,
                    player.suspect.name,
                    old_space.name,
                    new_space.name,
                ))

        suspects_in_space = [
            _
            for _ in new_space.suspects_present
            if _ != player.suspect and _.in_the_game
        ]

        if suspects_in_space:
            raise BlockedSpace(
                    'Cannot move. Suspect(s) blocking {}: {}.'.format(
                        new_space.name,
                        ', '.join([_.name for _ in suspects_in_space])
                    ))

        return True

    def __valid_player(self, player):
        if player not in self.__suspect_to_player_map.values():
            raise InvalidPlayer('Don\'t know this player')

    def __valid_player_turn(self, player):
        current_player = self.current_player

        if player != current_player:
            raise NotPlayersTurn('Turn belongs to {} ({})'.format(
                        current_player.name,
                        self.current_player.suspect.name,
                    ))

        return True

    def __valid_suspect(self, suspect):
        if suspect not in self.LIST_OF_SUSPECTS:
            raise InvalidSuspect('Invalid suspect')

        return True

    def __valid_weapon(self, weapon):
        if weapon not in self.LIST_OF_WEAPONS:
            raise InvalidWeapon('Invalid weapon')

        return True

    def __valid_space(self, space):
        if space not in self.LIST_OF_SPACES:
            raise InvalidSpace('Invalid space')

        return True

    def __valid_room(self, room):
        if room not in self.LIST_OF_ROOMS:
            raise InvalidRoom('Invalid room')

        return True

    def __valid_hallway(self, hallway):
        if hallway not in self.LIST_OF_HALLWAYS:
            raise InvalidHallway('Invalid hallway')

        return True

    def __valid_board_state(self):
        if not self.current_player:
            unmapped_suspect_names = [_.name for _ in self.unmapped_suspects]
            raise InsufficientPlayers('Not enough players to start the game. Still waiting for players for {}'.format(
                            ', '.join(unmapped_suspect_names)
                        ))

        if self.__game_over:
            if not self.__winner:
                raise GameOver('Game over. There were no winners :/')
            else:
                raise GameOver('{} ({}) has won the game'.format(
                            self.current_player.name,
                            self.current_suspect.name
                        ))

        return True

    def __valid_space_for_suggestion(self):
        '''
        Player must be in a room to make a suggestion
        '''
        space = self.__get_space_for(self.current_player)
        if type(space) is not Room:
            raise InvalidSpaceForSuggestion(
                        '{} ({}) must be in a room to '
                        'suggest; currently in {}'.format(
                            self.current_player.name,
                            self.current_suspect.name,
                            space.name
                        ))

    # ------ 'Public' properties ------

    @property
    def confidential_file(self):
        return self.__confidential_file

    @property
    def current_player(self):
        return self.__current_player

    @current_player.setter
    def current_player(self, player):
        self.__current_player = player

    @property
    def current_suspect(self):
        return self.current_player.suspect

    @property
    def unmapped_suspects(self):
        return [k
                for k, v in self.__suspect_to_player_map.items()
                if v is None
                ]

    @property
    def suspect_to_player_map(self):
        return self.__suspect_to_player_map

    @property
    def map(self):
        return self.__map

    @property
    def game_started(self):
        return self.__game_started

    @property
    def game_over(self):
        return self.__game_over

    @property
    def winner(self):
        return self.__winner

    @property
    def time_started(self):
        return self.__time_started
