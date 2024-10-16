import logging


def setup_logger():
    # Configuración del logger global (root logger)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Nivel del root logger

    # Limpiar los handlers del root logger para evitar duplicaciones
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Logger para discord.log (logs generales del bot)
    discord_handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='a')
    discord_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    discord_handler.setFormatter(discord_formatter)
    root_logger.addHandler(discord_handler)  # Añadir el handler a root logger para discord.log

    # Logger para commands.log (logs de comandos)
    command_logger = logging.getLogger('command_logger')
    command_logger.setLevel(logging.INFO)

    if not command_logger.handlers:  # Evitar duplicación de handlers
        command_handler = logging.FileHandler(filename='logs/commands.log', encoding='utf-8', mode='a')
        command_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        command_handler.setFormatter(command_formatter)
        command_logger.addHandler(command_handler)

    # Desactivar la propagación para evitar que los logs de comandos vayan al root logger
    command_logger.propagate = False

    # Configurar urllib3 para que sus logs vayan a discord.log y no a la consola
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.INFO)
    if not urllib3_logger.handlers:
        urllib3_logger.addHandler(discord_handler)
    urllib3_logger.propagate = False  # Evitar propagación al root logger
