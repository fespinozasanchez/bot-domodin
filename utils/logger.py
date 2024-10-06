import logging


def setup_logger():
    # Logger para discord.log (logs generales del bot)
    discord_handler = logging.FileHandler(
        filename='logs/discord.log', encoding='utf-8', mode='w')
    discord_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    discord_handler.setFormatter(discord_formatter)

    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO)
    discord_logger.addHandler(discord_handler)

    # Logger para commands.log (logs de los comandos ejecutados)
    command_handler = logging.FileHandler(
        filename='logs/commands.log', encoding='utf-8', mode='a')  # modo 'a' para añadir al archivo
    command_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    command_handler.setFormatter(command_formatter)

    command_logger = logging.getLogger('command_logger')
    command_logger.setLevel(logging.INFO)
    command_logger.addHandler(command_handler)

    # Eliminar la propagación para que los logs de comandos no vayan al logger global
    command_logger.propagate = False

    # Logger para mensajes generales que se estaban mostrando en pantalla
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Desactivamos cualquier handler existente en root logger (que podría estar escribiendo a la consola)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
