import discord
from discord.ext import commands, tasks
from utils.data_manager import load_user_data, save_user_data, load_all_users
import logging

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_all_users()
        self.passive_income.start()

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

    @tasks.loop(minutes=5)
    async def passive_income(self):
        for key, user_data in self.data.items():
            try:
                user_id, guild_id = key.split("_")
                self.update_balance(user_id, guild_id, 0.01)
            except ValueError:
                logging.error(
                    f"Key '{key}' does not have the expected format 'user_id_guild_id'")

    @passive_income.before_loop
    async def before_passive_income(self):
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
