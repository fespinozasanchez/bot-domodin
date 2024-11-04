from sqlalchemy import Column, Integer, ForeignKey
from rpg_module.Players.player import Player
import math

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
    

    def get_player_damage(self, player: Player):
            """Calcula el daño que un jugador hace al jefe."""
            a = 0.7  # Factor de crecimiento cuadrático reducido
            b = 0.5  # Factor de crecimiento lineal reducido
            c = 1  # Ajuste del daño base

            # Daño base usando logaritmo para controlar el crecimiento del nivel
            base_damage = a * math.log(player.level + 1) + b * player.level + c

            # Ajuste según clase y estadísticas del jugador
            if player.class_player == 'warrior':
                stat_modifier = a * math.log(player.strength + 1) + b * player.strength + c
            elif player.class_player == 'mage':
                stat_modifier = a * math.log(player.intelligence + 1) + b * player.intelligence + c
            elif player.class_player == 'thieve':
                stat_modifier = a * math.log(player.agility + 1) + b * player.agility + c
            else:
                raise ValueError("Clase de jugador no válida.")

            # Daño final aplicando el modificador de estadísticas
            final_damage = base_damage * stat_modifier

            # Limitar el daño final para evitar valores extremadamente altos
            final_damage = min(final_damage, 1000)  # Limitar el daño máximo a 1000 (puedes ajustar esto)

            return round(final_damage)