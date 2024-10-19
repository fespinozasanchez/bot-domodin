from sqlalchemy import Column, Integer,ForeignKey
from rpg_module.Players.player import Player

class Thieve(Player):
    __tablename__ = 'thieves'
    
    id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    stealth = Column(Integer, default=50)

    __mapper_args__ = {
        'polymorphic_identity': 'thieve',
    }
    def attack(self):
        return f"{self.name} performs a stealth attack!"

    def use_special_ability(self):
        return f"{self.name} uses special ability: Backstab!"

    def equip_item(self, item):
        return f"{self.name} has equipped {item.name}"

    def use_item(self, item):
        return f"{self.name} used {item.name}"

    def receive_damage(self, damage):
        self.health -= damage
        return f"{self.name} received {damage} damage"

    def die(self):
        return f"{self.name} has died silently in the shadows!"
