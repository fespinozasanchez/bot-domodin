import mysql.connector
from mysql.connector import Error
import logging
import time
from contextlib import closing
from config import DATABASE_CONFIG


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


def create_tables():
    def create():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    user_id VARCHAR(255),
                                    guild_id VARCHAR(255),
                                    balance FLOAT,
                                    PRIMARY KEY (user_id, guild_id)
                                  )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS bets (
                                    user_id VARCHAR(255) PRIMARY KEY,
                                    equipo VARCHAR(255),
                                    cantidad FLOAT,
                                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                                  )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    reminder_time DATETIME,
                                    message TEXT,
                                    channel_id BIGINT
                                  )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS items (
                                    item_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(255),
                                    item_type VARCHAR(255),
                                    description TEXT,
                                    price FLOAT,
                                    strength INTEGER,
                                    intelligence INTEGER,
                                    agility INTEGER,
                                    mana INTEGER,
                                    hp INTEGER
                                  )''')
                conn.commit()
            conn.close()

    retry_query(create)


def load_user_data(user_id, guild_id):
    def load():
        conn = connect_db()
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute(
                    'SELECT * FROM users WHERE user_id=%s AND guild_id=%s', (user_id, guild_id))
                return cursor.fetchone()
            conn.close()

    user_data = retry_query(load)
    if user_data:
        return {'user_id': user_data['user_id'], 'guild_id': user_data['guild_id'], 'balance': user_data['balance']}
    return None


def save_user_data(user_id, guild_id, balance):
    def save():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    'INSERT INTO users (user_id, guild_id, balance) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE balance=%s',
                    (user_id, guild_id, balance, balance))
                conn.commit()
            conn.close()

    retry_query(save)


# En utils/data_manager.py

def load_all_users(guild_id=None):
    def load_all():
        conn = connect_db()
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                if guild_id:
                    cursor.execute(
                        'SELECT * FROM users WHERE guild_id=%s', (guild_id,))
                else:
                    cursor.execute('SELECT * FROM users')
                return cursor.fetchall()
            conn.close()

    all_users = retry_query(load_all)
    return {f"{user['user_id']}_{user['guild_id']}": {'guild_id': user['guild_id'], 'balance': user['balance']} for user in all_users}


def load_bets():
    def load():
        conn = connect_db()
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT * FROM bets')
                return cursor.fetchall()
            conn.close()

    bets = retry_query(load)
    return {bet['user_id']: {'equipo': bet['equipo'], 'cantidad': bet['cantidad']} for bet in bets}


def save_bet(user_id, equipo, cantidad):
    def save():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('INSERT INTO bets (user_id, equipo, cantidad) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE equipo=%s, cantidad=%s',
                               (user_id, equipo, cantidad, equipo, cantidad))
                conn.commit()
            conn.close()

    retry_query(save)


def delete_bets():
    def delete():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('DELETE FROM bets')
                conn.commit()
            conn.close()

    retry_query(delete)


def save_reminder(reminder_time, message, channel_id):
    def save():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('INSERT INTO reminders (reminder_time, message, channel_id) VALUES (%s, %s, %s)',
                               (reminder_time, message, channel_id))
                conn.commit()
            conn.close()

    retry_query(save)


def load_reminders():
    def load():
        conn = connect_db()
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT * FROM reminders')
                return cursor.fetchall()
            conn.close()

    reminders = retry_query(load)
    return [{'id': r['id'], 'reminder_time': r['reminder_time'], 'message': r['message'], 'channel_id': r['channel_id']} for r in reminders]


def delete_reminder(reminder_id):
    def delete():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    'DELETE FROM reminders WHERE id=%s', (reminder_id,))
                conn.commit()
            conn.close()

    retry_query(delete)


# Crear las tablas si no existen
create_tables()
