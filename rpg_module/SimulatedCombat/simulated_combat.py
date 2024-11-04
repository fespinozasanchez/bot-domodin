import random
import math
from rpg_module.Players.player import Player
from rpg_module.Enemy.enemy import Enemy
from rpg_module.rpg_utils.rpg_data_manager import session
from rpg_module.Enemy import enemy_const

class SimulatedCombat:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.combat_log = []

    def fight(self):
        try:
            # Simular combate
            result = self.simulate_combat()

            if result == "player_wins":
                self.enemy.health = 0
                session.commit()
                self.award_victory_points()
                # Convertir el log de combate en un solo string con saltos de línea
                return '\n'.join(self.combat_log)
            elif result == "enemy_wins":
                damage = round(self.player.current_health * 0.3)
                self.player.current_health = max(0, self.player.current_health - damage)
                self.penalize_defeat_points()
                session.commit()
                # Convertir el log de combate en un solo string con saltos de línea
                return '\n'.join(self.combat_log)
            else:
                return "El combate terminó en un empate. No se ganaron ni perdieron puntos de experiencia."
        except Exception as e:
            session.rollback()
            return f"Ocurrió un error durante el combate: {str(e)}"


    def run(self):
        damage_taken = round(self.enemy.damage * 0.01)
        damage_reduction = round(round(self.player.defense * 0.1)*damage_taken)
        # Chance del 30% de huir
        if random.random() < 0.30:
            return [True, f"{self.player.name} ha decidido huir del combate contra el {self.enemy.name}."]
        else:
            self.player.current_health = max(0, self.player.current_health - damage_reduction)
            session.commit()
            return [False, f"El {self.enemy.name} ha sido más astuto que tú y te ha hecho {damage_reduction} puntos de daño!."]

    def simulate_combat(self):
        # Determinar quién ataca primero
        first_attacker = self.determine_first_attacker()
        player_attack = self.get_player_damage(self.player.class_player)
        enemy_attack = self.enemy.damage
        # Combate por turnos
        if first_attacker == 'player':
            if player_attack*1.3 > enemy_attack:
                self.combat_log.append(f"{self.player.name} ha derrotado al {self.enemy.name}.")
                self.combat_log.append(self.get_stat_gain_message())
                return "player_wins"
            else:
                self.combat_log.append(f"{self.enemy.name} ha derrotado a {self.player.name}.")
                self.combat_log.append(f"{self.player.name} tiene {self.player.current_health} de salud restante.")
                self.combat_log.append(self.get_stat_loss_message())
                return "enemy_wins"
        else:
            if enemy_attack > player_attack:
                self.combat_log.append(f"{self.enemy.name} ha derrotado a {self.player.name}.")
                self.combat_log.append(f"{self.player.name} tiene {self.player.current_health - round(self.player.current_health * 0.3)} de salud restante.")
                self.combat_log.append(self.get_stat_loss_message())
                return "enemy_wins"
            else:
                self.combat_log.append(f"{self.player.name} ha derrotado al {self.enemy.name}.")
                self.combat_log.append(self.get_stat_gain_message())
                return "player_wins"

    def determine_first_attacker(self):
        """Determina quién ataca primero basado en la evasión del jugador y la diferencia de niveles."""
        level_diff = self.player.level - self.enemy.level

        # Ajustamos la evasión del jugador en función de la diferencia de nivel
        if level_diff > 0:
            player_chance = (self.player.evasion + (level_diff * 2)) / (self.player.evasion + abs(level_diff) * 2)
        else:
            player_chance = self.player.evasion / (self.player.evasion + abs(level_diff) * 2)

        # El enemigo no tiene evasión, por lo que la probabilidad de que el jugador ataque primero es solo relativa a la evasión del jugador.
        if random.random() < player_chance:
            self.combat_log.append(f"{self.player.name} ataca primero gracias a su evasión.")
            return 'player'
        else:
            self.combat_log.append(f"{self.enemy.name} ataca primero.")
            return 'enemy'

    def award_victory_points(self):
        level_diff = self.enemy.level - self.player.level
        percent_change = abs(level_diff) * 0.1  
        if level_diff > 0:
            points_gained = self.enemy.experience * (1 + percent_change)
        else:
            points_gained = self.enemy.experience * (1 - percent_change)
        self.player.experience += int(points_gained)
        session.commit()


    def penalize_defeat_points(self):
        points_to_lose = round(self.enemy.experience * 0.2)
        self.player.experience = max(0, self.player.experience - points_to_lose)
        session.commit()

    def get_stat_gain_message(self):
        level_diff = self.enemy.level - self.player.level
        percent_change = abs(level_diff) * 0.1
        if level_diff > 0:
            points_gained = self.enemy.experience * (1 + percent_change)
        else:
            points_gained = self.enemy.experience * (1 - percent_change)
        return f"Has ganado {points_gained} puntos de experiencia!"

    def get_stat_loss_message(self):
        points_to_lose = round(self.enemy.experience * 0.2)
        return f"Has perdido {points_to_lose} puntos de experiencia."

    def get_player_damage(self, class_name):
        a = 0.7  # Factor de crecimiento cuadrático reducido
        b = 0.5  # Factor de crecimiento lineal reducido
        c = 1  # Ajuste del daño base

        # Daño base usando logaritmo para controlar el crecimiento del nivel
        base_damage = a * math.log(self.player.level + 1) + b * self.player.level + c

        # Ajuste según clase y estadísticas del jugador, aplicando logaritmo a las estadísticas
        if class_name == 'warrior':
            stat_modifier = a * math.log(self.player.strength + 1) + b * self.player.strength + c
        elif class_name == 'mage':
            stat_modifier = a * math.log(self.player.intelligence + 1) + b * self.player.intelligence + c
        elif class_name == 'thieve':
            stat_modifier = a * math.log(self.player.agility + 1) + b * self.player.agility + c
        else:
            raise ValueError("Clase de jugador no válida.")

        # Daño final aplicando el modificador de estadísticas
        final_damage = base_damage * stat_modifier

        # Limitar el daño final para evitar valores extremadamente altos
        final_damage = min(final_damage, 1000)  # Limitar el daño máximo a 1000 (puedes ajustar esto)

        return round(final_damage)
