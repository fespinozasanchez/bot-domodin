import discord
from discord.ui import View, Button
from rpg_module.rpg_utils.rpg_data_manager import get_player_by_name, session, level_up_player, revive_player
from rpg_module.Enemy.enemy import Enemy
from rpg_module.Enemy.boss_enemy import BossEnemy
from rpg_module.SimulatedCombat.simulated_combat import SimulatedCombat
from rpg_module.SimulatedCombat.boss_simulated_combat import SimulatedBossCombat
import time


class RPGView:
    boss_invocation_timeout = 0

    @staticmethod
    def general_menu_view(player_name, user_id, message=None):
        class GeneralMenu(View):
            def __init__(self, player_name, user_id, message=None):
                super().__init__(timeout=180.0)
                self.player_name = player_name
                self.user_id = user_id
                self.message = message
                player = get_player_by_name(player_name)
                self.player = player

                if player and player.current_health == 0:
                    self.add_item(ReviveButton(player_name, user_id, message))

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                if interaction.user.id == self.user_id:
                    return True
                await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
                return False

            @discord.ui.button(label="Ir de Aventura", style=discord.ButtonStyle.green)
            async def go_adventure(self, interaction: discord.Interaction, button: Button):
                if self.player.current_health == 0:
                    await interaction.response.send_message("Los héroes caídos no pueden participar en nuevas aventuras.", ephemeral=True)
                    return
                enemy = Enemy(self.player.level)
                await interaction.response.edit_message(
                    content=f"Te has encontrado con un {enemy.name} \nNivel: {enemy.level} \nTier: {enemy.tier} \n¿Qué quieres hacer?",
                    embed=None,
                    view=AdventureView(self.player_name, enemy, self.user_id, self.message)
                )

            @discord.ui.button(label="Ver Stats", style=discord.ButtonStyle.blurple)
            async def view_stats(self, interaction: discord.Interaction, button: Button):
                player = get_player_by_name(self.player_name)
                if player:
                    await interaction.response.edit_message(
                        embed=RPGView.player_info_embed(player),
                        view=PlayerInfoView(player, self.user_id, self.message)
                    )
                else:
                    await interaction.response.send_message("Jugador no encontrado.", ephemeral=True)

            @discord.ui.button(label="Asignar Stats", style=discord.ButtonStyle.gray)
            async def assign_stats(self, interaction: discord.Interaction, button: Button):
                player = get_player_by_name(self.player_name)
                if player:
                    await interaction.response.edit_message(
                        content=f"Puedes asignar tus {player.stats_points} puntos de stats disponibles:",
                        embed=None,
                        view=AssignStatsView(player, self.user_id, self.message)
                    )
                else:
                    await interaction.response.send_message("Jugador no encontrado.", ephemeral=True)

            @discord.ui.button(label="Subir de Nivel", style=discord.ButtonStyle.green)
            async def level_up(self, interaction: discord.Interaction, button: Button):
                player = get_player_by_name(self.player_name)
                if player:
                    level_up_message = level_up_player(player)
                    await interaction.response.edit_message(content=level_up_message, embed=None, view=self)
                else:
                    await interaction.response.send_message("Jugador no encontrado.", ephemeral=True)

            @discord.ui.button(label="Invocar un Jefe", style=discord.ButtonStyle.blurple)
            async def summon_boss(self, interaction: discord.Interaction, button: Button):
                if self.player.current_health == 0:
                    await interaction.response.send_message("Los héroes caídos no pueden invocar jefes.", ephemeral=True)
                    return
                current_time = time.time()
                if current_time < RPGView.boss_invocation_timeout:
                    remaining_time = int(RPGView.boss_invocation_timeout - current_time)
                    await interaction.response.send_message(
                        f"Ya hay un jefe invocado. Puedes invocar otro en {remaining_time} segundos.", ephemeral=True
                    )
                    return

                boss_enemy = BossEnemy(self.player.level)
                raid_view = RaidView(boss_enemy, self.player_name, self.user_id)
                await interaction.response.defer()
                raid_view.message = await interaction.followup.send(
                    content=(
                        f"**Has invocado a {boss_enemy.name}!**\n\n"
                        f"**Nivel:** {boss_enemy.level}\n"
                        f"**Tier:** {boss_enemy.tier}\n"  
                        f"**Experiencia a Repartir:** {boss_enemy.experience:,.0f}".replace(",", ".") + "\n"
                        f"**Daño requerido para derrotar:** {boss_enemy.health}\n\n"
                        "¡Jugadores, únanse a la Raid con el botón a continuación!"
                    ),
                    view=raid_view
                )

                RPGView.boss_invocation_timeout = current_time + 120

        return GeneralMenu(player_name, user_id, message)


    @staticmethod
    def ranking_embed(players):
        embed = discord.Embed(
            title="Ranking de Jugadores",
            color=discord.Color.gold()
        )
        for i, player in enumerate(players, start=1):
            embed.add_field(
                name=f"{i}. {player.name}",
                value=f" Clase {player.class_player} - Nivel: {player.level} - Experiencia: {player.experience:,.0f}".replace(",", "."),
                inline=False
            )
        return embed


    @staticmethod
    def player_info_embed(player):
        embed = discord.Embed(
            title=f"Información del Jugador: {player.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Clase", value=player.__class__.__name__, inline=True)
        embed.add_field(name="Nivel", value=player.level, inline=True)
        embed.add_field(name="Salud Máxima", value=player.health, inline=True)
        embed.add_field(name="Salud Actual", value=player.current_health, inline=True)
        embed.add_field(name="Fuerza", value=player.strength, inline=True)
        embed.add_field(name="Inteligencia", value=player.intelligence, inline=True)
        embed.add_field(name="Agilidad", value=player.agility, inline=True)
        embed.add_field(name="Defensa", value=player.defense, inline=True)
        embed.add_field(name="Evasión", value=player.evasion, inline=True)
        embed.add_field(name="Mana Máximo", value=player.mana, inline=True)
        embed.add_field(name="Mana Actual", value=player.current_mana, inline=True)
        embed.add_field(name="Experiencia", value=player.experience, inline=True)
        embed.add_field(name="Puntos de Estadística", value=player.stats_points, inline=True)
        return embed

    @staticmethod
    def registration_success_embed(player, class_name):
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
        return embed


class ReviveButton(Button):
    def __init__(self, player_name, user_id, message=None):
        super().__init__(label="Revivir", style=discord.ButtonStyle.green)
        player = get_player_by_name(player_name)
        self.player = player
        self.user_id = user_id
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            result_message = revive_player(self.player)
            await interaction.response.edit_message(content=result_message, embed=None, view=None)
            await interaction.followup.send("Volviendo al menú principal...", view=RPGView.general_menu_view(self.player.name, self.user_id, self.message))
        else:
            await interaction.response.send_message("No tienes permiso para interactuar con este botón.", ephemeral=True)


class AssignStatsView(View):
    def __init__(self, player, user_id, message=None):
        super().__init__(timeout=None)
        self.player = player
        self.user_id = user_id
        self.message = message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Asignar Fuerza", style=discord.ButtonStyle.green)
    async def assign_strength(self, interaction: discord.Interaction, button: Button):
        if self.player.stats_points > 0:
            self.player.strength += 1
            self.player.health += 10
            self.player.current_health += 10
            self.player.stats_points -= 1
            session.commit()
            await interaction.response.edit_message(
                content=f"Has aumentado tu fuerza a {self.player.strength}. Puntos restantes: {self.player.stats_points}",
                embed=None,
                view=self
            )
        else:
            await interaction.response.send_message("No tienes puntos de stats disponibles.", ephemeral=True)

    @discord.ui.button(label="Asignar Inteligencia", style=discord.ButtonStyle.green)
    async def assign_intelligence(self, interaction: discord.Interaction, button: Button):
        if self.player.stats_points > 0:
            self.player.intelligence += 1
            self.player.mana += 10
            self.player.current_mana += 10
            self.player.stats_points -= 1
            session.commit()
            await interaction.response.edit_message(
                content=f"Has aumentado tu inteligencia a {self.player.intelligence}. Puntos restantes: {self.player.stats_points}",
                embed=None,
                view=self
            )
        else:
            await interaction.response.send_message("No tienes puntos de stats disponibles.", ephemeral=True)

    @discord.ui.button(label="Asignar Agilidad", style=discord.ButtonStyle.green)
    async def assign_agility(self, interaction: discord.Interaction, button: Button):
        if self.player.stats_points > 0:
            self.player.agility += 1
            self.player.evasion += 0.01
            self.player.stats_points -= 1
            session.commit()
            await interaction.response.edit_message(
                content=f"Has aumentado tu agilidad a {self.player.agility}. Puntos restantes: {self.player.stats_points}",
                embed=None,
                view=self
            )
        else:
            await interaction.response.send_message("No tienes puntos de stats disponibles.", ephemeral=True)

    @discord.ui.button(label="Volver al Menú Principal", style=discord.ButtonStyle.green)
    async def return_to_main_menu(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(
            content="Volviendo al menú principal...",
            embed=None,
            view=RPGView.general_menu_view(self.player.name, self.user_id, self.message)
        )


class AdventureView(View):
    def __init__(self, player_name, enemy, user_id, message=None):
        super().__init__(timeout=None)
        self.player_name = player_name
        self.enemy = enemy
        self.user_id = user_id
        self.message = message
        self.combat_resolved = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Pelear", style=discord.ButtonStyle.red)
    async def fight(self, interaction: discord.Interaction, button: Button):
        if not self.combat_resolved:
            await interaction.response.defer()
            player = get_player_by_name(self.player_name)
            if player:
                combat = SimulatedCombat(player, self.enemy)
                combat_result = combat.fight()
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=f"Has decidido pelear contra {self.enemy.name}!\n{combat_result}\n",
                    embed=None,
                    view=ReturnToMenuView(self.player_name, self.user_id, self.message)
                )
                self.combat_resolved = True
            else:
                await interaction.followup.send("Jugador no encontrado.", ephemeral=True)

    @discord.ui.button(label="Huir", style=discord.ButtonStyle.gray)
    async def run_away(self, interaction: discord.Interaction, button: Button):
        if not self.combat_resolved:
            await interaction.response.defer()
            player = get_player_by_name(self.player_name)
            if player:
                combat = SimulatedCombat(player, self.enemy)
                run_result = combat.run()

                if run_result[0]:
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        content=run_result[1],
                        embed=None,
                        view=ReturnToMenuView(self.player_name, self.user_id, self.message)
                    )
                    self.combat_resolved = True
                else:
                    await interaction.followup.edit_message(
                        message_id=interaction.message.id,
                        content=run_result[1],
                        embed=None,
                        view=ReturnToMenuView(self.player_name, self.user_id, self.message)
                    )
                self.combat_resolved = True
            else:
                await interaction.followup.send("Jugador no encontrado.", ephemeral=True)


class ReturnToMenuView(View):
    def __init__(self, player_name, user_id, message=None):
        super().__init__(timeout=None)
        self.player_name = player_name
        self.user_id = user_id
        self.message = message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Volver al Menú Principal", style=discord.ButtonStyle.green)
    async def return_to_menu(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(
            content="Volviendo al menú principal...",
            embed=None,
            view=RPGView.general_menu_view(self.player_name, self.user_id, self.message)
        )


class PlayerInfoView(View):
    def __init__(self, player, user_id, message=None):
        super().__init__(timeout=None)
        self.player = player
        self.user_id = user_id
        self.message = message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Actualizar Información", style=discord.ButtonStyle.blurple)
    async def refresh_info(self, interaction: discord.Interaction, button: Button):
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
        await interaction.response.edit_message(
            content="Volviendo al menú principal...",
            embed=None,
            view=RPGView.general_menu_view(self.player.name, self.user_id, self.message)
        )


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


class RaidView(View):
    def __init__(self, boss_enemy, player_name, user_id):
        super().__init__(timeout=20) 
        self.boss_enemy = boss_enemy
        self.players_joined = []
        self.players_joined_names = []
        self.players_user_ids = []
        self.message = None

        initial_player = get_player_by_name(player_name)
        if initial_player and initial_player.name not in self.players_joined_names:
            self.players_joined.append(initial_player)
            self.players_joined_names.append(initial_player.name)
            self.players_user_ids.append(user_id)

        self.combat = SimulatedBossCombat(players=self.players_joined.copy(), boss=self.boss_enemy)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True 



    async def update_raid_message(self):
        content = (
            f"**Has invocado a {self.boss_enemy.name}!**\n\n"
            f"**Nivel:** {self.boss_enemy.level}\n"
            f"**Tier:** {self.boss_enemy.tier}\n"
            f"**Experiencia a Repartir:** {self.boss_enemy.experience:,.0f}".replace(",",".")+"\n"
            f"**Daño requerido para derrotar:** {self.boss_enemy.health}\n\n"
            f"**Jugadores actuales:** {', '.join(self.players_joined_names)}\n"
            f"**Daño total**: {self.combat.players_damage}"
        )
        await self.message.edit(content=content, view=self)

    @discord.ui.button(label="Unirse a la Raid", style=discord.ButtonStyle.green)
    async def join_raid(self, interaction: discord.Interaction, button: Button):
        player = get_player_by_name(interaction.user.name)
        if player.current_health == 0:
            await interaction.response.send_message("Los héroes caídos no pueden unirse a la Raid.", ephemeral=True)
            return
        if not player:
            await interaction.response.send_message("No se pudo encontrar al jugador en la base de datos.", ephemeral=True)
            return

        if player.name in self.players_joined_names:
            await interaction.response.send_message("Ya te has unido a la Raid.", ephemeral=True)
            return
        self.players_joined.append(player)
        self.players_joined_names.append(player.name)
        self.players_user_ids.append(interaction.user.id)

        self.combat = SimulatedBossCombat(players=self.players_joined.copy(), boss=self.boss_enemy)

        await interaction.response.send_message(f"{interaction.user.name} se ha unido a la Raid.", ephemeral=True)
        await self.update_raid_message()

    async def on_timeout(self):
        if self.players_joined:
            combat_log = self.combat.fight()
            log_chunks = split_text(f"**Resultado del combate:**\n{combat_log}")

            for chunk in log_chunks:
                await self.message.channel.send(content=chunk)

            return_to_menu_view = ReturnToMenuRaidView(self.players_joined_names, self.players_user_ids, self.message)
            await self.message.edit(content="El combate ha terminado. Revisa los resultados.", view=return_to_menu_view)
        else:
            await self.message.edit(content="Nadie se unió a la Raid. No se realizó el combate.", view=None)


class ReturnToMenuRaidView(View):
    def __init__(self, player_names, user_ids, message=None):
        super().__init__(timeout=None)
        self.player_names = player_names
        self.user_ids = user_ids
        self.message = message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in self.user_ids:
            return True
        await interaction.response.send_message("No tienes permiso para interactuar con este menú.", ephemeral=True)
        return False

    @discord.ui.button(label="Volver al Menú Principal", style=discord.ButtonStyle.green)
    async def return_to_menu(self, interaction: discord.Interaction, button: Button):
        player_name = interaction.user.name
        user_id = interaction.user.id
        await interaction.response.edit_message(
            content="Volviendo al menú principal...",
            embed=None,
            view=RPGView.general_menu_view(player_name, user_id, self.message)
        )


def split_text(text, max_length=2000):
    """Divide el texto en partes que no excedan max_length caracteres."""
    lines = text.split('\n')
    chunks = []
    current_chunk = ''

    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += '\n' + line
            else:
                current_chunk = line
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


