from .models import (
    Hallway,
    Room,
    Suspect,
    Weapon,
    )


# Weapons
ROPE = Weapon('rope')
KNIFE = Weapon('knife')
LEAD_PIPE = Weapon('lead pipe')
WRENCH = Weapon('wrench')
REVOLVER = Weapon('revolver')
CANDLESTICK = Weapon('candlestick')

LIST_OF_WEAPONS = [
    ROPE,
    KNIFE,
    LEAD_PIPE,
    WRENCH,
    REVOLVER,
    CANDLESTICK
    ]

# Suspects
SCARLET = Suspect('Miss Scarlet')
MUSTARD = Suspect('Colonel Mustard')
WHITE = Suspect('Mrs. White')
GREEN = Suspect('Mr. Green')
PEACOCK = Suspect('Mrs. Peacock')
PLUM = Suspect('Professor Plum')

LIST_OF_SUSPECTS = [
    SCARLET,
    MUSTARD,
    WHITE,
    GREEN,
    PEACOCK,
    PLUM,
    ]

# Spaces

# Rooms
STUDY = Room('The Study')
HALL = Room('The Hall')
LOUNGE = Room('The Lounge')
LIBRARY = Room('The Library')
BILLIARD_ROOM = Room('The Billiard Room')
DINING_ROOM = Room('The Dining Room')
CONSERVATORY = Room('The Conservatory')
BALLROOM = Room('The Ballroom')
KITCHEN = Room('The Kitchen')

# Hallways
STUDY_TO_HALL = Hallway('The Study to Hall Hallway')
HALL_TO_LOUNGE = Hallway('The Hall to Lounge Hallway')
STUDY_TO_LIBRARY = Hallway('The Study to Library Hallway')
HALL_TO_BILLIARD = Hallway('The Hall to Billiard Room Hallway')
LOUNGE_TO_DINING = Hallway('The Lounge to Dining Room Hallway')
LIBRARY_TO_BILLIARD = Hallway('The Library to Billiard Room Hallway')
BILLIARD_TO_DINING = Hallway('The Billiard Room to Dining Room Hallway')
LIBRARY_TO_CONSERVATORY = Hallway('The Library to Conservatory Hallway')
BILLIARD_TO_BALLROOM = Hallway('The Billiard Room to Ballroom Hallway')
DINING_TO_KITCHEN = Hallway('The Dining Room to Kitchen Hallway')
CONSERVATORY_TO_BALLROOM = Hallway('The Conservatory to Ballroom Hallway')
BALLROOM_TO_KITCHEN = Hallway('The Ballroom to Kitchen Hallway')

# Define the spaces a little more
STUDY.has_secret_passageway = True
STUDY.passage_way_to = KITCHEN

LOUNGE.has_secret_passageway = True
LOUNGE.passage_way_to = CONSERVATORY

CONSERVATORY.has_secret_passageway = True
CONSERVATORY.passage_way_to = LOUNGE

KITCHEN.has_secret_passageway = True
KITCHEN.passage_way_to = STUDY

# Add suspects to the spaces
HALL_TO_LOUNGE.suspects_present = [SCARLET]
STUDY_TO_LIBRARY.suspects_present = [PLUM]
LOUNGE_TO_DINING.suspects_present = [MUSTARD]
LIBRARY_TO_CONSERVATORY.suspects_present = [PEACOCK]
CONSERVATORY_TO_BALLROOM.suspects_present = [GREEN]
BALLROOM_TO_KITCHEN.suspects_present = [WHITE]

LIST_OF_ROOMS = [
    STUDY,
    HALL,
    LOUNGE,
    LIBRARY,
    BILLIARD_ROOM,
    DINING_ROOM,
    CONSERVATORY,
    BALLROOM,
    KITCHEN
    ]

LIST_OF_HALLWAYS = [
    STUDY_TO_HALL,
    HALL_TO_LOUNGE,
    STUDY_TO_LIBRARY,
    HALL_TO_BILLIARD,
    LOUNGE_TO_DINING,
    LIBRARY_TO_BILLIARD,
    BILLIARD_TO_DINING,
    LIBRARY_TO_CONSERVATORY,
    BILLIARD_TO_BALLROOM,
    DINING_TO_KITCHEN,
    CONSERVATORY_TO_BALLROOM,
    BALLROOM_TO_KITCHEN
    ]

LIST_OF_SPACES = LIST_OF_ROOMS + LIST_OF_HALLWAYS

# Make a deck
GAME_DECK = LIST_OF_WEAPONS + list(LIST_OF_SUSPECTS) + LIST_OF_ROOMS
