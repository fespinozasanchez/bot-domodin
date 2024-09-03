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


def create_tables_if_not_exist():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS predicciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pregunta VARCHAR(255) NOT NULL,
            fecha_limite DATE NOT NULL,
            creador_id BIGINT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS votos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            prediction_id INT NOT NULL,
            voto ENUM('si', 'no') NOT NULL,
            FOREIGN KEY (prediction_id) REFERENCES predicciones(id)
        );
        """
    ]

    conn = connect_db()
    if conn:
        try:
            with closing(conn.cursor()) as cursor:
                for query in queries:
                    cursor.execute(query)
            conn.commit()
            logging.info("Tablas verificadas o creadas exitosamente.")
        except Error as e:
            logging.error(f"Error al crear/verificar tablas: {e}")
        finally:
            conn.close()
    else:
        logging.error(
            "No se pudo conectar a la base de datos para verificar/crear tablas.")


def create_prediction(pregunta, fecha_limite, creador_id):
    query = "INSERT INTO predicciones (pregunta, fecha_limite, creador_id) VALUES (%s, %s, %s)"
    conn = connect_db()
    if conn:
        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute(query, (pregunta, fecha_limite, creador_id))
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            logging.error(f"Error al crear predicción: {e}")
        finally:
            conn.close()
    return None


def cast_vote(user_id, prediction_id, vote):
    query_check = "SELECT * FROM votos WHERE user_id = %s AND prediction_id = %s"
    query_insert = "INSERT INTO votos (user_id, prediction_id, voto) VALUES (%s, %s, %s)"

    conn = connect_db()
    if conn:
        try:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute(query_check, (user_id, prediction_id))
                existing_vote = cursor.fetchone()

                if existing_vote:
                    return False  # Ya ha votado

                cursor.execute(query_insert, (user_id, prediction_id, vote))
                conn.commit()
                return True
        except Error as e:
            logging.error(f"Error al registrar voto: {e}")
        finally:
            conn.close()
    return False


def get_all_predictions():
    query = """
    SELECT p.id, p.pregunta, p.fecha_limite,
           SUM(CASE WHEN v.voto = 'si' THEN 1 ELSE 0 END) AS votos_si,
           SUM(CASE WHEN v.voto = 'no' THEN 1 ELSE 0 END) AS votos_no
    FROM predicciones p
    LEFT JOIN votos v ON p.id = v.prediction_id
    GROUP BY p.id
    """

    conn = connect_db()
    if conn:
        try:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Error as e:
            logging.error(f"Error al obtener predicciones: {e}")
        finally:
            conn.close()
    return []


# Asegúrate de llamar a esta función al iniciar tu aplicación.
create_tables_if_not_exist()
