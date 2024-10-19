import random
from rpg_module.Players.player import Player
from rpg_module.Enemy.enemy import Enemy
from rpg_module.rpg_utils.rpg_data_manager import session
from rpg_module.Enemy import enemy_const

class SimulatedCombat:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy

    def fight(self):
        try:
            # Simular combate
            result = self.simulate_combat()

            if result == "player_wins":
                self.enemy.health = 0
                session.commit()
                self.award_victory_points()
                return f"{self.player.name} ha derrotado al {self.enemy.name}! {self.get_stat_gain_message()}"
            elif result == "enemy_wins":
                damage = random.randint(10, 30)
                self.player.health = max(0, self.player.health - damage)
                self.penalize_defeat_points()
                session.commit()
                return f"{self.enemy.name} ha derrotado a {self.player.name}. {self.player.name} tiene {self.player.health} de salud restante. {self.get_stat_loss_message()}"
            else:
                return "El combate terminó en un empate. No se ganaron ni perdieron puntos de stats."
        except Exception as e:
            session.rollback()
            return f"Ocurrió un error durante el combate: {str(e)}"

    def run(self):
        return f"{self.player.name} ha decidido huir del combate contra el {self.enemy.name}."

    def simulate_combat(self):
        # Lógica simplificada para determinar el resultado del combate
        player_attack = self.player.strength + random.randint(0, 20)
        enemy_attack = self.enemy.damage + random.randint(0, 20)

        if player_attack > enemy_attack:
            return "player_wins"
        elif enemy_attack > player_attack:
            return "enemy_wins"
        else:
            return "draw"

    def award_victory_points(self):
        # Ganar 3 puntos base de stats, amplificados por el tier del enemigo
        tier_multiplier = enemy_const.TIERS.get(self.enemy.tier, 1)
        points_to_gain = max(1, int(3 * (1 + tier_multiplier)))  
        self.player.stats_points += points_to_gain
        session.commit()

    def penalize_defeat_points(self):
        # Perder 3 puntos de stats
        points_to_lose = 3
        self.player.stats_points = max(0, self.player.stats_points - points_to_lose)
        session.commit()

    def get_stat_gain_message(self):
        tier_multiplier = enemy_const.TIERS.get(self.enemy.tier, 1)
        points_gained = max(1, int(3 * (1 + tier_multiplier)))
        return f"Has ganado {points_gained} puntos de stats!"

    def get_stat_loss_message(self):
        return "Has perdido 3 puntos de stats."
