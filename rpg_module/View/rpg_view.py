import discord
from discord.ui import View, Button
from rpg_module.rpg_utils.rpg_data_manager import get_player_by_name, session, level_up_player,revive_player
from rpg_module.Enemy.enemy import Enemy
from rpg_module.SimulatedCombat.simulated_combat import SimulatedCombat


class RPGView:
    @staticmethod
    def general_menu_view(player_name, user_id):
        class GeneralMenu(View):
            def __init__(self, player_name, user_id):
                super().__init__(timeout=180.0)
                self.player_name = player_name
                self.user_id = user_id
                player = get_player_by_name(player_name)

                if player and player.health == 0:
                    self.add_item(ReviveButton(player, user_id))

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                if interaction.user.id == self.user_id:
                    return True
                await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
                return False

            @discord.ui.button(label="Ir de Aventura", style=discord.ButtonStyle.green)
            async def go_adventure(self, interaction: discord.Interaction, button: Button):
                enemy = Enemy()
                await interaction.response.send_message(
                    f"Te has encontrado con un {enemy.name}. ¿Qué quieres hacer?", 
                    view=AdventureView(self.player_name, enemy, self.user_id),
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
                        view=AssignStatsView(player, self.user_id),
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

        return GeneralMenu(player_name, user_id)

    @staticmethod
    def player_info_embed(player):
        embed = discord.Embed(
            title=f"Información del Jugador: {player.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Clase", value=player.__class__.__name__, inline=True)
        embed.add_field(name="Nivel", value=player.level, inline=True)
        embed.add_field(name="Salud", value=player.health, inline=True)
        embed.add_field(name="Fuerza", value=player.strength, inline=True)
        embed.add_field(name="Inteligencia", value=player.intelligence, inline=True)
        embed.add_field(name="Agilidad", value=player.agility, inline=True)
        embed.add_field(name="Mana", value=player.mana, inline=True)
        embed.add_field(name="Puntos de Estadística", value=player.stats_points, inline=True)
        return embed

    @staticmethod
    def registration_success_embed(player,class_name):
        embed = discord.Embed(
            title="¡Registro Exitoso!",
            description=f"{player.name}, has sido registrado como {class_name}.",
            color=discord.Color.green()
        )
        return embed
    
    @staticmethod
    def already_registered_embed(player):
        embed = discord.Embed(
            title="Error en el Registro",
            description=f"{player.name}, ya estás registrado como {player.__class__.__name__}.",
            color=discord.Color.red()
        )
        return embed

    @staticmethod
    def registration_error_embed(error_message):
        embed = discord.Embed(
            title="Error en el Registro",
            description=error_message,
            color=discord.Color.red()
        )
        return embed# Actualización del RPGView con RegisterPlayerView y PlayerInfoView
class RegisterPlayerView(View):
    def __init__(self, player, user_id):
        super().__init__(timeout=None)
        self.player = player
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Ir al Menú Principal", style=discord.ButtonStyle.green)
    async def go_to_menu(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Bienvenido al menú principal...",
            view=RPGView.general_menu_view(self.player.name, self.user_id),
            ephemeral=True
        )

class ReviveButton(Button):
    def __init__(self, player, user_id):
        super().__init__(label="Revivir", style=discord.ButtonStyle.green)
        self.player = player
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            result_message=revive_player(self.player)
            await interaction.response.edit_message(content=result_message, view=None)
        else:
            await interaction.response.send_message("No tienes permiso para interactuar con este botón.", ephemeral=True)

class AdventureView(View):
    def __init__(self, player_name, enemy, user_id):
        super().__init__(timeout=None)
        self.player_name = player_name
        self.enemy = enemy
        self.user_id = user_id
        self.combat_resolved = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

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
                    view=ReturnToMenuView(self.player_name, self.user_id)
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
                    view=ReturnToMenuView(self.player_name, self.user_id)
                )
                self.combat_resolved = True
            else:
                await interaction.followup.send("Jugador no encontrado.", ephemeral=True)

class ReturnToMenuView(View):
    def __init__(self, player_name, user_id):
        super().__init__(timeout=None)
        self.player_name = player_name
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Volver al Menú Principal", style=discord.ButtonStyle.green)
    async def return_to_menu(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Volviendo al menú principal...",
            view=RPGView.general_menu_view(self.player_name, self.user_id),
            ephemeral=True
        )

class AssignStatsView(View):
    def __init__(self, player, user_id):
        super().__init__(timeout=None)
        self.player = player
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

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

class PlayerInfoView(View):
    def __init__(self, player, user_id):
        super().__init__(timeout=None)
        self.player = player
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Actualizar Información", style=discord.ButtonStyle.blurple)
    async def refresh_info(self, interaction: discord.Interaction, button: Button):
        # Refrescar y mostrar la información del jugador
        player = get_player_by_name(self.player.name)
        if player:
            await interaction.response.edit_message(
                embed=RPGView.player_info_embed(player),
                view=self
            )
        else:
            await interaction.response.send_message("Jugador no encontrado.", ephemeral=True)

    @discord.ui.button(label="Volver al Menú Principal", style=discord.ButtonStyle.green)
    async def return_to_menu(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Volviendo al menú principal...",
            view=RPGView.general_menu_view(self.player.name, self.user_id),
            ephemeral=True
        )
