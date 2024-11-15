import random
import math
from rpg_module.Players.player import Player
from rpg_module.Enemy.enemy import Enemy
from rpg_module.Enemy.boss_enemy import BossEnemy
from rpg_module.rpg_utils.rpg_data_manager import session


class SimulatedBossCombat:
    def __init__(self, players: list[Player], boss: BossEnemy):
        self.players = players
        self.boss = boss
        self.combat_log = []
        self.defeated_players = []
        self.players_damage= self.calculate_total_player_damage()




    def calculate_total_player_damage(self):
        return sum(player.get_player_damage(player) for player in self.players)



    def fight(self):
        """Simula el combate de un grupo de jugadores contra el jefe."""
        try:
            self.combat_log.append(f"🔰 **Combate contra el jefe {self.boss.name} (Salud: {self.boss.health})**")
            self.combat_log.append(f"👥 Jugadores en el combate: {', '.join([player.name for player in self.players])}\n")

            for player in self.players:
                if player in self.defeated_players:
                    continue  # Saltar jugadores ya derrotados (por si acaso)

                self.combat_log.append(f"⚔️ **{player.name}** entra en combate contra el jefe **{self.boss.name}**.")

                # Mientras el jugador y el jefe estén vivos
                while player.current_health > 0 and self.boss.health > 0:
                    # Turno del jugador
                    player_attack = player.get_player_damage(player)
                    self.boss.health = max(self.boss.health - player_attack, 0)
                    self.combat_log.append(
                        f"🔸 **{player.name}** ataca al jefe causando **{player_attack}** de daño. Salud restante del jefe: **{self.boss.health}**."
                    )

                    # Verificar si el jefe ha sido derrotado
                    if self.boss.health <= 0:
                        self.combat_log.append(f"🏆 ¡El jefe **{self.boss.name}** ha sido derrotado por **{player.name}**!")
                        self.award_victory_points()
                        session.commit()
                        return '\n'.join(self.combat_log)

                    # Turno del jefe
                    boss_attack = round(self.boss.damage*0.5)
                    player.current_health = max(player.current_health - boss_attack, 0)
                    self.combat_log.append(
                        f"🔹 El jefe **{self.boss.name}** ataca a **{player.name}** causando **{boss_attack}** de daño. Salud restante de {player.name}: **{player.current_health}**."
                    )

                    # Verificar si el jugador ha sido derrotado
                    if player.current_health <= 0:
                        self.defeated_players.append(player)
                        self.combat_log.append(f"💀 **{player.name}** ha sido derrotado por el jefe **{self.boss.name}**.\n")
                        break  # Salir del bucle while para pasar al siguiente jugador

                # Verificar si el jefe ha sido derrotado después del combate con el jugador actual
                if self.boss.health <= 0:
                    self.combat_log.append(f"🏆 ¡El jefe **{self.boss.name}** ha sido derrotado!")
                    self.award_victory_points()
                    session.commit()
                    return '\n'.join(self.combat_log)

            # Si se han recorrido todos los jugadores y el jefe sigue vivo
            if self.boss.health > 0:
                self.combat_log.append(f"☠️ Todos los jugadores han sido derrotados por el jefe **{self.boss.name}**.")
                self.penalize_defeat_points()
                session.commit()
                return '\n'.join(self.combat_log)

        except Exception as e:
            session.rollback()
            self.combat_log.append(f"❌ Ocurrió un error durante el combate: {str(e)}")
            return '\n'.join(self.combat_log)


  


    def award_victory_points(self):
        """Otorga puntos de victoria a todos los jugadores que hayan sobrevivido."""
        points_gained = self.boss.experience // len(self.players)
        for player in self.players:
            player.experience += points_gained
            self.combat_log.append(f"{player.name} ha ganado {points_gained} puntos de experiencia.")
        session.commit()

    def penalize_defeat_points(self):
        """Penaliza a los jugadores derrotados."""
        points_to_lose = round((self.boss.experience // len(self.players))*0.009)
        for player in self.defeated_players:
            player.experience = max(0, player.experience - points_to_lose)
            self.combat_log.append(f"{player.name} ha perdido {points_to_lose} puntos de experiencia.")
        session.commit()

    