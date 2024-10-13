import discord
from discord.ext import commands
import requests
import random
from utils.data_manager import load_user_data, save_user_data, load_bets, save_bet, delete_bets
from .const_economy import economic_limits
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
            apuesta_actual = f"${self.bets[user_id]['cantidad']:,.0f}".replace(",", ".")
            await ctx.send(f'Ya has apostado {apuesta_actual} en {equipo_actual}.')
            return

        self.bets[user_id] = {'equipo': equipo, 'cantidad': cantidad}
        user_data['balance'] -= cantidad
        save_user_data(user_id, guild_id, user_data['balance'])
        save_bet(user_id, equipo, cantidad)

        apuesta_formateada = f"${cantidad:,.0f}".replace(",", ".")
        await ctx.send(f'{usuario.name} ha apostado {apuesta_formateada} en {equipo}')

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
            cantidad_formateada = f"${apuesta['cantidad']:,.0f}".replace(",", ".")
            if usuario:
                mensaje += f'{usuario.name}: {cantidad_formateada} en {apuesta["equipo"]}\n'
            else:
                mensaje += f'Usuario desconocido (ID: {user_id}): {cantidad_formateada} en {apuesta["equipo"]}\n'
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
                    ganancia_formateada = f"${ganancia:,.0f}".replace(",", ".")
                    if ganador:
                        mensaje_ganadores += f'{ganador.name}: {ganancia_formateada} MelladoCoins\n'
                    else:
                        mensaje_ganadores += f'Usuario desconocido (ID: {ganador_id}): {ganancia_formateada} MelladoCoins\n'
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
        bot_user_id = str(self.bot.user.id)
        bot_data = load_user_data(bot_user_id, guild_id)
        user_data = load_user_data(user_id, guild_id)
        max_betting_amount = float(user_data['balance']) * float(economic_limits['max_own_balance_bet_percentage'])
        max_win_amount = float(bot_data['balance']) * float(economic_limits['max_win_percentage_per_bet'])
        if user_data is None:
            await ctx.send(f'{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.')
            return

        if cantidad.lower() == 'all':
            cantidad = user_data['balance']
        else:
            try:
                cantidad = float(cantidad)
            except ValueError:
                embed = discord.Embed(
                    title="🚫 Cantidad Inválida",
                    description="{usuario.name}}, la cantidad debe ser un número válido o 'all'.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        if cantidad <= 0:
            embed = discord.Embed(
                title="🚫 Cantidad Inválida",
                description="{usuario.name}}, solo puedes apostar cantidades positivas.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        if cantidad > max_betting_amount:
            embed = discord.Embed(
                title="🚫 Apuesta Máxima Excedida",
                description=f"{usuario.name}, Tu apuesta máxima permitida es {max_betting_amount} MelladoCoins. A llorar a la lloreria por mas plata",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if cantidad * 1.75 > max_win_amount:
            embed = discord.Embed(
                title="🚫 Ganancia Máxima Excedida",
                description=f"{usuario.name}, tu ganancia máxima permitida es {max_win_amount} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if bot_data['balance'] < (cantidad*1.75):
            embed = discord.Embed(
                title="❌ Apuesta Denegada",
                description="El banco no tiene suficientes MelladoCoins para realizar esta apuesta.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return


        if cantidad > user_data['balance']:
            embed = discord.Embed(
                title="🚫 Saldo Insuficiente",
                description=f"{usuario.name}, no tienes suficiente saldo  para apostar {cantidad} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        resultado = random.choice([0, 1])
        if resultado == 1:
            ganancia = cantidad*1.75
            user_data['balance'] += ganancia
            bot_data['balance'] -= ganancia
            saldo_formateado = f"${user_data['balance']:,.0f}".replace(",", ".")
            embed = discord.Embed(
                title="🎉 ¡Has Ganado!",
                description=f"{usuario.name}, has ganado {ganancia} MelladoCoins, tu nuevo saldo es {saldo_formateado} MelladoCoins.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            perdida = cantidad
            user_data['balance'] -= perdida
            bot_data['balance'] += perdida
            saldo_formateado = f"${user_data['balance']:,.0f}".replace(",", ".")
            embed = discord.Embed(
                title="😢 Has Perdido",
                description=f"{usuario.name}, has perdido. Tu nuevo saldo es {saldo_formateado} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        save_user_data(user_id, guild_id, user_data['balance'])
        save_user_data(self.bot.user.id, guild_id, bot_data['balance'])

    @commands.command(name='transferir', help='Realiza una transferencia de tus MelladoCoins. Uso: !transferir <usuario> <cantidad>')
    async def transferir(self, ctx, destinatario: discord.Member, cantidad: str):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)
        destinatario_id = str(destinatario.id)

        # Verificar si el usuario intenta transferirse a sí mismo
        if destinatario_id == user_id:
            embed = discord.Embed(
                title="🚫 Error de Transferencia",
                description="No puedes transferirte saldo a ti mismo.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=usuario.avatar.url)
            await ctx.send(embed=embed)
            return

        # Cargar datos de usuario y destinatario
        user_data = load_user_data(user_id, guild_id)
        destinatario_data = load_user_data(destinatario_id, guild_id)

        # Verificar si el usuario está registrado
        if user_data is None:
            embed = discord.Embed(
                title="🚫 No Registrado",
                description=f"{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=usuario.avatar.url)
            await ctx.send(embed=embed)
            return

        # Verificar si el destinatario está registrado
        if destinatario_data is None:
            embed = discord.Embed(
                title="🚫 Destinatario No Registrado",
                description=f"{destinatario.name} no está registrado. El destinatario debe registrarse antes de recibir saldo.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=destinatario.avatar.url)
            await ctx.send(embed=embed)
            return

        # Validar la cantidad de la transferencia
        try:
            cantidad = float(cantidad)
        except ValueError:
            embed = discord.Embed(
                title="🚫 Cantidad Inválida",
                description="La cantidad debe ser un número válido.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=usuario.avatar.url)
            await ctx.send(embed=embed)
            return

        if cantidad <= 0:
            embed = discord.Embed(
                title="🚫 Cantidad Inválida",
                description="Solo puedes transferir cantidades positivas.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=usuario.avatar.url)
            await ctx.send(embed=embed)
            return

        if cantidad > user_data['balance']:
            embed = discord.Embed(
                title="🚫 Saldo Insuficiente",
                description=f"No tienes suficiente saldo para transferir {cantidad} MelladoCoins.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=usuario.avatar.url)
            await ctx.send(embed=embed)
            return

        # Realizar la transferencia
        user_data['balance'] -= cantidad
        destinatario_data['balance'] += cantidad

        # Guardar los datos actualizados
        save_user_data(user_id, guild_id, user_data['balance'])
        save_user_data(destinatario_id, guild_id, destinatario_data['balance'])

        cantidad_formateada = f"${cantidad:,.0f}".replace(",", ".")
        saldo_usuario_formateado = f"${user_data['balance']:,.0f}".replace(",", ".")
        saldo_destinatario_formateado = f"${destinatario_data['balance']:,.0f}".replace(",", ".")

        # Mensaje de confirmación para el usuario
        embed_usuario = discord.Embed(
            title="✅ Transferencia Exitosa",
            description=f"Has transferido {cantidad_formateada} MelladoCoins a {destinatario.name}.",
            color=discord.Color.green()
        )
        embed_usuario.add_field(name="Tu Nuevo Saldo", value=f"{saldo_usuario_formateado} MelladoCoins", inline=False)
        embed_usuario.set_thumbnail(url=usuario.avatar.url)
        await ctx.send(embed=embed_usuario)

        # Mensaje de confirmación para el destinatario
        embed_destinatario = discord.Embed(
            title="💰 Has Recibido una Transferencia",
            description=f"Has recibido {cantidad_formateada} MelladoCoins de {usuario.name}.",
            color=discord.Color.green()
        )
        embed_destinatario.add_field(name="Tu Nuevo Saldo", value=f"{saldo_destinatario_formateado} MelladoCoins", inline=False)
        embed_destinatario.set_thumbnail(url=destinatario.avatar.url)
        await ctx.send(embed=embed_destinatario)


async def setup(bot):
    await bot.add_cog(Betting(bot))
