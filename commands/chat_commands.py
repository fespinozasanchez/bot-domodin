import discord
from discord.ext import commands
from TransformerModule.GPT import talkFunction


def register_commands(bot, chat_message):
    @bot.command(help="Preguntale algo al bot de dudosa reputación") 
    async def chat(ctx, message: str):
        try:
            msg=talkFunction(message)
           
            await ctx.send(msg)
        except ValueError:
            await ctx.send("Algo salio mal uwu")