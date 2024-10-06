import logging


def setup_logger():
    handler = logging.FileHandler(
        filename='logs/discord.log', encoding='utf-8', mode='w')

    # Configuración del formato con fecha y hora
    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'  # Incluyendo fecha y hora
    )
