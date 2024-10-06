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
token = os.getenv('DISCORD_TOKEN_DEVELOP')

# Configurar intentos de Discord
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Crear instancia del bot
bot = commands.Bot(command_prefix='!', description="this is a bot the Caro",
                   intents=intents, help_command=CustomHelpCommand())

# Crear instancia de ReminderManager
reminder_manager = ReminderManager()

# Registrar comandos
copa_america.register_commands(bot)
fun_commands.register_commands(bot)


async def load_cogs():
    cogs = [
        'cogs.hangman',
        'commands.music_commands',
        'features.betting_system',
        'features.economy',
        'moderation.moderation_commands',
        'commands.reminder_commands',
        'features.prediction_system',
        'commands.rpg_commands',
        'riot.leagueoflegends',
        'commands.market_commands'
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'Loaded cog: {cog}')
        except Exception as e:
            print(f'Failed to load cog {cog}: {e}')


@tasks.loop(seconds=60)
async def check_reminders():
    await reminder_manager.check_reminders(bot)


@bot.event
async def on_ready():
    # Inicia la tarea de recordatorios
    check_reminders.start()

    # Cambia la presencia del bot
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching,
                                  name='Dom domo din, el sabio dueño de Domodin, está vigilando...'),
        status=discord.Status.dnd
    )

    # Sincroniza los slash commands
    try:
        await bot.tree.sync()  # Sincroniza los comandos en Discord
        print(f"Slash commands synced successfully.")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")

    # Mensaje cuando el bot esté listo
    print(f'We have logged in as {bot.user}')


# Evento para registrar todos los comandos ejecutados
@bot.event
async def on_command(ctx):
    # Obtén el logger para comandos
    command_logger = logging.getLogger('command_logger')

    # Registrar información sobre el comando ejecutado
    command_logger.info(f'Comando ejecutado: {ctx.command} - Usuario: {ctx.author} - Servidor: {ctx.guild.name}')


async def main():
    @bot.command()
    async def sync(ctx):
        await bot.tree.sync()
        await ctx.send("Sincronizado")

    try:
        setup_logger()  # Configura el logger
        await load_cogs()
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        await bot.close()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
