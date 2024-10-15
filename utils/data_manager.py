from datetime import datetime
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
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        guild_id VARCHAR(255) NOT NULL,
                        balance DOUBLE NULL,
                        last_loan_time DATETIME NULL,
                        loan_amount FLOAT DEFAULT 0,
                        loan_due_time DATETIME NULL,
                        roulette_status DATETIME NULL,
                        roulette_available BOOLEAN DEFAULT True,
                        UNIQUE KEY unique_user_guild (user_id, guild_id)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bets (
                        user_id VARCHAR(255) PRIMARY KEY,
                        equipo VARCHAR(255),
                        cantidad FLOAT,
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        reminder_time DATETIME,
                        message TEXT,
                        channel_id BIGINT
                    )
                ''')
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
        # Asegúrate de que 'last_loan_time' y 'loan_due_time' se manejen correctamente
        last_loan_time = user_data.get('last_loan_time')
        loan_due_time = user_data.get('loan_due_time')
        roulette_status = user_data.get('roulette_status')

        # Convertir las fechas a objetos datetime si son cadenas
        if last_loan_time and isinstance(last_loan_time, str):
            last_loan_time = datetime.fromisoformat(last_loan_time)
        if loan_due_time and isinstance(loan_due_time, str):
            loan_due_time = datetime.fromisoformat(loan_due_time)
        if roulette_status and isinstance(roulette_status, str):
            roulette_status = datetime.fromisoformat(roulette_status)

        return {
            'id': user_data['id'],
            'user_id': user_data['user_id'],
            'guild_id': user_data['guild_id'],
            'balance': user_data['balance'],
            'last_loan_time': last_loan_time,
            'loan_amount': user_data.get('loan_amount', 0),
            'loan_due_time': loan_due_time,  # Puede ser None si no se ha solicitado préstamo antes
            'roulette_status': roulette_status,
            'roulette_available': user_data.get('roulette_available', False)
        }
    return None


def save_user_data(user_id, guild_id, balance):
    def save():
        conn = connect_db()
        if conn:
            conn.autocommit = True  # Activar autocommit
            with closing(conn.cursor()) as cursor:
                query = '''
                UPDATE users 
                SET balance = %s 
                WHERE user_id = %s 
                AND guild_id = %s
                '''
                # logging.info(f"Ejecutando consulta: {query} con valores: {balance}, {user_id}, {guild_id}")
                cursor.execute(query, (balance, user_id, guild_id))  # Utiliza los placeholders correctamente
                conn.commit()
            conn.close()

    retry_query(save)


def set_balance(user_id, guild_id, balance):
    def save():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                query = '''
                INSERT INTO users (user_id, guild_id, balance)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE balance = VALUES(balance)
                '''
                cursor.execute(query, (user_id, guild_id, balance))
                conn.commit()
            conn.close()

    retry_query(save)


def save_loan_data(user_id, guild_id, balance, last_loan_time, loan_amount, loan_due_time):
    # logging.info(f"Guardando datos de préstamo para el usuario: {user_id}, guild: {guild_id}, balance: {balance}, last_loan_time: {last_loan_time}, loan_amount: {loan_amount}, loan_due_time: {loan_due_time}")

    def save():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    '''
                    UPDATE users 
                    SET balance=%s, last_loan_time=%s, loan_amount=%s, loan_due_time=%s 
                    WHERE user_id=%s AND guild_id=%s
                    ''', (balance, last_loan_time, loan_amount, loan_due_time, user_id, guild_id)
                )
                conn.commit()
                # logging.info(f"Datos de préstamo guardados correctamente para el usuario {user_id} en el servidor {guild_id}")
            conn.close()

    retry_query(save)


def save_roulette_status(user_id, guild_id, roulette_status, roulette_available):
    def save():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    '''
                    UPDATE users 
                    SET roulette_status=%s, roulette_available=%s
                    WHERE user_id=%s AND guild_id=%s
                    ''', (roulette_status, roulette_available, user_id, guild_id)
                )
                conn.commit()
            conn.close()

    retry_query(save)

def load_all_users(guild_id=None):
    def load_all():
        conn = connect_db()
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                # Definir la consulta basada en si se proporciona guild_id
                query = 'SELECT id, user_id, guild_id, balance, last_loan_time, loan_amount, loan_due_time, roulette_status, roulette_available FROM users'

                if guild_id:
                    query += ' WHERE guild_id=%s'
                    cursor.execute(query, (guild_id,))
                else:
                    cursor.execute(query)

                # Obtener todos los resultados
                users = cursor.fetchall()
            conn.close()
            return users

    all_users = retry_query(load_all)

    # Convertir los resultados en un diccionario con todos los campos relevantes
    return {
        f"{user['user_id']}_{user['guild_id']}": {
            'id': user['id'],
            'guild_id': user['guild_id'],
            'balance': user['balance'],
            'last_loan_time': user['last_loan_time'],
            'loan_amount': user['loan_amount'],
            'loan_due_time': user['loan_due_time'],
            'roulette_status': user['roulette_status'],
            'roulette_available': user['roulette_available']
        }
        for user in all_users
    }


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
