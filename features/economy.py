import io
import numpy as np
import matplotlib.pyplot as plt
import discord
from discord.ext import commands, tasks
from utils.data_manager import load_user_data, save_user_data, load_all_users
import logging
import matplotlib
import random as ra
from utils.channel_manager import save_channel_setting, load_channel_setting
matplotlib.use('Agg')

logging.basicConfig(level=logging.DEBUG)


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_all_users()
        self.passive_income.start()
        self.mellado_coins_task.start()

    @commands.command(name='registrar')
    async def register_user(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        # Asegúrate de que la clave se forma correctamente
        key = f"{user_id}_{guild_id}"
        user_data = load_user_data(user_id, guild_id)
        if user_data:
            await ctx.send(f'{ctx.author.name}, ya estás registrado.')
        else:
            self.data[key] = {'guild_id': guild_id, 'balance': 1000}
            save_user_data(user_id, guild_id, 1000)
            await ctx.send(f'{ctx.author.name}, has sido registrado con un saldo inicial de 1000 MelladoCoins.')

    @commands.command(name='saldo')
    async def check_balance(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user_data = load_user_data(user_id, guild_id)
        if user_data:
            balance = user_data['balance']
            await ctx.send(f'{ctx.author.name}, tu saldo es {balance} MelladoCoins.')
        else:
            await ctx.send(f'{ctx.author.name}, no estás registrado. Usa el comando !registrar para registrarte.')

    @commands.command(name='grafico_saldos')
    async def grafico_saldos(self, ctx):
        guild_id = str(ctx.guild.id)
        all_users = load_all_users(guild_id)
        user_names = []
        balances = []
        for user_key, user_data in all_users.items():
            user = await self.bot.fetch_user(user_key.split('_')[0])
            user_names.append(user.name)
            balances.append(user_data['balance'])

        # Configuración del gráfico
        plt.figure(figsize=(12, 8))
        bars = plt.bar(user_names, balances, color=plt.cm.viridis(
            np.linspace(0, 1, len(user_names))))

        plt.xlabel('Usuarios', fontsize=14)
        plt.ylabel('Saldo (MelladoCoins)', fontsize=14)
        plt.title(f'Saldo de Usuarios en {ctx.guild.name}', fontsize=16)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Añadir etiquetas a las barras
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2),
                     ha='center', va='bottom', fontsize=10, color='black')

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        file = discord.File(buf, filename='grafico_saldos.png')
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
                logging.error(
                    f"Key '{key}' does not have the expected format 'user_id_guild_id'")

    @commands.command(name='set_channel')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        save_channel_setting(guild_id, channel.id)
        await ctx.send(f"Canal configurado a {channel.mention} para los mensajes de MelladoCoins.")
        logging.info(f"Canal configurado en {ctx.guild.name}: {channel.name}")

    @tasks.loop(minutes=60)
    async def mellado_coins_task(self):
        try:
            logging.debug("mellado_coins_task is running.")
            for guild in self.bot.guilds:
                guild_id = str(guild.id)
                channel_id = load_channel_setting(guild_id)  # Cargar la configuración del canal

                # Si no hay un canal configurado, selecciona el primer canal disponible
                if channel_id is None:
                    channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                    if channel:
                        channel_id = channel.id
                        save_channel_setting(guild_id, channel_id)  # Guarda este canal como el predeterminado
                        logging.info(f"Usando {channel.name} como canal por defecto en {guild.name}.")
                    else:
                        logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                        continue
                else:
                    channel = self.bot.get_channel(channel_id)
                    if not channel or not channel.permissions_for(guild.me).send_messages:
                        # Si el canal configurado ya no es válido, busca otro canal
                        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                        if channel:
                            channel_id = channel.id
                            save_channel_setting(guild_id, channel_id)  # Guarda este nuevo canal como el predeterminado
                            logging.info(f"Canal {channel.name} seleccionado como predeterminado en {guild.name}.")
                        else:
                            logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                            continue

                members = [member for member in guild.members if not member.bot]
                if not members:
                    continue

                usuario = ra.choice(members)
                user_id = str(usuario.id)
                user_data = load_user_data(user_id, guild_id)

                if user_data is None:
                    continue

                cantidad = ra.randint(-100, 100)
                user_data['balance'] += cantidad
                save_user_data(user_id, guild_id, user_data['balance'])

                if cantidad > 0:
                    await channel.send(f'¡<@{usuario.id}> es un ingeniero duro! y como es duro le voy a dar {cantidad} MelladoCoins. Tu nuevo saldo es {user_data["balance"]} MelladoCoins.')
                else:
                    await channel.send(f'<@{usuario.id}> tiene que irse a parvularia. Le he quitado {-cantidad} MelladoCoins. Tu nuevo saldo es {user_data["balance"]} MelladoCoins.')
        except Exception as e:
            logging.error("Error en mellado_coins_task:", exc_info=e)

    @passive_income.before_loop
    async def before_passive_income(self):
        await self.bot.wait_until_ready()

    @mellado_coins_task.before_loop
    async def before_mellado_coins_task(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        logging.debug("Bot is ready. Verifying members registration...")
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            for member in guild.members:
                if not member.bot:
                    user_id = str(member.id)
                    key = f"{user_id}_{guild_id}"
                    if key not in self.data:
                        self.data[key] = {
                            'guild_id': guild_id, 'balance': 1000}
                        save_user_data(user_id, guild_id, 1000)


async def setup(bot):
    await bot.add_cog(Economy(bot))
