class Enemy:
    def __init__(self, type, level, health):
        self.type = type
        self.level = level
        self.health = health

    def attack(self, target):
        pass

    def defend(self):
        pass