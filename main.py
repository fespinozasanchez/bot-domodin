from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import logging

handler = logging.FileHandler(
    filename='logs/discord.log', encoding='utf-8', mode='w')


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   description="this is a bot the Caro", intents=intents)


# Ping-pong
@bot.command()
async def ping(ctx):
    await ctx.send('pong')


# Hello
@bot.command()
async def hello(ctx):
    embed = discord.Embed()
    embed.title = "Hola mis queridos estudiantes,"
    embed.description = "los invito a estudiar un entretenido curso de Pascal, un potententisimo lenguaje de programación: [CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT](https://www.youtube.com/watch?v=yvFCI2whgOA)."
    embed.color =   embed.color = discord.Color.from_rgb(251, 141, 25)
    embed.set_thumbnail(url="https://jomerlisriera.files.wordpress.com/2015/03/lazarus_logo_new.png")
    await ctx.send(embed=embed)
    # await ctx.send('Hola mis estudiantes, vengan a estudiar conmigo, Pascal un potententisimo lenguaje de programación')
# https://www.youtube.com/watch?v=yvFCI2whgOA


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='[CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT]'), status=discord.Status.dnd)
    print(f'We have logged in as {bot.user}')


bot.run(token, log_handler=handler)
