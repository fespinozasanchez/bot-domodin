from sqlalchemy import Column, Integer, ForeignKey
from rpg_module.Players.player import Player

class Mage(Player):
    __tablename__ = 'mages'
    
    id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    magic_power = Column(Integer, default=50)

    __mapper_args__ = {
        'polymorphic_identity': 'mage',
    }

    def attack(self):
        return f"{self.name} casts a magical attack!"

    def use_special_ability(self):
        return f"{self.name} uses special ability: Fireball!"

    def equip_item(self, item):
        return f"{self.name} has equipped {item.name}"

    def use_item(self, item):
        return f"{self.name} used {item.name}"

    def receive_damage(self, damage):
        self.health -= damage
        return f"{self.name} received {damage} damage"

    def die(self):
        return f"{self.name} has perished in a magical duel!"