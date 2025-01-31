import io
import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands, tasks
from utils.data_manager import insert_bot_data, load_user_data, save_loan_data, save_user_data, load_all_users, set_balance
import logging
from PIL import Image, ImageDraw, ImageFont
import math
import random as ra
from utils.channel_manager import save_channel_setting, load_channel_setting
from datetime import datetime, timedelta
from .const_economy import taxes, give_money_limits, growth_limits
# matplotlib.use('Agg')

logging.basicConfig(level=logging.DEBUG)


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_all_users()
        self.passive_income.start()
        self.mellado_coins_task.start()
        self.central_bank_task.start()

    @commands.command(name='impuestos', help='Informa los impuestos a pagar por cantidad de MelladoCoins en transferencias. Uso: !info')
    async def impuestos(self, ctx):
        tax_dir = taxes
        embed = discord.Embed(
            title="🏦 Impuestos de Mellado Bank",
            description="Impuestos a pagar por cantidad de MelladoCoins en transferencias.",
            color=discord.Color.blue()
        )
        for amount, tax in tax_dir.items():
            embed.add_field(name=f"Por {amount:,.0f} MelladoCoins", value=f"{tax * 100:.2f}%", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='prestamo', help='Solicita un préstamo de MelladoCoins. Uso: !prestamo <cantidad>')
    async def prestamo(self, ctx, cantidad: int):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)

        if cantidad <= 0 or cantidad > 30_000_000:
            embed = discord.Embed(
                title="❌ Préstamo Denegado",
                description="El préstamo no puede ser negativo, cero o mayor a 30.000.000 MelladoCoins.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if ra.random() > 0.75:  # 50% de probabilidad de éxito
            embed = discord.Embed(
                title="❌ Préstamo Denegado",
                description="No, tienes cara de pobre, así que no te daré el préstamo.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Cargar los datos del usuario
        user_data = load_user_data(user_id, guild_id)
        if user_data is None:
            embed = discord.Embed(
                title="❌ No Registrado",
                description=f"{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Verificar si ya tiene un préstamo pendiente
        loan_amount = user_data.get('loan_amount', 0)
        if loan_amount > 0:
            embed = discord.Embed(
                title="⏳ Préstamo Denegado",
                description="No puedes solicitar un nuevo préstamo hasta que hayas pagado el anterior.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        bot_user_id = str(self.bot.user.id)
        bot_data = load_user_data(bot_user_id, guild_id)

        if bot_data is None:
            logging.error(f"No se encontró el balance del bot en la base de datos (user_id: {bot_user_id}, guild_id: {guild_id})")
            return

        # Verificar si el banco tiene saldo suficiente
        if bot_data['balance'] < cantidad:
            embed = discord.Embed(
                title="❌ Préstamo Denegado",
                description="El banco no tiene suficientes MelladoCoins para otorgar este préstamo.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        user_data['balance'] += cantidad
        bot_data['balance'] -= cantidad

        save_user_data(bot_user_id, guild_id, bot_data['balance'])

        loan_due_time = datetime.now() + timedelta(days=1)
        save_loan_data(user_id, guild_id, user_data['balance'], last_loan_time=datetime.now(), loan_amount=cantidad, loan_due_time=loan_due_time)

        cantidad_formateada = f"${cantidad:,.0f}".replace(",", ".")
        saldo_formateado = f"${user_data['balance']:,.0f}".replace(",", ".")

        # Respuesta del bot con embed para el usuario
        embed = discord.Embed(
            title="✅ Préstamo Aprobado",
            description=f"¡Has recibido {cantidad_formateada} MelladoCoins!",
            color=discord.Color.green()
        )
        embed.add_field(name="Nuevo Saldo", value=f"{saldo_formateado} MelladoCoins", inline=False)
        embed.set_thumbnail(url=usuario.avatar.url)

        await ctx.send(embed=embed)

        # Embed del banco
        saldo_bot_formateado = f"${bot_data['balance']:,.0f}".replace(",", ".")

        embed_bot = discord.Embed(
            title="💰 Préstamo Emitido",
            description=f"El banco (bot) ha transferido {cantidad_formateada} MelladoCoins hacia {usuario.mention}.\nEl préstamo vence en 24 horas.\n¡No olvides pagar a tiempo!\nHay un impuesto del 55% sobre el monto del préstamo.\nSi no pagas a tiempo, se aplicará un interés diario del 1.7% sobre el monto del préstamo.",
            color=discord.Color.blue()
        )
        embed_bot.add_field(name="Saldo del Banco", value=f"{saldo_bot_formateado} MelladoCoins", inline=False)
        embed_bot.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.send(embed=embed_bot)

    @commands.command(name='pagar_prestamo', help='Paga tu préstamo pendiente. Uso: !pagar_prestamo')
    async def pagar_prestamo(self, ctx):
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)

        # logging.info(f"Solicitud de pago de préstamo por parte de {usuario.name} ({user_id}) en el guild {guild_id}")

        # Cargar los datos del usuario
        user_data = load_user_data(user_id, guild_id)
        if user_data is None:
            embed = discord.Embed(
                title="❌ No Registrado",
                description=f"{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loan_amount = user_data.get('loan_amount', 0)
        loan_due_time = user_data.get('loan_due_time')
        balance = user_data.get('balance', 0)

        # Verificar si hay un préstamo pendiente
        if loan_amount <= 0:
            embed = discord.Embed(
                title="❌ Sin Préstamos Pendientes",
                description="No tienes ningún préstamo pendiente que pagar.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Calcular el impuesto del 55% y los intereses si aplica
        ahora = datetime.now()
        impuesto_fijo = loan_amount * 0.55
        interes_extra = 0

        if ahora > loan_due_time:
            tiempo_pasado = ahora - loan_due_time
            dias_extra = tiempo_pasado.days
            interes_extra = loan_amount * (0.074 * dias_extra)

        total_a_pagar = loan_amount + impuesto_fijo + interes_extra
        total_a_pagar_formateado = f"${total_a_pagar-balance:,.0f}".replace(",", ".")

        if balance < total_a_pagar:
            embed = discord.Embed(
                title="❌ Saldo Insuficiente",
                description=f"No tienes suficiente saldo para pagar el préstamo. Necesitas {total_a_pagar_formateado} MelladoCoins más.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Actualizar el saldo del usuarios
        user_data['balance'] -= total_a_pagar
        save_loan_data(user_id, guild_id, user_data['balance'], last_loan_time=None, loan_amount=0, loan_due_time=None)

        # Cargar el saldo del banco
        bot_user_id = str(self.bot.user.id)
        bot_data = load_user_data(bot_user_id, guild_id)

        if bot_data is None:
            logging.error(f"No se encontró el balance del bot en la base de datos (user_id: {bot_user_id}, guild_id: {guild_id})")
            return

        # Actualizar el saldo del banco
        bot_data['balance'] += total_a_pagar
        save_user_data(bot_user_id, guild_id, bot_data['balance'])

        cantidad_formateada = f"${total_a_pagar:,.0f}".replace(",", ".")
        saldo_formateado = f"${user_data['balance']:,.0f}".replace(",", ".")

        # Respuesta del bot con embed para el usuario
        embed = discord.Embed(
            title="✅ Préstamo Pagado",
            description=f"Has pagado {cantidad_formateada} MelladoCoins, incluyendo el impuesto del 55%.",
            color=discord.Color.green()
        )
        embed.add_field(name="Nuevo Saldo", value=f"{saldo_formateado} MelladoCoins", inline=False)
        embed.set_thumbnail(url=usuario.avatar.url)

        await ctx.send(embed=embed)

        # Embed del banco
        saldo_bot_formateado = f"${bot_data['balance']:,.0f}".replace(",", ".")

        embed_bot = discord.Embed(
            title="💰 Préstamo Recibido",
            description=f"El banco ha recibido el pago de {cantidad_formateada} MelladoCoins.",
            color=discord.Color.blue()
        )
        embed_bot.add_field(name="Saldo del Banco", value=f"{saldo_bot_formateado} MelladoCoins", inline=False)
        embed_bot.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.send(embed=embed_bot)

    @commands.command(name='registrar')
    async def register_user(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        # Asegúrate de que la clave se forma correctamente
        key = f"{user_id}_{guild_id}"
        user_data = load_user_data(user_id, guild_id)
        # print(user_data)
        if user_data:
            await ctx.send(f'{ctx.author.name}, ya estás registrado.')
        else:
            self.data[key] = {'guild_id': guild_id, 'balance': 50000}
            save_user_data(user_id, guild_id, 1000)
            await ctx.send(f'{ctx.author.name}, has sido registrado con un saldo inicial de $1.000 MelladoCoins.')

    @commands.command(name='saldo')
    async def check_balance(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user_data = load_user_data(user_id, guild_id)

        if user_data:
            balance = round(user_data['balance'], 0)  # Redondear a 0 decimales
            balance_formatted = f"${balance:,.0f}".replace(",", ".")  # Formato con puntos de mil y sin decimales
            embed = discord.Embed(
                title="💳 Mellado Bank",
                description=f"Saldo disponible para {ctx.author.name}",
                color=discord.Color.blue()  # Puedes elegir el color que más te guste
            )
            embed.set_thumbnail(url=ctx.author.avatar.url)  # Se corrige el acceso a la URL del avatar
            embed.add_field(name="Usuario", value=ctx.author.name, inline=True)
            embed.add_field(name="ID", value=ctx.author.id, inline=True)
            embed.add_field(name="Saldo Disponible", value=f"{balance_formatted} MelladoCoins", inline=False)
            embed.set_footer(text="Gracias por utilizar Mellado Bank", icon_url="https://pillan.inf.uct.cl/~fespinoza/logo.png")  # Logo del banco, opcional

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🚫 Mellado Bank",
                description=f"{ctx.author.name}, no estás registrado.",
                color=discord.Color.red()  # Rojo para resaltar el error
            )
            embed.set_thumbnail(url=ctx.author.avatar.url)  # Se corrige el acceso a la URL del avatar
            embed.add_field(name="Acción Requerida", value="Usa el comando !registrar para registrarte.", inline=False)
            embed.set_footer(text="Registro necesario para utilizar Mellado Bank", icon_url="https://pillan.inf.uct.cl/~fespinoza/logo.png")  # Logo del banco, opcional

            await ctx.send(embed=embed)

    @commands.command(name='grafico_saldos')
    async def grafico_saldos(self, ctx):
        """
        This function likely generates a graphical representation of account balances.

        :param ctx: ctx is a common abbreviation for "context" in programming. It typically refers to the
        context in which a function or method is being called, and it often contains information or
        references that are relevant to the current execution environment. In the case of your code
        snippet, ctx likely represents the context of the function
        """
        guild_id = str(ctx.guild.id)
        bot1 = "1290763344113827953"
        bot2 = "1015378452225994793"
        all_users = load_all_users(guild_id)
        all_users = {k: v for k, v in all_users.items() if not any(bot in k.split('_')[0] for bot in [bot1, bot2])}

        all_users = dict(sorted(all_users.items(), key=lambda item: item[1]['balance'], reverse=True))
        user_names = []
        balances = []

        for user_key, user_data in all_users.items():
            user = await self.bot.fetch_user(user_key.split('_')[0])
            user_names.append(user.name)
            balances.append(round(user_data['balance'], 0))

        width = 800
        height = 600
        padding = 120
        max_users_per_chart = 6
        total_users = len(user_names)

        colors = [(255, 99, 71), (60, 179, 113), (65, 105, 225), (255, 165, 0), (147, 112, 219), (255, 20, 147)]

        try:
            title_font = ImageFont.truetype("arialbd.ttf", 14)
        except IOError:
            title_font = ImageFont.load_default()

        num_chunks = math.ceil(total_users / max_users_per_chart)
        for chunk_idx in range(num_chunks):

            start_idx = chunk_idx * max_users_per_chart
            end_idx = min((chunk_idx + 1) * max_users_per_chart, total_users)
            user_chunk = user_names[start_idx:end_idx]
            balance_chunk = balances[start_idx:end_idx]
            chunk_users = len(user_chunk)

            bar_width = max(20, (width - 2 * padding) // (chunk_users * 2))
            spacing = max(30, (width - 2 * padding) // (chunk_users * 2))
            img = Image.new('RGB', (width, height), color=(255, 255, 255))
            d = ImageDraw.Draw(img)

            title = f"Saldo de Usuarios en {ctx.guild.name} - Parte {chunk_idx + 1}"
            d.text((width // 2 - len(title) * 3, 10), title, font=title_font, fill=(0, 0, 0))

            max_balance = max(balance_chunk) if max(balance_chunk) > 0 else 1
            min_balance = min(balance_chunk) if min(balance_chunk) < 0 else 0

            zero_line_y = height - padding - int((0 - min_balance) / (max_balance - min_balance) * (height - 2 * padding))
            d.line([(padding, zero_line_y), (width - padding, zero_line_y)], fill=(0, 0, 0), width=2)  # Línea negra para el saldo 0

            # Dibujar barras con diferentes colores
            for i, (name, balance) in enumerate(zip(user_chunk, balance_chunk)):
                # Calcular la altura de la barra proporcional al saldo
                if balance >= 0:
                    bar_height = int((balance / (max_balance - min_balance)) * (height - 2 * padding))
                    y0 = zero_line_y - bar_height  # La barra positiva crece hacia arriba desde el eje 0
                    y1 = zero_line_y  # Parte inferior en el eje 0
                else:
                    bar_height = int((abs(balance) / (max_balance - min_balance)) * (height - 2 * padding))
                    y0 = zero_line_y  # La barra negativa empieza en el eje 0
                    y1 = zero_line_y + bar_height  # Crece hacia abajo

                x0 = padding + i * (bar_width + spacing)

                # Dibujar la barra con un color diferente
                bar_color = colors[i % len(colors)]  # Ciclar entre los colores disponibles
                d.rectangle([x0, y0, x0 + bar_width, y1], fill=bar_color)

                # Rotar los nombres de los usuarios 90 grados para evitar solapamientos
                name_font_size = 20  # Tamaño base de la fuente
                if bar_width < 50:  # Si el espacio es pequeño, reducir la fuente
                    name_font_size = 10
                try:
                    name_font = ImageFont.truetype("arialbd.ttf", name_font_size)
                except IOError:
                    name_font = ImageFont.load_default()

                # Crear una imagen con el nombre rotado
                text_img = Image.new('RGBA', (100, 40), (255, 255, 255, 0))
                draw_text = ImageDraw.Draw(text_img)
                draw_text.text((0, 0), name, font=name_font, fill=(0, 0, 0))

                # Rotar el texto 90 grados
                rotated_text_img = text_img.rotate(90, expand=True)

                # Ajustar la posición del texto rotado debajo de la barra
                img.paste(rotated_text_img, (x0 + bar_width // 2 - rotated_text_img.width // 2, height - padding - 25), rotated_text_img)

                # Escribir el saldo sobre la barra
                d.text((x0 + 5, y0 - 20), f"${balance:,.0f}", font=title_font, fill=(0, 0, 0))

            # Guardar la imagen en un buffer de memoria como PNG
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)

            # Enviar el archivo PNG a Discord
            file = discord.File(buf, filename=f'grafico_saldos_parte_{chunk_idx + 1}.png')
            await ctx.send(file=file)

    def update_balance(self, user_id, guild_id, amount):
        user_data = load_user_data(user_id, guild_id)
        if user_data:
            user_data['balance'] += amount
            save_user_data(user_id, guild_id, user_data['balance'])

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            user_id = str(message.author.id)
            guild_id = str(message.guild.id)
            key = f"{user_id}_{guild_id}"
            if key in self.data:
                self.update_balance(user_id, guild_id, 0.1)

    @tasks.loop(minutes=60)
    async def passive_income(self):
        for key, user_data in self.data.items():
            try:
                user_id, guild_id = key.split("_")
                self.update_balance(user_id, guild_id, 0.01)
            except ValueError:
                logging.error(f"Key '{key}' does not have the expected format 'user_id_guild_id'")

    @commands.command(name='set_channel')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        save_channel_setting(guild_id, channel.id)
        await ctx.send(f"Canal configurado a {channel.mention} para los mensajes de MelladoCoins.")
        logging.info(f"Canal configurado en {ctx.guild.name}: {channel.name}")

    @commands.command(name='saldo_dimadon', help='Muestra el saldo de Dimadon')
    async def saldo_dimadon(self, ctx):
        guild_id = str(ctx.guild.id)
        bot_id = self.bot.user.id
        bot_data = load_user_data(str(bot_id), guild_id)
        if bot_data:
            balance = round(bot_data['balance'], 0)
            balance_formatted = f"${balance:,.0f}".replace(",", ".")
            embed = discord.Embed(
                title="💰 Mellado Bank",
                description="Saldo del Banco Central",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.add_field(name="Usuario", value=self.bot.user.name, inline=True)
            embed.add_field(name="ID", value=self.bot.user.id, inline=True)
            embed.add_field(name="Saldo Disponible", value=f"{balance_formatted} MelladoCoins", inline=False)
            embed.set_footer(text="Gracias por utilizar Mellado Bank", icon_url="https://pillan.inf.uct.cl/~fespinoza/logo.png")  # Logo del banco, opcional

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🚫 Mellado Bank",
                description=f"El Banco Central no está registrado.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.add_field(name="Acción Requerida", value="El Banco Central debe ser registrado para utilizar Mellado Bank.", inline=False)
            embed.set_footer(text="Registro necesario para utilizar Mellado Bank", icon_url="https://pillan.inf.uct.cl/~fespinoza/logo.png")

    @tasks.loop(hours=12)
    async def mellado_coins_task(self):
        try:
            for guild in self.bot.guilds:
                guild_id = str(guild.id)
                channel_id = load_channel_setting(guild_id)  # Cargar la configuración del canal

                # Si no hay un canal configurado, selecciona el primer canal disponible
                if channel_id is None:
                    channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                    if channel:
                        channel_id = channel.id
                        save_channel_setting(guild_id, channel_id)  # Guarda este canal como el predeterminado
                    else:
                        logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                        continue
                else:
                    channel = self.bot.get_channel(channel_id)
                    if not channel or not channel.permissions_for(guild.me).send_messages:
                        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                        if channel:
                            channel_id = channel.id
                            save_channel_setting(guild_id, channel_id)  # Guarda este nuevo canal como el predeterminado
                        else:
                            logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                            continue

                members = [member for member in guild.members if not member.bot]
                if not members:
                    continue

                usuario = ra.choice(members)
                user_id = str(usuario.id)
                user_data = load_user_data(user_id, guild_id)
                try:
                    bot_data = load_user_data(str(self.bot.user.id), guild_id)
                except KeyError:
                    bot_data = None

                if user_data is None:
                    continue

                # Verificar si el bot_data existe, si no, inicializarlo
                if bot_data is None or 'balance' not in bot_data:
                    logging.warning(f"No se encontró balance para el bot en {guild.name}, inicializando con balance predeterminado.")
                    bot_data = {'balance': 100_000_000_000}  # Valor predeterminado
                    save_user_data(str(self.bot.user.id), guild_id, bot_data['balance'])

                balance = user_data['balance']

                # Si el saldo es 0 o negativo, darle un saldo base entre 10,000 y 100,000
                if balance <= 0:
                    balance = ra.randint(10_000, 1_000_000)
                    logging.info(f"{usuario.name} tenía saldo negativo o cero. Se le ha asignado un saldo base de {balance}.")
                    user_data['balance'] = balance
                    save_user_data(user_id, guild_id, user_data['balance'])

                perder = ra.choice([True, False])  # 50% de probabilidad de ganar o perder
                limit_loss = ra.uniform(0.03, give_money_limits["max_percentage_loss"])
                limit_win = ra.uniform(0.01, give_money_limits["max_percentage_win"])

                if perder:
                    cantidad = -(ra.uniform(balance * 0.02, balance * limit_loss))
                else:
                    cantidad = ra.uniform(balance * 0.01, balance * limit_win)

                # Verificar si el bot tiene suficiente saldo
                if bot_data['balance'] < abs(cantidad):
                    logging.warning(f"El bot no tiene suficiente saldo para enviar {cantidad} MelladoCoins.")
                    return  # Salir si no hay suficiente saldo en el bot

                # Ajustar el balance del usuario y el bot
                logging.info(f"Enviando {cantidad:.2f} MelladoCoins a {usuario.name} en {guild.name}")
                user_data['balance'] += cantidad
                bot_data['balance'] -= cantidad

                # Guardar los nuevos balances
                logging.info(f"Nuevo saldo de {usuario.name}: {user_data['balance']:.2f}")
                save_user_data(user_id, guild_id, user_data['balance'])
                save_user_data(str(self.bot.user.id), guild_id, bot_data['balance'])

                balance_formatted = f"${user_data['balance']:,.0f}".replace(",", ".")

                embed = discord.Embed(
                    title="💰 MelladoCoins" if cantidad > 0 else "💸 MelladoCoins"
                )

                # Verificar si el usuario tiene un avatar personalizado o usar el predeterminado
                if usuario.avatar:
                    embed.set_thumbnail(url=usuario.avatar.url)
                else:
                    embed.set_thumbnail(url=usuario.default_avatar.url)

                cantidad_formateada = f"${abs(cantidad):,.0f}".replace(",", ".")
                if cantidad > 0:
                    embed.add_field(name="¡Felicidades!", value=f"¡{usuario.name} ha recibido {cantidad_formateada} MelladoCoins!", inline=False)
                else:
                    embed.add_field(name="Tiene que irse a parvularia.", value=f"¡{usuario.name} ha perdido {cantidad_formateada} MelladoCoins!", inline=False)

                embed.add_field(name="Nuevo Saldo", value=f"{balance_formatted} MelladoCoins", inline=False)
                await channel.send(embed=embed)

        except Exception as e:
            logging.error("Error en mellado_coins_task:", exc_info=e)

    @tasks.loop(hours=24)
    async def central_bank_task(self):
        try:
            for guild in self.bot.guilds:
                guild_id = str(guild.id)
                channel_id = load_channel_setting(guild_id)  # Cargar la configuración del canal

                # Si no hay un canal configurado, selecciona el primer canal disponible
                if channel_id is None:
                    channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                    if channel:
                        channel_id = channel.id
                        save_channel_setting(guild_id, channel_id)  # Guarda este canal como el predeterminado
                    else:
                        logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                        continue
                else:
                    channel = self.bot.get_channel(channel_id)
                    if not channel or not channel.permissions_for(guild.me).send_messages:
                        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                        if channel:
                            channel_id = channel.id
                            save_channel_setting(guild_id, channel_id)  # Guarda este nuevo canal como el predeterminado
                        else:
                            logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                            continue

                bot_data = load_user_data(str(self.bot.user.id), guild_id)

                # Verificar si el bot_data existe, si no, inicializarlo
                if bot_data is None:
                    logging.warning(f"No se encontró balance para el bot en {guild.name}, inicializando con balance predeterminado.")
                    bot_data = {'balance': 100000000000}  # Valor predeterminado
                    insert_bot_data(self.bot.user.id, guild_id, bot_data['balance'])

                # Obtener el crecimiento del banco central
                key = ra.choice(list(growth_limits.keys()))
                value = growth_limits[key]

                new_balance = bot_data['balance'] * (1 + value)

                bot_data['balance'] = new_balance
                save_user_data(str(self.bot.user.id), guild_id, bot_data['balance'])

                balance_formatted = f"${bot_data['balance']:,.0f}".replace(",", ".")

                embed = discord.Embed(title="💰 Banco Central")
                embed.add_field(name="¡El Banco Central ha crecido!",
                                value=f"El Banco Central ha crecido un {value * 100:.2f}%",
                                inline=False)
                embed.add_field(name="Nuevo Saldo",
                                value=f"{balance_formatted} MelladoCoins",
                                inline=False)
                embed.set_thumbnail(url=self.bot.user.avatar.url)
                await channel.send(embed=embed)

        except Exception as e:
            logging.error(f"Error procesando el Banco Central en {guild.name}:", exc_info=e)

    @passive_income.before_loop
    async def before_passive_income(self):
        await self.bot.wait_until_ready()

    @mellado_coins_task.before_loop
    async def before_mellado_coins_task(self):
        await self.bot.wait_until_ready()

    @central_bank_task.before_loop
    async def before_central_bank_task(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Bot is ready. Verifying members registration...")

        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            logging.info(f"Processing guild: {guild.name} (ID: {guild_id})")

            # Verificar y registrar a todos los miembros que no son bots
            for member in guild.members:
                if not member.bot:
                    user_id = str(member.id)
                    key = f"{user_id}_{guild_id}"

                    logging.info(f"Checking registration for user: {member.name} (ID: {user_id}) in guild {guild.name}")

                    if key not in self.data:
                        self.data[key] = {'guild_id': guild_id, 'balance': 50000}
                        save_user_data(user_id, guild_id, 50000)
                        logging.info(f"Registering user {member.name} (ID: {user_id}) with balance 50000 in guild {guild.name}")
                        set_balance(user_id, guild_id, 50000)

            # Registrar al bot en este servidor (guild) con balance inicial
            bot_id = str(self.bot.user.id)
            bot_data = load_user_data(bot_id, guild_id)

            if bot_data is None:
                logging.warning(f"No se encontró balance para el bot en {guild.name}, inicializando con balance predeterminado.")
                self.data[f"{bot_id}_{guild_id}"] = {'guild_id': guild_id, 'balance': 100000000000}
                set_balance(bot_id, guild_id, 100000000000)
                logging.warning(f"{guild.name} - {guild_id}: {self.data}")
            else:
                logging.info(f"Bot ya registrado en {guild.name} (ID: {guild_id}) con balance existente.")


async def setup(bot):
    await bot.add_cog(Economy(bot))
