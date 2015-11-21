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
