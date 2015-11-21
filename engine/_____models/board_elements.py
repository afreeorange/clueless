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
