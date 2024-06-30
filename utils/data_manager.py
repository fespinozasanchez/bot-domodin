import sqlite3
import os
import logging

DATABASE = 'features/db/economy.db'

# Configuración del logging
logging.basicConfig(level=logging.DEBUG)


def connect_db():
    if not os.path.exists('features/db'):
        os.makedirs('features/db')
    conn = sqlite3.connect(DATABASE)
    return conn


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        balance REAL
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bets (
                        user_id TEXT PRIMARY KEY,
                        equipo TEXT,
                        cantidad REAL,
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                      )''')
    conn.commit()
    conn.close()


def load_user_data(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return {'user_id': user_data[0], 'balance': user_data[1]}
    return None


def save_user_data(user_id, balance):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO users (user_id, balance) VALUES (?, ?)', (user_id, balance))
    conn.commit()
    conn.close()


def load_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()
    conn.close()
    return {user[0]: {'balance': user[1]} for user in all_users}


def load_bets():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bets')
    bets = cursor.fetchall()
    conn.close()
    return {bet[0]: {'equipo': bet[1], 'cantidad': bet[2]} for bet in bets}


def save_bet(user_id, equipo, cantidad):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO bets (user_id, equipo, cantidad) VALUES (?, ?, ?)',
                   (user_id, equipo, cantidad))
    conn.commit()
    conn.close()


def delete_bets():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bets')
    conn.commit()
    conn.close()


# Crear las tablas si no existen
create_tables()
