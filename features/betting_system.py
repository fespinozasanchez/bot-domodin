import discord
from discord.ext import commands
import requests
import random
from utils.data_manager import load_user_data, save_user_data, load_bets, save_bet, delete_bets
import logging


class Betting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bets = load_bets()

    @commands.command(name='apostar', help='Apostar por un equipo !apostar <equipo> <cantidad>')
    async def place_bet(self, ctx, equipo: str, cantidad: int):
        if cantidad <= 0:
            await ctx.send(f'Solo puedes apostar cantidades positivas, mono enfermo.')
            return

        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)

        user_data = load_user_data(user_id, guild_id)

        if user_data is None:
            await ctx.send(f'{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.')
            return

        if user_data['balance'] < cantidad:
            await ctx.send(f'{usuario.name}, no tienes suficiente saldo para realizar esta apuesta.')
            return

        if user_id in self.bets:
            equipo_actual = self.bets[user_id]['equipo']
            await ctx.send(f'Ya has apostado {self.bets[user_id]["cantidad"]} en {equipo_actual}.')
            return

        self.bets[user_id] = {'equipo': equipo, 'cantidad': cantidad}
        user_data['balance'] -= cantidad
        save_user_data(user_id, guild_id, user_data['balance'])
        save_bet(user_id, equipo, cantidad)

        await ctx.send(f'{usuario.name} ha apostado {cantidad} en {equipo}')

    @commands.command(name='apuestas', help='Muestra las apuestas actuales')
    async def show_bets(self, ctx):
        if not self.bets:
            await ctx.send('No hay apuestas realizadas aún.')
            return
        mensaje = "Apuestas actuales:\n"
        for user_id, apuesta in self.bets.items():
            usuario = self.bot.get_user(int(user_id))
            if usuario is None:
                usuario = await self.bot.fetch_user(int(user_id))
            if usuario:
                mensaje += f'{usuario.name}: {apuesta["cantidad"]} en {apuesta["equipo"]}\n'
            else:
                mensaje += f'Usuario desconocido (ID: {user_id}): {apuesta["cantidad"]} en {apuesta["equipo"]}\n'
        await ctx.send(mensaje)

    @commands.command(name='resultados', help='Muestra el resultado de un partido')
    async def match_result(self, ctx):
        url = "https://onefootball.com/proxy-web-experience/es/partido/2470842"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['trackingEvents'][0]['typedServerParameter']['match_state']['value'] == 'FullTime':
            canada = data['containers'][1]['fullWidth']['component']['matchScore']['homeTeam']
            chile = data['containers'][1]['fullWidth']['component']['matchScore']['awayTeam']
            mensaje_resultado = f'Resultado final: {canada["name"]} {canada["score"]} - {chile["name"]} {chile["score"]}'
            await ctx.send(mensaje_resultado)

            if canada["score"] > chile["score"]:
                equipo_ganador = canada["name"]
            elif chile["score"] > canada["score"]:
                equipo_ganador = chile["name"]
            else:
                equipo_ganador = 'Empate'

            ganadores = [user_id for user_id, apuesta in self.bets.items(
            ) if apuesta['equipo'].lower() == equipo_ganador.lower()]

            if ganadores:
                mensaje_ganadores = 'Los ganadores son:\n'
                for ganador_id in ganadores:
                    ganancia = self.bets[ganador_id]['cantidad'] * 2
                    guild_id = str(ctx.guild.id)
                    user_data = load_user_data(ganador_id, guild_id)
                    user_data['balance'] += ganancia
                    save_user_data(ganador_id, guild_id, user_data['balance'])
                    ganador = self.bot.get_user(int(ganador_id))
                    if ganador is None:
                        ganador = await self.bot.fetch_user(int(ganador_id))
                    if ganador:
                        mensaje_ganadores += f'{ganador.name}: { ganancia} MelladoCoins\n'
                    else:
                        mensaje_ganadores += f'Usuario desconocido (ID: {ganador_id}): {ganancia} MelladoCoins\n'
                await ctx.send(mensaje_ganadores)
            else:
                await ctx.send('Nadie ganó la apuesta.')

            delete_bets()  # Eliminar todas las apuestas una vez que se han procesado
            self.bets.clear()  # Limpiar la caché de apuestas después de borrarlas de la base de datos
        else:
            await ctx.send('El partido aún no ha terminado.')

    @commands.command(name='ruleta', help='Apuesta. !ruleta <cantidad> o !ruleta all')
    async def ruleta(self, ctx, cantidad: str):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)

        user_data = load_user_data(user_id, guild_id)
        if user_data is None:
            await ctx.send(f'{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.')
            return

        if cantidad.lower() == 'all':
            cantidad = user_data['balance']
        else:
            try:
                cantidad = float(cantidad)
            except ValueError:
                await ctx.send(f'{usuario.name}, la cantidad debe ser un número o "all".')
                return

        if cantidad <= 0:
            await ctx.send(f'Solo puedes apostar cantidades positivas, mono enfermo.')
            return

        if cantidad > user_data['balance']:
            await ctx.send(f'{usuario.name}, no tienes suficiente saldo para apostar esa cantidad.')
            return

        resultado = random.choice([0, 1])
        if resultado == 1:
            ganancia = cantidad
            user_data['balance'] += ganancia
            await ctx.send(f'{usuario.name}, ¡has ganado! Tu nuevo saldo es {user_data["balance"]} MelladoCoins.')
        else:
            perdida = cantidad
            user_data['balance'] -= perdida
            await ctx.send(f'{usuario.name}, has perdido. Tu nuevo saldo es {user_data["balance"]} MelladoCoins.')

        save_user_data(user_id, guild_id, user_data['balance'])


    @commands.command(name='transferir', help='Realiza una transferencia de tus MelladoCoins. Uso: !transferir <usuario> <cantidad>')
    async def transferir(self, ctx, destinatario: discord.Member, cantidad: str):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)
        destinatario_id = str(destinatario.id)

        if destinatario_id == user_id:
            await ctx.send(f'{usuario.name}, no puedes transferirte saldo a ti mismo.')
            return

        user_data = load_user_data(user_id, guild_id)
        destinatario_data = load_user_data(destinatario_id, guild_id)

        if user_data is None:
            await ctx.send(f'{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.')
            return

        if destinatario_data is None:
            await ctx.send(f'{destinatario.name} no está registrado. El destinatario debe registrarse antes de recibir saldo.')
            return

        try:
            cantidad = float(cantidad)
        except ValueError:
            await ctx.send(f'{usuario.name}, la cantidad debe ser un número.')
            return

        if cantidad <= 0:
            await ctx.send(f'{usuario.name}, solo puedes transferir cantidades positivas.')
            return

        if cantidad > user_data['balance']:
            await ctx.send(f'{usuario.name}, no tienes suficiente saldo para transferir esa cantidad.')
            return

        # Realizar la transferencia
        user_data['balance'] -= cantidad
        destinatario_data['balance'] += cantidad

        # Guardar los datos actualizados
        save_user_data(user_id, guild_id, user_data['balance'])
        save_user_data(destinatario_id, guild_id, destinatario_data['balance'])

        await ctx.send(f'{usuario.name}, has transferido {cantidad} MelladoCoins a {destinatario.name}. Tu nuevo saldo es {user_data["balance"]} MelladoCoins.')
        await ctx.send(f'{destinatario.name}, has recibido {cantidad} MelladoCoins de {usuario.name}. Tu nuevo saldo es {destinatario_data["balance"]} MelladoCoins.')




async def setup(bot):
    await bot.add_cog(Betting(bot))
