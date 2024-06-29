import logging


def setup_logger():
    handler = logging.FileHandler(
        filename='logs/discord.log', encoding='utf-8', mode='w')
    logging.basicConfig(handlers=[handler], level=logging.INFO)
