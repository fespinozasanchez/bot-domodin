import mysql.connector
from mysql.connector import Error
import logging
from contextlib import closing
from config import DATABASE_CONFIG
import time


def connect_db():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        logging.error(f"Error: {e}")
        return None


def retry_query(func, *args, **kwargs):
    delay = 0.1
    for _ in range(5):  # Intentar hasta 5 veces
        try:
            return func(*args, **kwargs)
        except Error as e:
            if "Lock wait timeout exceeded" in str(e):
                time.sleep(delay)
                delay *= 2  # Aumentar el tiempo de espera exponencialmente
            else:
                raise
    raise Exception("Persistent database lock error")


def create_channel_table():
    def create():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS channel_settings (
                        guild_id VARCHAR(255) PRIMARY KEY,
                        channel_id BIGINT
                    )
                ''')
                conn.commit()
            conn.close()

    retry_query(create)


def save_channel_setting(guild_id, channel_id):
    def save():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    INSERT INTO channel_settings (guild_id, channel_id)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE channel_id=%s
                ''', (guild_id, channel_id, channel_id))
                conn.commit()
            conn.close()

    retry_query(save)


def load_channel_setting(guild_id):
    def load():
        conn = connect_db()
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute(
                    'SELECT channel_id FROM channel_settings WHERE guild_id=%s', (guild_id,))
                result = cursor.fetchone()
            conn.close()
            if result:
                return result['channel_id']
            return None

    return retry_query(load)


# Crear la tabla al cargar el módulo
create_channel_table()
