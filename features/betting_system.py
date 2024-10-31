import discord
from discord.ext import commands
import requests
import random
from utils.data_manager import load_user_data, save_user_data, load_bets, save_bet, delete_bets, save_roulette_status
from .const_economy import economic_limits, taxes
from .const_gacha import slot_combinations, super_slot_combinations
import logging
from datetime import datetime, timedelta


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

        if user_data is None:
            await ctx.send(f'{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.')
            return

        # Validar si la cantidad es un número o 'all'
        all_in = False
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("No puedes apostar cantidades negativas o cero.")
        except ValueError as e:
            if cantidad.lower() == 'all':
                # Validar disponibilidad de la ruleta 'all'
                roulette_status = user_data.get('roulette_status')
                if roulette_status is not None:
                    now = datetime.now()
                    if isinstance(roulette_status, datetime):
                        next_available_time = roulette_status + timedelta(hours=24)
                    else:
                        roulette_status = datetime.combine(roulette_status, datetime.min.time())
                        next_available_time = roulette_status + timedelta(hours=24)
                    if now < next_available_time:
                        time_remaining = next_available_time - now
                        horas = int(time_remaining.total_seconds() // 3600)
                        minutos = int((time_remaining.total_seconds() % 3600) // 60)
                        segundos = int(time_remaining.total_seconds() % 60)
                        embed = discord.Embed(
                            title="🚫 Ruleta No Disponible",
                            description=f"{usuario.name}, la ruleta estará disponible en {horas} horas, {minutos} minutos y {segundos} segundos.",
                            color=discord.Color.red()
                        )
                        await ctx.send(embed=embed)
                        return
                cantidad_float = user_data['balance']
                all_in = True
            else:
                embed = discord.Embed(
                    title="🚫 Cantidad Inválida",
                    description=f"{usuario.name}, la cantidad debe ser un número positivo o 'all'.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Validar límites de apuesta si no es 'all'
        if not all_in:
            if cantidad_float > user_data['balance']:
                cantidad_formateada = f"${cantidad_float:,.0f}".replace(",", ".")
                embed = discord.Embed(
                    title="🚫 Saldo Insuficiente",
                    description=f"{usuario.name}, no tienes suficiente saldo para apostar {cantidad_formateada} MelladoCoins.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            max_betting_amount = float(user_data['balance']) * float(economic_limits['max_own_balance_bet_percentage'])
            max_win_amount = float(bot_data['balance']) * float(economic_limits['max_win_percentage_per_bet'])

            if cantidad_float > max_betting_amount:
                max_betting_amount_formated = f"${max_betting_amount:,.0f}".replace(",", ".")
                embed = discord.Embed(
                    title="🚫 Apuesta Máxima Excedida",
                    description=f"{usuario.name}, la apuesta máxima es {max_betting_amount_formated} MelladoCoins.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            if cantidad_float * 1.30 > max_win_amount:
                max_win_amount = f"${max_win_amount:,.0f}".replace(",", ".")
                embed = discord.Embed(
                    title="🚫 Ganancia Máxima Excedida",
                    description=f"{usuario.name}, la ganancia máxima es {max_win_amount} MelladoCoins.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Comprobar si el banco tiene fondos suficientes
        if bot_data['balance'] < (cantidad_float * (2 if all_in else 1.30)):
            embed = discord.Embed(
                title="❌ Apuesta Denegada",
                description="El banco no tiene suficientes MelladoCoins para realizar esta apuesta.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Actualizar estado de la ruleta 'all' solo si la apuesta es válida
        if all_in:
            user_data['roulette_available'] = False
            save_roulette_status(user_id, guild_id, datetime.now(), False)

        # Resultado de la ruleta
        resultado = random.choices([0, 1], weights=[60, 40], k=1)[0]
        if resultado == 1:
            ganancia = cantidad_float * (2 if all_in else 1.30)
            user_data['balance'] += ganancia
            bot_data['balance'] -= ganancia
            ganancia_formateada = f"${ganancia:,.0f}".replace(",", ".")
            balance_formateado = f"${user_data['balance']:,.0f}".replace(",", ".")
            embed = discord.Embed(
                title="🎉 ¡Has Ganado!",
                description=f"{usuario.name}, has ganado {ganancia_formateada} MelladoCoins. Tu nuevo saldo es {balance_formateado} MelladoCoins.",
                color=discord.Color.green()
            )
        else:
            user_data['balance'] = 0 if all_in else user_data['balance'] - cantidad_float
            bot_data['balance'] += cantidad_float
            balance_formateado = f"${user_data['balance']:,.0f}".replace(",", ".")
            cantidad_formateada = f"${cantidad_float:,.0f}".replace(",", ".")
            embed = discord.Embed(
                title="😢 Has Perdido",
                description=f"{usuario.name}, has perdido {cantidad_formateada} MelladoCoins. Tu nuevo saldo es {balance_formateado} MelladoCoins.",
                color=discord.Color.red()
            )
        # Guardar los datos actualizados
        save_user_data(user_id, guild_id, user_data['balance'])
        save_user_data(bot_user_id, guild_id, bot_data['balance'])

        await ctx.send(embed=embed)

    @commands.command(name='transferir', help='Realiza una transferencia de tus MelladoCoins. Uso: !transferir <usuario> <cantidad>')
    async def transferir(self, ctx, destinatario: discord.Member, cantidad: str):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)
        bot_user_id = str(self.bot.user.id)
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

        # Cargar datos de usuario , destinatario y el bot
        user_data = load_user_data(user_id, guild_id)
        destinatario_data = load_user_data(destinatario_id, guild_id)
        bot_data = load_user_data(bot_user_id, guild_id)

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

        for limite in taxes.keys():
            if cantidad >= limite:
                impuesto = taxes[limite]
            else:
                impuesto = 0

        cantidad_format = f"${cantidad:,.0f}".replace(",", ".")
        tax_format = f"${cantidad*impuesto:,.0f}".replace(",", ".")
        if cantidad+cantidad*impuesto > user_data['balance']:
            embed = discord.Embed(
                title="🚫 Saldo Insuficiente",
                description=f"No tienes suficiente saldo para transferir {cantidad_format} MelladoCoins con su impuesto de {tax_format} MelladoCoins.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=usuario.avatar.url)
            await ctx.send(embed=embed)
            return

        # Realizar la transferencia
        user_data['balance'] -= cantidad+cantidad*impuesto
        destinatario_data['balance'] += cantidad
        bot_data['balance'] += cantidad*impuesto

        # Guardar los datos actualizados
        save_user_data(user_id, guild_id, user_data['balance'])
        save_user_data(destinatario_id, guild_id, destinatario_data['balance'])
        save_user_data(bot_user_id, guild_id, bot_data['balance'])

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


    @commands.command(name='gacha', help='Juego gacha. !gacha <cantidad>')
    async def gacha(self, ctx, cantidad: str):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)
        bot_user_id = str(self.bot.user.id)

        # Cargar los datos del usuario
        user_data = load_user_data(user_id, guild_id)
        bot_data = load_user_data(bot_user_id, guild_id)


        max_betting_amount = round(float(user_data['balance']) * float(economic_limits['max_own_balance_bet_percentage']))
        max_win_amount = round(float(bot_data['balance']) * float(economic_limits['max_win_percentage_per_bet']))

        max_betting_amount_formated = f"${max_betting_amount:,.0f}".replace(",", ".")
        max_win_amount_formated = f"${max_win_amount:,.0f}".replace(",", ".")

        if user_data is None:
            embed = discord.Embed(
                title="🚫 No Registrado",
                description=f"{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if int(cantidad) > max_betting_amount:
            embed = discord.Embed(
                title="🚫 Apuesta Máxima Excedida",
                description=f"{usuario.name}, la apuesta máxima es {max_betting_amount_formated} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        if int(cantidad)> max_win_amount:
            embed = discord.Embed(
                title="🚫 Ganancia Máxima Excedida",
                description=f"{usuario.name}, la ganancia máxima es {max_win_amount_formated} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("La cantidad debe ser mayor que 0.")
        except ValueError:
            embed = discord.Embed(
                title="🚫 Cantidad Inválida",
                description=f"{usuario.name}, por favor ingresa una cantidad válida.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if cantidad_float > user_data['balance']:
            embed = discord.Embed(
                title="🚫 Saldo Insuficiente",
                description=f"{usuario.name}, no tienes suficiente saldo para apostar {cantidad_float:.0f} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Crear el embed inicial para mostrar el juego
        embed = discord.Embed(title="🎰 ¡Gacha! 🎰", description=f"{usuario.name} está apostando {cantidad_float:.0f} MelladoCoins.", color=discord.Color.green())
        embed.add_field(name="Resultado", value="❓ | ❓ | ❓", inline=False)
        embed.set_footer(text="Presiona 'Girar' para jugar.")

        # Crear los botones
        button_girar = discord.ui.Button(label="Girar", style=discord.ButtonStyle.primary)

        # Callback para cuando el botón sea presionado
        async def button_callback(interaction):
            if interaction.user != usuario:
                await interaction.response.send_message("¡No puedes jugar en el turno de otra persona!", ephemeral=True)
                return

            # Generar los símbolos de la gachapon
            simbolos = ['🍒', '🍋', '🍉', '🔔', '⭐']
            resultado = random.choices(simbolos, k=3)

            # Mostrar el resultado en el embed
            embed.set_field_at(0, name="Resultado", value=f'{resultado[0]} | {resultado[1]} | {resultado[2]}')

            # Calcular las ganancias
            ganancia = 0
            if resultado[0] == resultado[1] == resultado[2]:  # Tres iguales
                ganancia = cantidad_float * slot_combinations[resultado[0]]
                ganancia_format = f"${ganancia:,.0f}".replace(",", ".")
                embed.add_field(name="Ganancia", value=f"¡Jackpot! Has ganado {ganancia_format} MelladoCoins.", inline=False)
                user_data['balance'] += ganancia
                bot_data['balance'] -= ganancia
            elif resultado[0] == resultado[1] or resultado[1] == resultado[2]:  # Dos iguales
                embed.add_field(name="Ganancia", value=f"¡Dos iguales! No hay ganancia esta vez.", inline=False)
            else:
                embed.add_field(name="Ganancia", value="No has ganado esta vez. Mejor suerte la próxima vez.", inline=False)
                user_data['balance'] -= cantidad_float
                bot_data['balance'] += cantidad_float

            # Guardar los datos actualizados
            save_user_data(user_id, guild_id, user_data['balance'])
            save_user_data(bot_user_id, guild_id, bot_data['balance'])

            # Botón para volver a jugar
            button_play_again = discord.ui.Button(label="Volver a jugar", style=discord.ButtonStyle.secondary)

            async def play_again_callback(interaction):
                if interaction.user == usuario:
                    # Reiniciar el juego actualizando el mismo embed y reutilizando el botón
                    embed.clear_fields()  # Limpia los campos anteriores
                    embed.add_field(name="Resultado", value="❓ | ❓ | ❓  ", inline=False)
                    embed.set_footer(text="Presiona 'Girar' para jugar nuevamente.")
                    
                    view = discord.ui.View()
                    view.add_item(button_girar)  # Volvemos a agregar el botón de "Girar"
                    
                    await interaction.response.edit_message(embed=embed, view=view)  # Actualizar el mensaje original
                else:
                    await interaction.response.send_message("¡No puedes reiniciar el juego de otra persona!", ephemeral=True)

            button_play_again.callback = play_again_callback

            # Crear nueva vista con botón de "Volver a jugar"
            view = discord.ui.View()
            view.add_item(button_play_again)

            await interaction.response.edit_message(embed=embed, view=view)

        # Asociar el callback al botón
        button_girar.callback = button_callback

        # Crear la vista y añadir el botón
        view = discord.ui.View()
        view.add_item(button_girar)

        # Enviar el embed con el botón
        await ctx.send(embed=embed, view=view)



    @commands.command(name='super_gacha', help='Juego gacha avanzado. !super_gacha <cantidad>')
    async def super_gacha(self, ctx, cantidad: str):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)
        bot_user_id = str(self.bot.user.id)

        user_data=load_user_data(user_id, guild_id)
        bot_data=load_user_data(bot_user_id, guild_id)

        max_betting_amount = round(float(user_data['balance']) * float(economic_limits['max_own_balance_bet_percentage']))
        max_win_amount = round(float(bot_data['balance']) * float(economic_limits['max_win_percentage_per_bet']))

        max_betting_amount_formated = f"${max_betting_amount:,.0f}".replace(",", ".")
        max_win_amount_formated = f"${max_win_amount:,.0f}".replace(",", ".")


        if user_data is None:
            embed = discord.Embed(
                title="🚫 No Registrado",
                description=f"{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if int(cantidad) > max_betting_amount:
            embed = discord.Embed(
                title="🚫 Apuesta Máxima Excedida",
                description=f"{usuario.name}, la apuesta máxima es {max_betting_amount_formated} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if int(cantidad)> max_win_amount:
            embed = discord.Embed(
                title="🚫 Ganancia Máxima Excedida",
                description=f"{usuario.name}, la ganancia máxima es {max_win_amount_formated} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if cantidad is None:
            embed = discord.Embed(
                title="🚫 Cantidad Inválida",
                description=f"{usuario.name}, por favor ingresa una cantidad válida.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("La cantidad debe ser mayor que 0.")
        except ValueError:
            embed = discord.Embed(
                title="🚫 Cantidad Inválida",
                description=f"{usuario.name}, por favor ingresa una cantidad válida.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        cantidad_float_format = f"${cantidad_float:,.0f}".replace(",", ".")
        if cantidad_float > user_data['balance']:
            embed = discord.Embed(
                title="🚫 Saldo Insuficiente",
                description=f"{usuario.name}, no tienes suficiente saldo para apostar {cantidad_float_format} MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="🎰 ¡Super Gacha! 🎰", description=f"{usuario.name} está apostando {cantidad_float_format} MelladoCoins.", color=discord.Color.red())
        embed.add_field(name="Resultado", value="❓ | ❓ | ❓ | ❓| ❓", inline=False)
        embed.set_footer(text="Presiona 'Girar' para jugar.")


        button_girar = discord.ui.Button(label="Girar", style=discord.ButtonStyle.primary)

        async def button_callback(interaction):
            if interaction.user != usuario:
                await interaction.response.send_message("¡No puedes jugar en el turno de otra persona!", ephemeral=True)
                return

            # Generar los símbolos de la gachapon
            simbolos = ['🍒', '🍋', '🍉', '🔔', '⭐']
            resultado = random.choices(simbolos, k=5)

            # Mostrar el resultado en el embed
            embed.set_field_at(0, name="Resultado", value=f'{resultado[0]} | {resultado[1]} | {resultado[2]}| {resultado[3]}| {resultado[4]}')

            # Calcular las ganancias
            ganancia = 0
            if resultado[0] == resultado[1] == resultado[2] == resultado[3] == resultado[4]:  # Cinco iguales
                ganancia = cantidad_float * super_slot_combinations[resultado[0]]
                ganancia_format =f"{ganancia:,.0f}".replace(",", ".")
                embed.add_field(name="Ganancia", value=f"¡Jackpot! Has ganado {ganancia_format} MelladoCoins.", inline=False)
                user_data['balance'] += ganancia
                bot_data['balance'] -= ganancia
                 # Guardar los datos actualizados
           
        
            # Cuatro iguales 
            elif (resultado[0] == resultado[1] == resultado[2] == resultado[3] or
                resultado[1] == resultado[2] == resultado[3] == resultado[4]):
                ganancia = cantidad_float * super_slot_combinations[resultado[2]]  *0.50
                ganancia_format =f"{ganancia:,.0f}".replace(",", ".")
                embed.add_field(name="Ganancia", value=f"Cuatro iguales! Has ganado {ganancia_format} MelladoCoins.", inline=False)
                user_data['balance'] += ganancia
                bot_data['balance'] -= ganancia
                # Guardar los datos actualizados
             
               

            # Tres iguales 
            elif (resultado[0] == resultado[1] == resultado[2] or
                resultado[1] == resultado[2] == resultado[3] or
                resultado[2] == resultado[3] == resultado[4]):
                ganancia = cantidad_float * slot_combinations[resultado[2]]  
                ganancia_format =f"{ganancia:,.0f}".replace(",", ".")
                embed.add_field(name="Ganancia", value=f"¡Tres iguales! Has ganado {ganancia_format} MelladoCoins.", inline=False)
                user_data['balance'] += ganancia
                bot_data['balance'] -= ganancia
                # Guardar los datos actualizados
                
               

            # Dos iguales 
            elif (resultado[0] == resultado[1] or
                resultado[1] == resultado[2] or
                resultado[2] == resultado[3] or
                resultado[3] == resultado[4]):
                coste= cantidad_float
                user_data['balance'] -= coste
                bot_data['balance'] += coste
                embed.add_field(name="Ganancia", value="No has ganado esta vez. Mejor suerte la próxima vez.", inline=False)
                

            # Ninguna ganancia
            else:
                coste= cantidad_float
                user_data['balance'] -= coste
                bot_data['balance'] += coste
                embed.add_field(name="Ganancia", value="No has ganado esta vez. Mejor suerte la próxima vez.", inline=False)
                
                
            save_user_data(user_id, guild_id, user_data['balance'])
            save_user_data(bot_user_id, guild_id, bot_data['balance'])
           

            # Botón para volver a jugar
            button_play_again = discord.ui.Button(label="Volver a jugar", style=discord.ButtonStyle.secondary)
            async def play_again_callback(interaction):
                if interaction.user == usuario:
                    # Reiniciar el juego actualizando el mismo embed y reutilizando el botón
                    embed.clear_fields()  # Limpia los campos anteriores
                    embed.add_field(name="Resultado", value="❓ | ❓ | ❓ |❓ |❓", inline=False)
                    embed.set_footer(text="Presiona 'Girar' para jugar nuevamente.")
                    
                    view = discord.ui.View()
                    view.add_item(button_girar)  # Volvemos a agregar el botón de "Girar"
                    
                    await interaction.response.edit_message(embed=embed, view=view)  # Actualizar el mensaje original
                else:
                    await interaction.response.send_message("¡No puedes reiniciar el juego de otra persona!", ephemeral=True)

            button_play_again.callback = play_again_callback
            

            # Crear nueva vista con botón de "Volver a jugar"
            view = discord.ui.View()
            view.add_item(button_play_again)

            await interaction.response.edit_message(embed=embed, view=view)

        # Asociar el callback al botón
        button_girar.callback = button_callback

        
        


        # Crear la vista y añadir el botón
        view = discord.ui.View()
        view.add_item(button_girar)

        # Enviar el embed con el botón
        await ctx.send(embed=embed, view=view)
            










    @commands.command(name='gacha_info', help='Información sobre el juego gacha')
    async def gacha_info(self, ctx):
        embed = discord.Embed(
            title="🎰 Gacha",
            description="¡Bienvenido al juego Gacha! En este juego, debes hacer girar la máquina de Gachapon y esperar a que los símbolos coincidan. Aquí tienes la tabla de pagos:",
            color=discord.Color.green()
        )
        for simbolo, pago in slot_combinations.items():
            embed.add_field(name=simbolo, value=f"Paga x{pago}", inline=True)
        embed.set_footer(text="¡Buena suerte!")

        await ctx.send(embed=embed)
                      
    @commands.command(name='super_gacha_info', help='Información sobre el juego super gacha')
    async def super_gacha_info(self, ctx):
        embed = discord.Embed(
            title="🎰 Super Gacha",
            description="¡Bienvenido al juego Super Gacha! En este juego, debes hacer girar la máquina de Gachapon y esperar a que los símbolos coincidan. Aquí tienes la tabla de pagos:",
            color=discord.Color.red()
        )
        for simbolo, pago in super_slot_combinations.items():
            embed.add_field(name=simbolo, value=f"Paga x{pago}", inline=True)
        embed.set_footer(text="¡Buena suerte!")

        await ctx.send(embed=embed)


    

async def setup(bot):
    await bot.add_cog(Betting(bot))
