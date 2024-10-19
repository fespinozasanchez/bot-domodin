import discord
from discord.ui import View, Button
from rpg_module.rpg_utils.rpg_data_manager import get_player_by_name, session, level_up_player
from rpg_module.Enemy.enemy import Enemy
from rpg_module.SimulatedCombat.simulated_combat import SimulatedCombat

class RPGView:
    @staticmethod
    def general_menu_view(player_name):
        """
        Retorna un View con las opciones del menú general del jugador.
        """
        class GeneralMenu(View):
            def __init__(self, player_name):
                super().__init__(timeout=None)
                self.player_name = player_name
                player = get_player_by_name(player_name)

                # Si el jugador tiene salud igual a 0, agregar el botón de revivir
                if player and player.health == 0:
                    self.add_item(ReviveButton(player))

            @discord.ui.button(label="Ir de Aventura", style=discord.ButtonStyle.green)
            async def go_adventure(self, interaction: discord.Interaction, button: Button):
                enemy = Enemy()
                await interaction.response.send_message(
                    f"Te has encontrado con un {enemy.name}. ¿Qué quieres hacer?", 
                    view=AdventureView(self.player_name, enemy),
                    ephemeral=True
                )

            @discord.ui.button(label="Ver Stats", style=discord.ButtonStyle.blurple)
            async def view_stats(self, interaction: discord.Interaction, button: Button):
                player = get_player_by_name(self.player_name)
                if player:
                    await interaction.response.send_message(
                        f"Stats de {player.name}:\nNivel: {player.level}\nSalud: {player.health}\nFuerza: {player.strength}\nInteligencia: {player.intelligence}\nAgilidad: {player.agility}\nMana: {player.mana}\nPuntos de Stats Disponibles: {player.stats_points}",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message("Jugador no encontrado.", ephemeral=True)

            @discord.ui.button(label="Asignar Stats", style=discord.ButtonStyle.gray)
            async def assign_stats(self, interaction: discord.Interaction, button: Button):
                player = get_player_by_name(self.player_name)
                if player:
                    await interaction.response.send_message(
                        "Puedes asignar tus puntos de stats disponibles:", 
                        view=AssignStatsView(player),
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message("Jugador no encontrado.", ephemeral=True)

            @discord.ui.button(label="Subir de Nivel", style=discord.ButtonStyle.green)
            async def level_up(self, interaction: discord.Interaction, button: Button):
                player = get_player_by_name(self.player_name)
                if player:
                    level_up_message = level_up_player(player)
                    await interaction.response.send_message(level_up_message, ephemeral=True)
                else:
                    await interaction.response.send_message("Jugador no encontrado.", ephemeral=True)

        return GeneralMenu(player_name)

class ReviveButton(Button):
    def __init__(self, player):
        super().__init__(label="Revivir", style=discord.ButtonStyle.green)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        self.player.health = 100  # Restaurar la salud del jugador
        session.commit()
        await interaction.response.edit_message(content=f"{self.player.name} ha sido revivido y ahora tiene 100 de salud.", view=None)

class AdventureView(View):
    def __init__(self, player_name, enemy):
        super().__init__(timeout=None)
        self.player_name = player_name
        self.enemy = enemy
        self.combat_resolved = False

    @discord.ui.button(label="Pelear", style=discord.ButtonStyle.red)
    async def fight(self, interaction: discord.Interaction, button: Button):
        if not self.combat_resolved:
            await interaction.response.defer()  # Defer la respuesta inicial para procesar
            player = get_player_by_name(self.player_name)
            if player:
                # Simulación de combate
                combat = SimulatedCombat(player, self.enemy)
                combat_result = combat.fight()

                # Editar el mensaje original para mostrar el resultado del combate y dar la opción de volver al menú
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=f"Has decidido pelear contra {self.enemy.name}!\n{combat_result}", 
                    view=ReturnToMenuView(self.player_name)
                )
                self.combat_resolved = True
            else:
                await interaction.followup.send("Jugador no encontrado.", ephemeral=True)

    @discord.ui.button(label="Huir", style=discord.ButtonStyle.gray)
    async def run_away(self, interaction: discord.Interaction, button: Button):
        if not self.combat_resolved:
            await interaction.response.defer()  # Defer la respuesta inicial para procesar
            player = get_player_by_name(self.player_name)
            if player:
                combat = SimulatedCombat(player, self.enemy)
                run_result = combat.run()

                # Editar el mensaje original para mostrar que el jugador huyó y dar la opción de volver al menú
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=run_result, 
                    view=ReturnToMenuView(self.player_name)
                )
                self.combat_resolved = True
            else:
                await interaction.followup.send("Jugador no encontrado.", ephemeral=True)

class ReturnToMenuView(View):
    def __init__(self, player_name):
        super().__init__(timeout=None)
        self.player_name = player_name

    @discord.ui.button(label="Volver al Menú Principal", style=discord.ButtonStyle.green)
    async def return_to_menu(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Volviendo al menú principal...",
            view=RPGView.general_menu_view(self.player_name),
            ephemeral=True
        )

class AssignStatsView(View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(label="Asignar Fuerza", style=discord.ButtonStyle.green)
    async def assign_strength(self, interaction: discord.Interaction, button: Button):
        if self.player.stats_points > 0:
            self.player.strength += 1
            self.player.stats_points -= 1
            session.commit()
            await interaction.response.send_message(f"Has aumentado tu fuerza a {self.player.strength}. Puntos restantes: {self.player.stats_points}", ephemeral=True)
        else:
            await interaction.response.send_message("No tienes puntos de stats disponibles.", ephemeral=True)

    @discord.ui.button(label="Asignar Inteligencia", style=discord.ButtonStyle.green)
    async def assign_intelligence(self, interaction: discord.Interaction, button: Button):
        if self.player.stats_points > 0:
            self.player.intelligence += 1
            self.player.stats_points -= 1
            session.commit()
            await interaction.response.send_message(f"Has aumentado tu inteligencia a {self.player.intelligence}. Puntos restantes: {self.player.stats_points}", ephemeral=True)
        else:
            await interaction.response.send_message("No tienes puntos de stats disponibles.", ephemeral=True)

    @discord.ui.button(label="Asignar Agilidad", style=discord.ButtonStyle.green)
    async def assign_agility(self, interaction: discord.Interaction, button: Button):
        if self.player.stats_points > 0:
            self.player.agility += 1
            self.player.stats_points -= 1
            session.commit()
            await interaction.response.send_message(f"Has aumentado tu agilidad a {self.player.agility}. Puntos restantes: {self.player.stats_points}", ephemeral=True)
        else:
            await interaction.response.send_message("No tienes puntos de stats disponibles.", ephemeral=True)
