import logging


def setup_logger():
    # Logger para discord.log (logs generales del bot)
    discord_logger = logging.getLogger('discord')
    if not discord_logger.handlers:  # Evitar múltiples handlers
        discord_handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
        discord_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        discord_handler.setFormatter(discord_formatter)
        discord_logger.addHandler(discord_handler)
        discord_logger.setLevel(logging.INFO)

    # Logger para commands.log
    command_logger = logging.getLogger('command_logger')
    if not command_logger.handlers:  # Evitar múltiples handlers
        command_handler = logging.FileHandler(filename='logs/commands.log', encoding='utf-8', mode='a')
        command_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        command_handler.setFormatter(command_formatter)
        command_logger.addHandler(command_handler)
        command_logger.setLevel(logging.INFO)

    # Remover handlers del root logger para evitar impresión en consola
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Asegurarse de que no haya propagación hacia el root logger
    discord_logger.propagate = False
    command_logger.propagate = False

    # Configurar urllib3 para que vaya a discord.log
    urllib3_logger = logging.getLogger('urllib3')
    if not urllib3_logger.handlers:  # Evitar múltiples handlers
        urllib3_logger.addHandler(discord_handler)
        urllib3_logger.setLevel(logging.INFO)
        urllib3_logger.propagate = False
