import discord
from discord.ext import commands
import requests
from utils.data_manager import load_user_data, save_user_data, load_bets, save_bet, delete_bets
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)


class Betting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bets = load_bets()
        logging.debug(f"Datos cargados al iniciar el bot: {self.bets}")

    @commands.command(name='apostar')
    async def place_bet(self, ctx, equipo: str, cantidad: int):
        usuario = ctx.author
        user_id = str(usuario.id)

        user_data = load_user_data(user_id)
        logging.debug(f"Intentando apuesta para el usuario {
                      user_id}. Datos actuales: {user_data}")

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
        logging.debug(f"Nuevo saldo para {user_id}: {user_data['balance']}")
        save_user_data(user_id, user_data['balance'])
        save_bet(user_id, equipo, cantidad)

        await ctx.send(f'{usuario.name} ha apostado {cantidad} en {equipo}')

    @commands.command(name='apuestas')
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
                mensaje += f'{usuario.name}: {
                    apuesta["cantidad"]} en {apuesta["equipo"]}\n'
            else:
                mensaje += f'Usuario desconocido (ID: {user_id}): {apuesta["cantidad"]} en {
                    apuesta["equipo"]}\n'
        await ctx.send(mensaje)

    @commands.command(name='resultados')
    async def match_result(self, ctx):
        url = "https://onefootball.com/proxy-web-experience/es/partido/2470842"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        canada = data['containers'][1]['fullWidth']['component']['matchScore']['homeTeam']
        chile = data['containers'][1]['fullWidth']['component']['matchScore']['awayTeam']
        mensaje_resultado = f'Resultado final: {canada["name"]} {
            canada["score"]} - {chile["name"]} {chile["score"]}'
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
                user_data = load_user_data(ganador_id)
                user_data['balance'] += ganancia
                save_user_data(ganador_id, user_data['balance'])
                ganador = self.bot.get_user(int(ganador_id))
                if ganador is None:
                    ganador = await self.bot.fetch_user(int(ganador_id))
                if ganador:
                    mensaje_ganadores += f'{ganador.name}: {
                        ganancia} pesos chilenos\n'
                else:
                    mensaje_ganadores += f'Usuario desconocido (ID: {ganador_id}): {
                        ganancia} pesos chilenos\n'
            delete_bets()
            await ctx.send(mensaje_ganadores)
        else:
            await ctx.send('Nadie ganó la apuesta.')


async def setup(bot):
    await bot.add_cog(Betting(bot))
