import discord
from discord.ext import commands
from utils.rpg_data_manager import register_player, get_player_stats

def register_commands(bot):
    @bot.command(help='Registra un jugador. Usa el comando solo una vez por usuario.')
    async def registerplayer(ctx):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)

        # Verificar si el jugador ya está registrado
        player_data = get_player_stats(user_id)
        if player_data:
            await ctx.send(f'{usuario.name}, ya estás registrado como jugador.')
            return

        # Registrar nuevo jugador con datos iniciales
        initial_data = {
            'level': 1,
            'experience': 0.0,
            'health': 100,
            'mana': 50,
            'strength': 10,
            'intelligence': 10,
            'agility': 10
        }
        register_player(user_id, guild_id, **initial_data)

        await ctx.send(f'{usuario.name}, has sido registrado como jugador con éxito.')

    @bot.command(help='Muestra las estadísticas de tu personaje.')
    async def stats(ctx):
        usuario = ctx.author
        user_id = str(usuario.id)

        # Cargar los datos del jugador
        player_data = get_player_stats(user_id)
        if not player_data:
            await ctx.send(f'{usuario.name}, no estás registrado como jugador. Usa el comando !registerplayer para registrarte.')
            return

        # Crear el embed con las estadísticas
        embed = discord.Embed(
            title=f"Estadísticas de {usuario.name}",
            description="Aquí están tus estadísticas actuales:",
            color=0xFF5733
        )
        embed.add_field(name="Nivel", value=player_data['level'])
        embed.add_field(name="Experiencia", value=player_data['experience'])
        embed.add_field(name="Salud", value=player_data['health'])
        embed.add_field(name="Mana", value=player_data['mana'])
        embed.add_field(name="Fuerza", value=player_data['strength'])
        embed.add_field(name="Inteligencia", value=player_data['intelligence'])
        embed.add_field(name="Agilidad", value=player_data['agility'])

        # Enviar el embed con las estadísticas
        await ctx.send(embed=embed)

    @bot.command(help="Pregunta si pasa el ramo")
    async def poto(ctx):
        await ctx.send("poto")

