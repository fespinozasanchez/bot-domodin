import os
import logging
import sys
import signal
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from a_queue.audio_queue import AudioQueue
from commands import fun_commands
from utils.custom_help import CustomHelpCommand
from utils.logger import setup_logger
from utils.reminder_manager import ReminderManager
from features import copa_america


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
intents.members = True
intents.message_content = True

# Crear instancia del bot
bot = commands.Bot(command_prefix='!', description="this is a bot the Caro",
                   intents=intents, help_command=CustomHelpCommand())

# Crear instancia de ReminderManager
reminder_manager = ReminderManager()
copa_america.register_commands(bot)
# Registrar comandos
fun_commands.register_commands(bot)


async def load_cogs():
    await bot.load_extension('cogs.hangman')
    await bot.load_extension('commands.music_commands')
    await bot.load_extension('features.betting_system')
    await bot.load_extension('features.economy')
    await bot.load_extension('moderation.moderation_commands')
    await bot.load_extension('commands.reminder_commands')
    # Nuevo módulo agregado aquí
    await bot.load_extension('features.prediction_system')


@tasks.loop(seconds=60)
async def check_reminders():
    await reminder_manager.check_reminders(bot)


@bot.event
async def on_ready():
    check_reminders.start()
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching,
                                  name='[CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT]'),
        status=discord.Status.dnd
    )
    print(f'We have logged in as {bot.user}')


async def main():
    setup_logger()
    await load_cogs()
    await bot.start(token)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
