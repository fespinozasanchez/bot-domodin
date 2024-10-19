import discord
from discord.ext import commands
from discord.ui import View, Button
from rpg_module.rpg_utils.rpg_data_manager import register_player, get_player_by_name, init_alchemy_db, session
from rpg_module.View.rpg_view import RPGView, AdventureView, AssignStatsView
import random

class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Inicializa la base de datos.')
    async def init_db(self, ctx):
        try:
            init_alchemy_db()
            await ctx.send("Base de datos inicializada con éxito.")
        except Exception as e:
            await ctx.send(f"Error al inicializar la base de datos: {str(e)}")

    @commands.command(help='Registra un jugador. Usa el comando solo una vez por usuario.')
    async def register_player(self, ctx, class_name):
        usuario = ctx.author
        name = usuario.name

        # Verificar si el jugador ya está registrado
        player_data = get_player_by_name(name)
        if player_data:
            await ctx.send(embed=RPGView.already_registered_embed(player_data))
            return

        # Registrar nuevo jugador con datos iniciales
        try:
            new_player = register_player(name, class_name.lower())
            await ctx.send(embed=RPGView.registration_success_embed(new_player))
        except ValueError as e:
            await ctx.send(embed=RPGView.registration_error_embed(str(e)))

    @commands.command(help='Muestra información sobre el jugador registrado.')
    async def player_info(self, ctx):
        usuario = ctx.author
        name = usuario.name

        # Obtener información del jugador
        player_data = get_player_by_name(name)
        if not player_data:
            await ctx.send(f'{usuario.name}, no estás registrado como jugador.')
            return

        await ctx.send(embed=RPGView.player_info_embed(player_data))

    @commands.command(help='Muestra el menú general del jugador.')
    async def rpg_menu(self, ctx):
        usuario = ctx.author
        name = usuario.name

        # Verificar si el jugador está registrado
        player_data = get_player_by_name(name)
        if not player_data:
            await ctx.send(f'{usuario.name}, no estás registrado como jugador.')
            return

        view = RPGView.general_menu_view(name)
        await ctx.send("🐲¿Que deseas hacer?🐲", view=view)

async def setup(bot):
    await bot.add_cog(RPG(bot))
