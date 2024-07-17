# weapon.py
from items import Item

class Weapon(Item):
    def __init__(self, name, description, increase_stat, increase_amount):
        super().__init__(name, "Weapon", description)
        self.increase_stat = increase_stat
        self.increase_amount = increase_amount

    def apply_bonus(self, player):
        if self.increase_stat == "str":
            player.strength += self.increase_amount
        elif self.increase_stat == "int":
            player.intelligence += self.increase_amount
        elif self.increase_stat == "agi":
            player.agility += self.increase_amount
