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
                return f"{self.player.name} ha derrotado al {self.enemy.name}!, {self.get_stat_gain_message()}"
            elif result == "enemy_wins":
                damage = round(self.player.health*0.3)
                self.player.health = max(0, self.player.health - damage)
                self.penalize_defeat_points()
                session.commit()
                return f"{self.enemy.name} ha derrotado a {self.player.name}. {self.player.name} tiene {self.player.health} de salud restante. {self.get_stat_loss_message()}"
            else:
                return "El combate terminó en un empate. No se ganaron ni perdieron puntos de experiencia."
        except Exception as e:
            session.rollback()
            return f"Ocurrió un error durante el combate: {str(e)}"

    def run(self):
        damage_taken=round(self.enemy.damage*0.20)
        #chance del 30% de huir
        if random.random() < 0.30:
            return [True,f"{self.player.name} ha decidido huir del combate contra el {self.enemy.name}."]
        else:
            self.player.health = max(0, self.player.health - damage_taken)
            session.commit()
            return [False,f" El {self.enemy.name} ha sido mas astuto que tú y te ha hecho {damage_taken} puntos de daño!."]

    def simulate_combat(self):
        # Lógica simplificada para determinar el resultado del combate
        if self.player.class_player == 'warrior':
            player_attack = self.get_player_damage('warrior')
        elif self.player.class_player == 'mage':
            player_attack = self.get_player_damage('mage')
        elif self.player.class_player == 'thieve':
            player_attack = self.get_player_damage('thieve')
        else:
            raise ValueError("Clase de jugador no válida.")
        enemy_attack = self.enemy.damage

        if player_attack > enemy_attack:
            return "player_wins"
        elif enemy_attack > player_attack:
            return "enemy_wins"
        else:
            return "draw"

    def award_victory_points(self):
        points_gained = self.enemy.experience
        self.player.experience += points_gained
        session.commit()

    def penalize_defeat_points(self):
        points_to_lose = round(self.enemy.experience*0.2)
        self.player.experience = max(0, self.player.experience - points_to_lose)
        session.commit()

    def get_stat_gain_message(self):
        points_gained = self.enemy.experience
        return f"Has ganado {points_gained} puntos de experiencia!"

    def get_stat_loss_message(self):
        points_to_lose = round(self.enemy.experience*0.2)
        return f"Has perdido {points_to_lose} puntos de experiencia."


    def get_player_damage(self, class_name):
        a = 2  # Factor de crecimiento cuadrático
        b = 3  # Factor de crecimiento lineal
        c = 1  # Daño base

        # Daño base, escalado con el nivel del jugador
        base_damage = a * (self.player.level ** 1.5) + b * self.player.level + c  # Menos agresivo que el cuadrático

        # Ajuste según clase y estadísticas del jugador
        if class_name == 'warrior':
            # Usamos raíz cuadrada para controlar el crecimiento de los experiencia
            stat_modifier = (a * (self.player.strength ** 0.5) + b * self.player.strength + c)
        elif class_name == 'mage':
            # Similar para el mago, basado en inteligencia
            stat_modifier = (a * (self.player.intelligence ** 0.5) + b * self.player.intelligence + c)
        elif class_name == 'thieve':
            # El ladrón se basa en agilidad
            stat_modifier = (a * (self.player.agility ** 0.5) + b * self.player.agility + c)
        else:
            raise ValueError("Clase de jugador no válida.")

        # Evitamos un crecimiento descontrolado del daño aplicando un escalado logarítmico
        final_damage = base_damage * stat_modifier
        return round(final_damage)
        


 