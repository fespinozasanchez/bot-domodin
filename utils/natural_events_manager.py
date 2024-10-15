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
                    CREATE TABLE IF NOT EXISTS events_daily (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        current_event VARCHAR(255),
                        updated_at TIMESTAMP
                    )
                ''')
                conn.commit()
            conn.close()
    retry_query(create)




def get_current_natural_event():
    def query():
        conn = connect_db()
        current_event = None
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT current_event, updated_at FROM events_daily ORDER BY id DESC LIMIT 1')
                current_event = cursor.fetchone()
            conn.close()
        return current_event
    return retry_query(query)

def update_current_natural_event(event_name, fecha_cambio):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    INSERT INTO events_daily (current_event, updated_at)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE current_event = VALUES(current_event), updated_at = VALUES(updated_at)
                ''', (event_name, fecha_cambio))
                conn.commit()
            conn.close()
    retry_query(query)

# Crear las tablas si no existen
create_tables()