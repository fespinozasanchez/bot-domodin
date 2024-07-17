# armor.py
from items import Item

class Armor(Item):
    def __init__(self, name, description, increase_stat, increase_amount):
        super().__init__(name, "Armor", description)
        self.increase_stat = increase_stat
        self.increase_amount = increase_amount

    def apply_bonus(self, player):
        if self.increase_stat == "mana":
            player.mana += self.increase_amount
        elif self.increase_stat == "hp":
            player.health += self.increase_amount
