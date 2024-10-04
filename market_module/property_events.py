import logging
import random
from datetime import datetime, timedelta
from enum import Enum
from utils.market_data_manager import (
    get_current_event, obtener_mantencion_propiedades, obtener_costo_diario_propiedades, update_current_event,
    verificar_estado_inversionista, actualizar_controladores_propiedades_barrio, actualizar_estado_inversionista,
    eliminar_propiedad, guardar_propiedad, obtener_propiedad, actualizar_desgaste_propiedad,
    actualizar_controlador_penalizacion, obtener_propiedades_por_usuario, obtener_saldo_usuario, actualizar_saldo_usuario
)


class EventoGlobal(Enum):
    MAL_DIA_NEGOCIOS = 'Mal día para los negocios'
    BUEN_DIA_NEGOCIOS = 'Buen día para los negocios'
    NINGUNO = 'Es un día normal'

    def __str__(self):
        return self.value


class ManejadorEventosDiarios:
    eventos_diarios = [EventoGlobal.MAL_DIA_NEGOCIOS, EventoGlobal.BUEN_DIA_NEGOCIOS, EventoGlobal.NINGUNO]

    @classmethod
    def seleccionar_evento_diario(cls):
        return random.choice(cls.eventos_diarios)

    @classmethod
    def manejar_eventos_diarios(cls):
        try:
            resultado_evento = get_current_event()
            evento_actual = resultado_evento['current_event']
            fecha_cambio = resultado_evento['updated_at']
        except Exception as e:
            logging.error(f"Error al obtener el evento global actual: {e}")
            return

        # Asegurarnos de que la fecha sea del tipo datetime para hacer la comparación
        try:
            if isinstance(fecha_cambio, str):
                fecha_cambio = datetime.strptime(fecha_cambio, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logging.error("Error al convertir la fecha de cambio del evento global a datetime.")

        ahora = datetime.now()

        try:
            if ahora - fecha_cambio >= timedelta(hours=4):
                nuevo_evento = cls.seleccionar_evento_diario()
                try:
                    update_current_event(nuevo_evento.value, ahora)
                except Exception as e:
                    logging.error(f"Error al actualizar el evento global: {e}")
                logging.info(f"El evento global ha cambiado a: {nuevo_evento}")
            else:
                logging.info(f"El evento global actual es: {evento_actual}")
        except Exception as e:
            logging.error(f"Error al manejar los eventos diarios: {e}")


def obtener_evento_global():
    """
    The function obtains the current global event, returning a specific value if no event is found.
    :return: The function `obtener_evento_global` is returning the value of the current event if it
    exists and has a key 'current_event' in the dictionary `evento_actual`. If the current event does
    not exist or does not have the key 'current_event', then it returns the value `NINGUNO` from the
    `EventoGlobal` enum.
    """
    evento_actual = get_current_event()

    if evento_actual and 'current_event' in evento_actual:
        return evento_actual['current_event']
    return EventoGlobal.NINGUNO.value


# Evento: Comprar una propiedad
def comprar_propiedad(usuario_id, guild_id, propiedad):
    if propiedad is not None:
        saldo = obtener_saldo_usuario(usuario_id, guild_id)
        if saldo < propiedad['valor_compra']:
            faltante = propiedad['valor_compra'] - saldo
            raise Exception(f"No tienes suficiente saldo para comprar esta propiedad. Te faltan ${int(faltante):,}".replace(",", ".") + " MelladoCoins.")

        guardar_propiedad(propiedad)
        actualizar_saldo_usuario(usuario_id, guild_id, saldo - propiedad['valor_compra'])
        actualizar_controladores_propiedades_barrio(propiedad['barrio'])


def vender_propiedad(id_inversionista, usuario_id, guild_id, propiedad_id):
    """
    Evento para manejar la venta de una propiedad.
    La propiedad se elimina de la base de datos y el jugador recibe un porcentaje del valor de compra.
    """
    propiedad = obtener_propiedad(propiedad_id)
    if propiedad and propiedad['inversionista_id'] == id_inversionista:
        suerte = propiedad['suerte']
        valor_venta = propiedad['valor_compra'] * (0.8 + suerte)
        saldo_actual = obtener_saldo_usuario(usuario_id, guild_id)
        nuevo_saldo = saldo_actual + valor_venta
        actualizar_saldo_usuario(usuario_id, guild_id, nuevo_saldo)
        eliminar_propiedad(propiedad_id)
        return f"${int(nuevo_saldo):,}".replace(",", ".") + " MelladoCoins"


def mejorar_propiedad(usuario_id, propiedad_id, cantidad_dinero):
    """
    Mejora una propiedad reduciendo su desgaste en función del dinero invertido.
    """
    propiedad = obtener_propiedad(propiedad_id)

    if propiedad and propiedad['usuario_id'] == usuario_id:
        desgaste_actual = propiedad['desgaste']
        costo_por_punto = 100.0
        puntos_mejora = cantidad_dinero / costo_por_punto
        nuevo_desgaste = max(0.0, desgaste_actual - puntos_mejora)
        nuevo_desgaste_minimo = min(nuevo_desgaste, propiedad['desgaste_minimo'])
        actualizar_desgaste_propiedad(propiedad_id, nuevo_desgaste, nuevo_desgaste_minimo)


def aplicar_desgaste_automatico(propiedad):
    """
    Aplica un desgaste automático a la propiedad en función de su tier.
    Las propiedades de tier S++ no se desgastan.
    """
    tier = propiedad['tier']
    desgaste_actual = propiedad['desgaste']

    if tier == 'S++':
        return desgaste_actual

    tier_factors = {
        'S+': 0.001, 'S': 0.002, 'A': 0.003,
        'B': 0.004, 'C': 0.005, 'D': 0.006,
        'E': 0.007, 'F': 0.008
    }

    factor_desgaste = tier_factors.get(tier, 0.01)
    nuevo_desgaste = min(desgaste_actual + factor_desgaste, 1.00)
    return nuevo_desgaste


def mejorar_desgaste(id_propiedad, cantidad_pago):
    """
    Mejora el desgaste de una propiedad pagando una cierta cantidad.
    """
    propiedad = obtener_propiedad(id_propiedad)
    if propiedad:
        desgaste_actual = propiedad['desgaste']
        desgaste_minimo = propiedad['desgaste_minimo']
        diferencia_desgaste = max(desgaste_actual - desgaste_minimo, 0)
        factor_eficiencia = 1.0 - (diferencia_desgaste ** 2)
        mejora = (cantidad_pago / 10000) * (factor_eficiencia + 0.05)
        nuevo_desgaste = max(0.0, desgaste_actual - mejora)
        nuevo_desgaste_minimo = min(nuevo_desgaste, desgaste_minimo)
        actualizar_desgaste_propiedad(id_propiedad, nuevo_desgaste, nuevo_desgaste_minimo)


def calcular_costo_desgaste_a_cero(id_propiedad):
    """
    Calcula cuánto costaría reducir el desgaste de una propiedad a 0.
    """
    propiedad = obtener_propiedad(id_propiedad)
    if propiedad:
        desgaste_actual = propiedad['desgaste']
        desgaste_minimo = propiedad['desgaste_minimo']
        diferencia_desgaste = desgaste_actual - desgaste_minimo
        factor_eficiencia = 1.0 - (diferencia_desgaste ** 2)
        costo_mejora = (diferencia_desgaste / factor_eficiencia) * 10000.0
        return f"${int(costo_mejora):,}".replace(",", ".") + " MelladoCoins"


def pagar_renta_diaria(id_inversionista, guild_id, user_id):
    """
    Maneja el pago de la renta diaria de todas las propiedades del usuario.
    Las propiedades hogar que son residencia principal (es_residencia_principal=1) no generan renta.
    Solo las propiedades arrendadas generan renta diaria.
    """
    propiedades = obtener_propiedades_por_usuario(id_inversionista)
    if propiedades:
        total_renta = 0.0
        evento_actual = obtener_evento_global()

        penalizado = verificar_estado_inversionista(id_inversionista)
        for propiedad in propiedades:
            if propiedad['tipo'] == 'hogar' and propiedad['es_residencia_principal'] == 1:
                continue

            if not propiedad['arrendada']:
                continue

            renta_diaria = propiedad['renta_diaria']

            if evento_actual == EventoGlobal.MAL_DIA_NEGOCIOS.value:
                renta_diaria *= 0.95
            elif evento_actual == EventoGlobal.BUEN_DIA_NEGOCIOS.value:
                renta_diaria *= 1.10

            # Ajustar renta si el inversionista está penalizado
            if penalizado:
                renta_diaria *= 0.85

            total_renta += renta_diaria

        saldo_actual = obtener_saldo_usuario(user_id, guild_id)
        nuevo_saldo = saldo_actual + total_renta
        actualizar_saldo_usuario(user_id, guild_id, nuevo_saldo)
        return f"${int(nuevo_saldo):,}".replace(",", ".") + " MelladoCoins"

# Evento: Pagar costo diario


def pagar_costo_diario(usuario_id, guild_id, user_id):
    """
    Maneja el pago del costo diario de todas las propiedades del usuario.
    Si el saldo es insuficiente o el usuario está penalizado, se aplica la penalización.
    """
    if verificar_estado_inversionista(usuario_id):
        return

    propiedades = obtener_costo_diario_propiedades(usuario_id)
    if propiedades:
        saldo_usuario = obtener_saldo_usuario(user_id, guild_id)
        total_costo_diario = sum(propiedad['costo_diario'] for propiedad in propiedades)

        if saldo_usuario < total_costo_diario:
            actualizar_saldo_usuario(user_id, guild_id, 0.0)
            penalizar_propietario(usuario_id)
        else:
            nuevo_saldo = saldo_usuario - total_costo_diario
            actualizar_saldo_usuario(user_id, guild_id, nuevo_saldo)
            return f"${int(nuevo_saldo):,}".replace(",", ".") + " MelladoCoins"

# Evento: Pago de costo de mantenimiento


def pagar_costo_mantenimiento(usuario_id, guild_id, user_id):
    """
    Maneja el pago del costo de mantenimiento de todas las propiedades del usuario.
    """
    if verificar_estado_inversionista(usuario_id):
        return

    propiedades = obtener_mantencion_propiedades(usuario_id)
    if propiedades:
        saldo_usuario = obtener_saldo_usuario(user_id, guild_id)
        total_costo_mantenimiento = sum(propiedad['costo_mantenimiento'] for propiedad in propiedades)

        if saldo_usuario < total_costo_mantenimiento:
            actualizar_saldo_usuario(user_id, guild_id, 0.0)
            penalizar_propietario(usuario_id)
        else:
            nuevo_saldo = saldo_usuario - total_costo_mantenimiento
            actualizar_saldo_usuario(user_id, guild_id, nuevo_saldo)
            return f"${int(nuevo_saldo):,}".replace(",", ".") + " MelladoCoins"

# Función: Penalizar propietario


def penalizar_propietario(usuario_id):
    """
    Penaliza al propietario de todas sus propiedades.
    """
    actualizar_estado_inversionista(usuario_id, penalizado=True)
    actualizar_controlador_penalizacion(usuario_id, penalizado=True)

# Función: Despenalizar propietario


def despenalizar_propietario(usuario_id):
    """
    Elimina la penalización del propietario de todas sus propiedades.
    """
    actualizar_estado_inversionista(usuario_id, penalizado=False)
