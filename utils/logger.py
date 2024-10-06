import logging


def setup_logger():
    # Logger para discord.log (logs generales del bot)
    discord_logger = logging.getLogger('discord')
    if not discord_logger.handlers:  # Evitar múltiples handlers
        discord_handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
        discord_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        discord_handler.setFormatter(discord_formatter)
        discord_logger.setLevel(logging.INFO)
        discord_logger.addHandler(discord_handler)

    # Logger para commands.log
    command_logger = logging.getLogger('command_logger')
    if not command_logger.handlers:  # Evitar múltiples handlers
        command_handler = logging.FileHandler(filename='logs/commands.log', encoding='utf-8', mode='a')
        command_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        command_handler.setFormatter(command_formatter)
        command_logger.setLevel(logging.INFO)
        command_logger.addHandler(command_handler)

    # Eliminar handlers del root logger que imprimen en la consola
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
