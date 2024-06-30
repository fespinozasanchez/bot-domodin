import os
import logging
import sys
import signal
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from a_queue.audio_queue import AudioQueue
from utils.logger import setup_logger
from commands import fun_commands, music_commands, reminder_commands
from utils.reminder_manager import ReminderManager


def def_handler(sig, frame):
    print("\n\n[!] Saliendo...\n")
    sys.exit(1)


# Ctrl+C
signal.signal(signal.SIGINT, def_handler)

# Cargar variables de entorno
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Configurar intentos de Discord
intents = discord.Intents.default()
intents.message_content = True

# Crear instancia del bot
bot = commands.Bot(command_prefix='!',
                   description="this is a bot the Caro", intents=intents)

# Instanciar las clases necesarias
audio_queue = AudioQueue()
reminder_manager = ReminderManager()

# Registrar comandos
fun_commands.register_commands(bot)
music_commands.register_commands(bot, audio_queue)
reminder_commands.register_commands(bot, reminder_manager)
# chat_commands.register_commands(bot)

# Función asíncrona para cargar los cogs


async def load_cogs():
    await bot.load_extension('cogs.hangman')
    await bot.load_extension('features.betting_system')  # Cargar el nuevo cog
    # Cargar el nuevo cog de economía
    await bot.load_extension('features.economy')


@tasks.loop(seconds=60)
async def check_reminders():
    await reminder_manager.check_reminders(bot)


@bot.event
async def on_ready():
    check_reminders.start()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='[CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT]'), status=discord.Status.dnd)
    print(f'We have logged in as {bot.user}')


async def main():
    # Configurar el logger
    setup_logger()
    # Cargar los cogs
    await load_cogs()
    # Ejecutar el bot
    await bot.start(token)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
