import logging


def setup_logger():
    # Logger para discord.log
    handler = logging.FileHandler(
        filename='logs/discord.log', encoding='utf-8', mode='w')

    # Logger para commands.log
    command_handler = logging.FileHandler(
        filename='logs/commands.log', encoding='utf-8', mode='a')  # modo 'a' para añadir al archivo

    # Configuración del formato con fecha y hora
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Configuración para discord.log
    handler.setFormatter(formatter)

    # Configuración para commands.log
    command_handler.setFormatter(formatter)

    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'  # Incluyendo fecha y hora
    )

    # Logger específico para comandos
    command_logger = logging.getLogger('command_logger')
    command_logger.setLevel(logging.INFO)
    command_logger.addHandler(command_handler)
