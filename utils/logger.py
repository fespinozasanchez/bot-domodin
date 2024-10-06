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
        filename='logs/commands.log', encoding='utf-8', mode='a')
    command_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    command_handler.setFormatter(command_formatter)

    command_logger = logging.getLogger('command_logger')
    command_logger.setLevel(logging.INFO)
    command_logger.addHandler(command_handler)

    # Eliminar la propagación para que los logs de comandos no vayan al logger global
    command_logger.propagate = False

    # Configurar los logs de urllib3 para que vayan a discord.log
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.INFO)
    urllib3_logger.addHandler(discord_handler)  # Agregar handler para escribir en discord.log
    urllib3_logger.propagate = False

    # Remover handlers del root logger para que no imprima en la consola
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Evitar que root logger imprima en consola, pero permitir que lo haga en archivos
    root_logger.setLevel(logging.WARNING)
