from datetime import datetime
import mysql.connector
from mysql.connector import Error
import logging
import time
import random
from contextlib import closing
from config import DATABASE_CONFIG
from market_module.const_market import TIERS, COLORS, BARRIOS, NOMBRES_HOGAR, NOMBRES_TIENDA, NIVEL_WEIGHTS, TIER_WEIGHTS, BARRIO_WEIGHTS
from market_module.property_market import elegir_valor_ponderado_por_suerte, calcular_costo_mantenimiento, calcular_costo_diario, calcular_valor_compra, generar_controladores, calcular_desgaste, calcular_renta_diaria, calcular_suerte

# Conexión a la base de datos


def connect_db():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        logging.error(f"Error: {e}")
        return None

# Función para generar una propiedad aleatoria


def generar_propiedad(tipo):
    # Selección de nivel, tier y barrio usando distribuciones ponderadas
    suerte = calcular_suerte()
    # Nivel ajustado por suerte
    nivel = elegir_valor_ponderado_por_suerte([1, 2, 3, 4, 5], NIVEL_WEIGHTS, suerte)
    # Tier ajustado por suerte
    tier = elegir_valor_ponderado_por_suerte(list(TIERS.keys()), TIER_WEIGHTS, suerte)

    barrio = elegir_valor_ponderado_por_suerte(BARRIOS, BARRIO_WEIGHTS, suerte)

    tamaño = random.randint(2, 100 * nivel)  # A mayor nivel, mayor tamaño, pero no lineal
    pisos = random.randint(1, nivel * 2)  # Más pisos para niveles superiores
    desgaste = calcular_desgaste()
    color = random.choice(COLORS)

    # Generar controladores
    controladores = generar_controladores()

    porcentajes_colores = obtener_proporciones_barrio(barrio)

    # Nombre según tipo y nivel
    if tipo == "hogar":
        nombre = random.choice(NOMBRES_HOGAR[nivel])
        arrendada = False  # La propiedad hogar inicialmente no estará arrendada.
        es_residencia_principal = False
    else:
        nombre = random.choice(NOMBRES_TIENDA[nivel])
        arrendada = True
        es_residencia_principal = False

    # Calcular valores
    valor_compra = calcular_valor_compra(nivel, tier, tamaño, pisos, suerte)
    renta_diaria = calcular_renta_diaria(nivel, tier, suerte, desgaste, controladores, porcentajes_colores, color, valor_compra)
    costo_diario = calcular_costo_diario(nivel, tier, tamaño, pisos, suerte, renta_diaria)
    costo_mantenimiento = calcular_costo_mantenimiento(nivel, tier, tamaño, pisos, suerte)

    # Crear la propiedad
    propiedad = {
        "id": None,  # El ID se asignará cuando se inserte en la base de datos
        "tipo": tipo,
        "nombre": nombre,
        "nivel": nivel,
        "valor_compra": valor_compra,
        "renta_diaria": renta_diaria,
        "costo_diario": costo_diario,
        "costo_mantenimiento": costo_mantenimiento,
        "tier": tier,
        "barrio": barrio,
        "color": color,
        "tamaño": tamaño,
        "pisos": pisos,
        "suerte": suerte,
        "desgaste": desgaste,
        "desgaste_minimo": desgaste,  # El desgaste mínimo inicial es igual al desgaste actual
        "controladores": controladores,
        "arrendada": arrendada,  # Indica si la propiedad está arrendada
        "es_residencia_principal": es_residencia_principal  # Indica si la propiedad es la residencia principal
    }

    return propiedad


def obtener_propiedades_home(id_inversionista):
    def query():
        conn = connect_db()
        propiedades = []
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('''SELECT * FROM propiedades 
                                  WHERE inversionista_id = %s AND tipo = 'hogar' AND es_residencia_principal = 1 AND arrendada = 0''',
                               (id_inversionista,))
                propiedades = cursor.fetchall()
            conn.close()
        return propiedades
    return retry_query(query)


def obtener_id_inversionista(usuario_id, guild_id):
    def query():
        conn = connect_db()
        inversionista_id = None
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT id FROM users WHERE user_id = %s AND guild_id = %s', (usuario_id, guild_id))
                user_data = cursor.fetchone()
                if user_data:
                    user_id = user_data['id']
                    cursor.execute('SELECT id FROM inversionistas WHERE usuario_id = %s', (user_id,))
                    inversionista = cursor.fetchone()
                    if inversionista:
                        inversionista_id = inversionista['id']
            conn.close()
        return inversionista_id
    return retry_query(query)


# Intentar consultas con reintento en caso de errores de bloqueo
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


def create_property_tables():
    def create():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                # Tabla de inversionistas con clave foránea referenciada a la tabla users
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS inversionistas (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT,
                        penalizado BOOLEAN DEFAULT FALSE,
                        next_desgaste TIMESTAMP NULL,
                        next_renta TIMESTAMP NULL,
                        next_mantenimiento TIMESTAMP NULL,
                        next_costos_diarios TIMESTAMP NULL,
                        FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')

                # Tabla de propiedades con clave foránea a inversionistas
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS propiedades (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        inversionista_id INT,
                        tipo VARCHAR(255),
                        nombre VARCHAR(255),
                        nivel INT,
                        valor_compra FLOAT,
                        renta_diaria FLOAT,
                        costo_diario FLOAT,
                        costo_mantenimiento FLOAT,
                        tier VARCHAR(10),
                        barrio INT,
                        color VARCHAR(255),
                        tamaño INT,
                        pisos INT,
                        suerte FLOAT,
                        desgaste FLOAT,
                        desgaste_minimo FLOAT,
                        controladores VARCHAR(255),
                        arrendada BOOLEAN,
                        es_residencia_principal BOOLEAN,
                        FOREIGN KEY (inversionista_id) REFERENCES inversionistas(id) ON DELETE CASCADE
                    )
                ''')

                # Tabla de barrios con clave foránea a propiedades
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS barrios (
                        barrio_id INT,
                        color VARCHAR(255),
                        propiedad_id INT,
                        PRIMARY KEY (barrio_id, propiedad_id),
                        FOREIGN KEY (propiedad_id) REFERENCES propiedades(id) ON DELETE CASCADE
                    )
                ''')

                # Tabla para almacenar el evento global actual y la fecha de cambio del evento
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        current_event VARCHAR(255),
                        updated_at TIMESTAMP
                    )
                ''')

                conn.commit()
            conn.close()

    retry_query(create)


def get_current_event():
    def query():
        conn = connect_db()
        current_event = None
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT current_event, updated_at FROM events ORDER BY id DESC LIMIT 1')
                current_event = cursor.fetchone()
            conn.close()
        return current_event
    return retry_query(query)


def update_current_event(event_name, fecha_cambio):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''
                    INSERT INTO events (current_event, updated_at)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE current_event = VALUES(current_event), updated_at = VALUES(updated_at)
                ''', (event_name, fecha_cambio))
                conn.commit()
            conn.close()
    retry_query(query)


def register_investor(usuario_id, guild_id):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                try:
                    # Obtenemos el ID del usuario en base a user_id y guild_id
                    cursor.execute('SELECT id FROM users WHERE user_id = %s AND guild_id = %s', (usuario_id, guild_id))
                    user_data = cursor.fetchone()

                    if user_data:
                        user_id = user_data['id']
                        # Insertamos al usuario como inversionista con el id obtenido
                        cursor.execute('''INSERT INTO inversionistas (
                                        usuario_id, penalizado, 
                                        next_desgaste, next_renta, 
                                        next_mantenimiento, next_costos_diarios) 
                                        VALUES (%s, %s, %s, %s, %s, %s)''',
                                       (user_id, False, datetime.now(), datetime.now(), datetime.now(), datetime.now()))

                        conn.commit()

                        # Obtenemos el último ID insertado en la tabla inversionistas
                        cursor.execute('SELECT LAST_INSERT_ID() AS inversionista_id')
                        inversionista_data = cursor.fetchone()

                        if inversionista_data:
                            return inversionista_data['inversionista_id']  # Devolvemos el ID del inversionista registrado
                        else:
                            raise Exception("Error al obtener el ID del inversionista.")
                    else:
                        raise Exception("El usuario no fue encontrado en la tabla 'users'.")
                except Error as e:
                    conn.rollback()
                    raise Exception(f"Error al registrar inversionista: {str(e)}")
                finally:
                    conn.close()

    return retry_query(query)


# Guardar una propiedad en la base de datos


def guardar_propiedad(propiedad):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''INSERT INTO propiedades (
                                inversionista_id, tipo, nombre, nivel, valor_compra, renta_diaria, 
                                costo_diario, costo_mantenimiento, tier, barrio, color, 
                                tamaño, pisos, suerte, desgaste, desgaste_minimo, controladores,
                                arrendada, es_residencia_principal)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                               (propiedad['usuario_id'], propiedad['tipo'], propiedad['nombre'], propiedad['nivel'],
                                propiedad['valor_compra'], propiedad['renta_diaria'], propiedad['costo_diario'],
                                propiedad['costo_mantenimiento'], propiedad['tier'], propiedad['barrio'], propiedad['color'],
                                propiedad['tamaño'], propiedad['pisos'], propiedad['suerte'], propiedad['desgaste'],
                                propiedad['desgaste_minimo'], str(propiedad['controladores']), propiedad['arrendada'], propiedad['es_residencia_principal']))
                conn.commit()
            conn.close()
    retry_query(query)

# Obtener una propiedad de la base de datos por ID


def obtener_propiedad(id_propiedad):
    def load():
        conn = connect_db()
        propiedad = None
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT * FROM propiedades WHERE id = %s', (id_propiedad,))
                propiedad = cursor.fetchone()  # Guardar el resultado en una variable
            conn.close()  # Cerrar la conexión antes de retornar

        return propiedad  # Retornar el valor después de cerrar la conexión

    return retry_query(load)


def obtener_pagos():
    """
    The function `obtener_pagos` retrieves payment information from a database with a retry mechanism.
    :return: The function `obtener_pagos` is returning the result of calling the `retry_query` function
    with the `load` function as an argument.
    """
    def load():
        conn = connect_db()
        pagos = None
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT * FROM inversionistas')
                pagos = cursor.fetchall()
            conn.close()

        return pagos

    return retry_query(load)


# Obtener todas las propiedades de un usuario
def obtener_propiedades_por_usuario(inversionista_id):
    def query():
        conn = connect_db()
        propiedades = []
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT * FROM propiedades WHERE inversionista_id = %s', (inversionista_id,))
                propiedades = cursor.fetchall()
            conn.close()
        return propiedades
    return retry_query(query)


# Actualizar el desgaste de una propiedad y su mínimo en la base de datos
def actualizar_desgaste_propiedad(id_propiedad, nuevo_desgaste, nuevo_desgaste_minimo):
    def update():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor(dictionary=True)) as cursor:  # Aseguramos que el cursor devuelva un diccionario
                    # Actualizar el desgaste y el desgaste mínimo de la propiedad
                    cursor.execute('''UPDATE propiedades 
                                      SET desgaste = %s, desgaste_minimo = %s 
                                      WHERE id = %s''', (nuevo_desgaste, nuevo_desgaste_minimo, id_propiedad))

                    # Recalcular la renta diaria basada en el nuevo desgaste
                    recalcular_renta_diaria(cursor, id_propiedad)

                    conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    retry_query(update)

# Actualizar el estado de una propiedad para indicar si es residencia principal o no


def actualizar_estado_residencia_principal(propiedad_id, es_residencia_principal):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''UPDATE propiedades 
                                  SET es_residencia_principal = %s
                                  WHERE id = %s''', (es_residencia_principal, propiedad_id))
                conn.commit()
            conn.close()
    retry_query(query)

# Actualizar el estado de una propiedad para indicar si está arrendada o no


def actualizar_estado_propiedad_arrendada(propiedad_id, arrendada):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''UPDATE propiedades 
                                  SET arrendada = %s
                                  WHERE id = %s''', (arrendada, propiedad_id))
                conn.commit()
            conn.close()
    retry_query(query)

# Recalcular la renta diaria de una propiedad utilizando el cursor existente


def recalcular_renta_diaria(cursor, id_propiedad):
    cursor.execute('''SELECT nivel, tier, tamaño, pisos, suerte, desgaste, controladores, color, barrio, valor_compra
                      FROM propiedades WHERE id = %s''', (id_propiedad,))
    propiedad = cursor.fetchone()
    if propiedad:
        porcentajes_colores = obtener_proporciones_barrio(propiedad['barrio'])

        # Calcular la nueva renta
        nueva_renta = calcular_renta_diaria(
            propiedad['nivel'],
            propiedad['tier'],
            propiedad['suerte'],
            propiedad['desgaste'],
            propiedad['controladores'],
            porcentajes_colores,
            propiedad['color'],
            propiedad['valor_compra']
        )
        # Actualizar la renta diaria en la base de datos
        cursor.execute('''UPDATE propiedades SET renta_diaria = %s WHERE id = %s''',
                       (nueva_renta, id_propiedad))


# Actualizar los controladores de las propiedades en el barrio en la base de datos
# Actualizar propiedades del barrio y recalcular la renta
def actualizar_controladores_barrio(barrio_id, porcentajes):
    def query():
        conn = connect_db()
        if conn:
            try:
                with closing(conn.cursor(dictionary=True)) as cursor:
                    cursor.execute('''SELECT id, color FROM propiedades WHERE barrio = %s''', (barrio_id,))
                    propiedades = cursor.fetchall()

                    for propiedad in propiedades:
                        color = propiedad['color']
                        propiedad_id = propiedad['id']
                        controladores = [0, 0, 0, 0]

                        # Ajustar controladores según los porcentajes
                        if porcentajes.get(color, 0) > 50:
                            controladores[0] = 1
                        if porcentajes.get(color, 0) > 80:
                            controladores[1] = 1
                        if porcentajes.get(color, 0) < 20:
                            controladores[2] = 1

                        # Actualizar controladores en la propiedad
                        cursor.execute('''UPDATE propiedades SET controladores = %s WHERE id = %s''',
                                       (str(controladores), propiedad_id))

                        # Recalcular la renta dentro de la misma transacción
                        recalcular_renta_diaria(cursor, propiedad_id)

                    conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    retry_query(query)

# Obtener el saldo del usuario


def obtener_saldo_usuario(usuario_id, guild_id):
    def query():
        conn = connect_db()
        saldo = 0
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT balance FROM users WHERE user_id = %s AND guild_id = %s', (usuario_id, guild_id))
                usuario = cursor.fetchone()
                if usuario:
                    saldo = usuario['balance']
            conn.close()
        return saldo
    return retry_query(query)

# Actualizar el saldo del usuario


def actualizar_saldo_usuario(usuario_id, guild_id, nuevo_saldo):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('UPDATE users SET balance = %s WHERE user_id = %s AND guild_id = %s', (nuevo_saldo, usuario_id, guild_id))
                conn.commit()
            conn.close()
    retry_query(query)

# Obtener las proporciones de colores en un barrio
# Obtener las proporciones de colores en un barrio


def obtener_proporciones_barrio(barrio_id):
    def query():
        conn = connect_db()
        proporciones = {}
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('''SELECT color, COUNT(*) as cantidad 
                                  FROM propiedades WHERE barrio = %s 
                                  GROUP BY color''', (barrio_id,))
                colores = cursor.fetchall()

                total_propiedades = sum([color['cantidad'] for color in colores])
                for color in colores:
                    proporciones[color['color']] = (color['cantidad'] / total_propiedades) * 100
            conn.close()
        return proporciones
    return retry_query(query)

# Actualizar el controlador[3] de todas las propiedades del usuario en la base de datos


def actualizar_controlador_penalizacion(usuario_id, penalizado):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''UPDATE propiedades 
                                  SET controladores = JSON_SET(controladores, '$[3]', %s)
                                  WHERE inversionista_id = %s''', (1 if penalizado else 0, usuario_id))
                conn.commit()
            conn.close()
    retry_query(query)

# Verificar si el inversionista está penalizado


def verificar_estado_inversionista(id_inversionista):
    def query():
        conn = connect_db()
        penalizado = False
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT penalizado FROM inversionistas WHERE id = %s', (id_inversionista,))
                inversionista = cursor.fetchone()
                if inversionista:
                    penalizado = inversionista['penalizado']
            conn.close()
        return penalizado
    return retry_query(query)

# Eliminar una propiedad de la base de datos


def eliminar_propiedad(propiedad_id):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('DELETE FROM propiedades WHERE id = %s', (propiedad_id,))
                conn.commit()
            conn.close()
    retry_query(query)

# Actualizar los controladores de las propiedades en el barrio


def actualizar_controladores_propiedades_barrio(barrio_id):
    porcentajes_colores = obtener_proporciones_barrio(barrio_id)
    actualizar_controladores_barrio(barrio_id, porcentajes_colores)

# Actualizar el estado del inversionista


def actualizar_estado_inversionista(usuario_id, penalizado):
    def query():
        conn = connect_db()
        if conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('''INSERT INTO inversionistas (id, penalizado)
                                  VALUES (%s, %s)
                                  ON DUPLICATE KEY UPDATE penalizado = %s''',
                               (usuario_id, penalizado, penalizado))
                conn.commit()
            conn.close()
    retry_query(query)


# Obtener las rentas diarias de las propiedades de un usuario
def obtener_renta_propiedades(usuario_id):
    def query():
        conn = connect_db()
        rentas = []
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT renta_diaria FROM propiedades WHERE usuario_id = %s', (usuario_id,))
                rentas = cursor.fetchall()
            conn.close()
        return rentas
    return retry_query(query)

# Obtener los costos diarios de las propiedades de un usuario


def obtener_costo_diario_propiedades(usuario_id):
    def query():
        conn = connect_db()
        costos = []
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT costo_diario FROM propiedades WHERE inversionista_id = %s', (usuario_id,))
                costos = cursor.fetchall()
            conn.close()
        return costos
    return retry_query(query)

# Obtener los costos de mantenimiento de las propiedades de un usuario


def obtener_mantencion_propiedades(usuario_id):
    def query():
        conn = connect_db()
        costos = []
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT costo_mantenimiento FROM propiedades WHERE inversionista_id = %s', (usuario_id,))
                costos = cursor.fetchall()
            conn.close()
        return costos
    return retry_query(query)

# Obtener todos los usuarios registrados como inversionistas


def obtener_usuarios_registrados():
    def query():
        conn = connect_db()
        usuarios = []
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT * FROM inversionistas')
                usuarios = cursor.fetchall()
            conn.close()
        return usuarios
    return retry_query(query)


def obtener_usuarios_con_fecha(columna_fecha, fecha_actual):
    conn = connect_db()
    if conn:
        with closing(conn.cursor(dictionary=True)) as cursor:
            cursor.execute(f'SELECT * FROM inversionistas WHERE {columna_fecha} <= %s', (fecha_actual,))
            return cursor.fetchall()
    return []


def actualizar_fecha_tarea(columna_fecha, usuario_id, nueva_fecha):
    conn = connect_db()
    if conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(f'UPDATE inversionistas SET {columna_fecha} = %s WHERE usuario_id = %s', (nueva_fecha, usuario_id))
            conn.commit()


def get_user_inversionista(user_id):
    conn = connect_db()
    if conn:
        with closing(conn.cursor(dictionary=True)) as cursor:
            query = '''
                SELECT users.*
                FROM inversionistas
                JOIN users ON inversionistas.usuario_id = users.id
                WHERE inversionistas.usuario_id = %s
            '''
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            # Asegúrate de limpiar cualquier resultado pendiente
            cursor.fetchall()  # Esto asegura que no haya resultados pendientes
            return result
    return None


# Verificar si un usuario está registrado como inversionista


def es_inversionista(usuario_id, guild_id):
    def query():
        conn = connect_db()
        inversionista = False
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                # Buscamos el ID del usuario en la tabla users primero
                cursor.execute('SELECT id FROM users WHERE user_id = %s AND guild_id = %s', (usuario_id, guild_id))
                user_data = cursor.fetchone()

                if user_data:
                    # Verificamos si el usuario está en la tabla inversionistas usando su ID
                    user_id = user_data['id']
                    cursor.execute('SELECT usuario_id FROM inversionistas WHERE usuario_id = %s', (user_id,))
                    inversionista = cursor.fetchone() is not None
            conn.close()
        return inversionista
    return retry_query(query)


# Obtener todos los usuarios penalizados actualmente


def obtener_usuarios_penalizados():
    def query():
        conn = connect_db()
        usuarios_penalizados = []
        if conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute('SELECT usuario_id FROM inversionistas WHERE penalizado = 1')
                usuarios_penalizados = cursor.fetchall()
            conn.close()
        return usuarios_penalizados
    return retry_query(query)


# Crear las tablas si no existen
create_property_tables()
