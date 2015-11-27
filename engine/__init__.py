from .models import (
    Board,
    Player,
    Room,
    Suspect,
    Weapon,
    )


import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):

        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
