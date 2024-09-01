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
                # Crear la tabla users primero
                cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    user_id VARCHAR(255),
                                    guild_id VARCHAR(255),
                                    balance FLOAT,
                                    PRIMARY KEY (user_id, guild_id)
                                  )''')
                # Luego crear la tabla items
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
                # Luego crear la tabla players con claves foráneas referenciadas
                cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                                    player_id INT AUTO_INCREMENT PRIMARY KEY,
                                    user_id VARCHAR(255),
                                    guild_id VARCHAR(255),
                                    level INT,
                                    experience FLOAT,
                                    health INT,
                                    mana INT,
                                    strength INT,
                                    intelligence INT,
                                    agility INT,
                                    FOREIGN KEY(user_id, guild_id) REFERENCES users(user_id, guild_id)
                                  )''')
                # Luego crear la tabla player_items
                cursor.execute('''CREATE TABLE IF NOT EXISTS player_items (
                                    player_item_id INT AUTO_INCREMENT PRIMARY KEY,
                                    player_id INT,
                                    item_id INT,
                                    quantity INT,
                                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                                    FOREIGN KEY(item_id) REFERENCES items(item_id)
                                  )''')
                # Luego crear la tabla skills
                cursor.execute('''CREATE TABLE IF NOT EXISTS skills (
                                    skill_id INTEGER AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(255),
                                    mana_cost INTEGER,
                                    damage INTEGER,
                                    cooldown INTEGER
                                  )''')
                # Finalmente, crear la tabla player_skills
                cursor.execute('''CREATE TABLE IF NOT EXISTS player_skills (
                                    player_skill_id INT AUTO_INCREMENT PRIMARY KEY,
                                    player_id INT,
                                    skill_id INT,
                                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                                    FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                                  )''')
                conn.commit()
            conn.close()

    retry_query(create)

def load_player_items(player_id):
    def load():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor(dictionary=True)) as cursor:
                    cursor.execute('SELECT * FROM player_items WHERE player_id=%s', (player_id,))
                    return cursor.fetchall()
            finally:
                conn.close()

    items = retry_query(load)
    return [{'item_id': item['item_id'], 'quantity': item['quantity']} for item in items]

def save_player_item(player_id, item_id, quantity):
    def save():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''INSERT INTO player_items (player_id, item_id, quantity)
                                      VALUES (%s, %s, %s)
                                      ON DUPLICATE KEY UPDATE quantity=%s''',
                                   (player_id, item_id, quantity, quantity))
                    conn.commit()
            except:
                conn.rollback()
                raise
            finally:
                conn.close()

    retry_query(save)

def load_player_skills(player_id):
    def load():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor(dictionary=True)) as cursor:
                    cursor.execute('SELECT * FROM player_skills WHERE player_id=%s', (player_id,))
                    return cursor.fetchall()
            finally:
                conn.close()

    skills = retry_query(load)
    return [{'skill_id': skill['skill_id']} for skill in skills]

def save_player_skill(player_id, skill_id):
    def save():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''INSERT INTO player_skills (player_id, skill_id)
                                      VALUES (%s, %s)
                                      ON DUPLICATE KEY UPDATE skill_id=%s''',
                                   (player_id, skill_id, skill_id))
                    conn.commit()
            except:
                conn.rollback()
                raise
            finally:
                conn.close()

    retry_query(save)



def register_player(user_id, guild_id, level, experience, health, mana, strength, intelligence, agility):
    def register():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('''INSERT INTO players (user_id, guild_id, level, experience, health, mana, strength, intelligence, agility)
                                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                   (user_id, guild_id, level, experience, health, mana, strength, intelligence, agility))
                    conn.commit()
            except Error as e:
                print(f"Error: {e}")
                conn.rollback()
            finally:
                conn.close()

    retry_query(register)

def get_player_stats(user_id):
    def load():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor(dictionary=True)) as cursor:
                    cursor.execute('''SELECT user_id, guild_id, level, experience, health, mana, strength, intelligence, agility
                                      FROM players
                                      WHERE user_id=%s''', (user_id,))
                    return cursor.fetchone()
            finally:
                conn.close()

    stats = retry_query(load)
    return stats

create_tables()
