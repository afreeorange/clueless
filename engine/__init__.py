# Fix the player <-> suspect mess
# Add more properties to check stuff (e.g. current_player shouldn't
# exist until the game is started...)

from .models import (
    Board,
    Player,
    Room,
    Suspect,
    Weapon,
    )


# Logging. Prevent the "No handlers could be found" error
import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
