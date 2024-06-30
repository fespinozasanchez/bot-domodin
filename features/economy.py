from discord.ext import commands, tasks
from utils.data_manager import load_user_data, save_user_data, load_all_users
import logging


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_all_users()
        self.passive_income.start()

    @commands.command(name='registrar')
    async def register_user(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.data:
            await ctx.send(f'{ctx.author.name}, ya estás registrado.')
        else:
            self.data[user_id] = {'balance': 1000}
            save_user_data(user_id, 1000)
            await ctx.send(f'{ctx.author.name}, has sido registrado con un saldo inicial de 1000 pesos chilenos.')

    @commands.command(name='saldo')
    async def check_balance(self, ctx):
        user_id = str(ctx.author.id)
        user_data = load_user_data(user_id)
        if user_data:
            balance = user_data['balance']
            await ctx.send(f'{ctx.author.name}, tu saldo es {balance} pesos chilenos.')
        else:
            await ctx.send(f'{ctx.author.name}, no estás registrado. Usa el comando !registrar para registrarte.')

    def update_balance(self, user_id, amount):
        user_data = load_user_data(user_id)
        if user_data:
            user_data['balance'] += amount
            save_user_data(user_id, user_data['balance'])

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            user_id = str(message.author.id)
            if user_id in self.data:
                self.update_balance(user_id, 0.1)

    @tasks.loop(minutes=5)
    async def passive_income(self):
        for user_id in self.data:
            self.update_balance(user_id, 0.01)

    @passive_income.before_loop
    async def before_passive_income(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Economy(bot))
