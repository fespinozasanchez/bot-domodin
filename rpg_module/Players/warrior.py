from sqlalchemy import Column, Integer, ForeignKey
from rpg_module.Players.player import Player

class Warrior(Player):
    __tablename__ = 'warriors'
    
    id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    rage = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'warrior',
    }

    def attack(self):
        return f"{self.name} attacks with rage!"

    def use_special_ability(self):
        return f"{self.name} uses special ability: Berserk!"

    def equip_item(self, item):
        return f"{self.name} has equipped {item.name}"

    def use_item(self, item):
        return f"{self.name} used {item.name}"

    def receive_damage(self, damage):
        self.health -= damage
        return f"{self.name} received {damage} damage"

    def die(self):
        return f"{self.name} has died in battle!"
