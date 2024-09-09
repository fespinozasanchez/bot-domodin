import random
from utils.market_data_manager import (
   obtener_mantencion_propiedades, obtener_costo_diario_propiedades, 
    verificar_estado_inversionista, actualizar_controladores_propiedades_barrio, actualizar_estado_inversionista, 
    eliminar_propiedad, guardar_propiedad, obtener_propiedad, actualizar_desgaste_propiedad, 
    actualizar_controlador_penalizacion, obtener_propiedades_por_usuario, obtener_saldo_usuario, actualizar_saldo_usuario
)

# Evento que afecta la renta diaria globalmente
EVENTO_GLOBAL = None  # Variable que determina si ocurre un evento como "buen_dia_negocios" o "mal_dia_negocios"

# Función para determinar si ocurre un evento diario
def determinar_evento_diario():
    probabilidad_evento = 0.3  # 30% de que ocurra un evento diario
    return random.random() < probabilidad_evento

# Función que selecciona el evento diario si ocurre
def seleccionar_evento_diario():
    eventos_diarios = ['mal_dia_negocios', 'buen_dia_negocios']
    return random.choice(eventos_diarios)

# Eventos diarios
def mal_dia_negocios():
    global EVENTO_GLOBAL
    EVENTO_GLOBAL = 'mal_dia_negocios'

def buen_dia_negocios():
    global EVENTO_GLOBAL
    EVENTO_GLOBAL = 'buen_dia_negocios'

# Función que maneja los eventos diarios
def manejar_eventos_diarios():
    if determinar_evento_diario():
        evento = seleccionar_evento_diario()
        if evento == 'mal_dia_negocios':
            mal_dia_negocios()
        elif evento == 'buen_dia_negocios':
            buen_dia_negocios()
    else:
        global EVENTO_GLOBAL
        EVENTO_GLOBAL = None

# Eventos circunstanciales
# Evento: Comprar una propiedad
def comprar_propiedad(usuario_id, propiedad):
    """
    Evento que maneja la compra de una propiedad.
    Almacena la propiedad en la base de datos con el ID del usuario.
    También actualiza los colores en el barrio correspondiente.
    """
    
    if propiedad is not None:
        # Obtener el saldo del usuario
        saldo = obtener_saldo_usuario(usuario_id)
        
        # Verificar si el usuario tiene suficiente saldo para comprar la propiedad
        if saldo < propiedad['valor_compra']:
            raise Exception(f"No tienes suficiente saldo para comprar esta propiedad. Te faltan {propiedad['valor_compra'] - saldo} MelladoCoins.")
        
        # Si tiene suficiente saldo, proceder con la compra
        propiedad['usuario_id'] = usuario_id
        guardar_propiedad(propiedad)
        
        # Actualizar el saldo del usuario
        actualizar_saldo_usuario(usuario_id, saldo - propiedad['valor_compra'])
        
        # Actualizar controladores de barrio
        actualizar_controladores_propiedades_barrio(propiedad['barrio'])


# Evento: Venta de propiedad
def vender_propiedad(usuario_id, propiedad_id):
    """
    Evento para manejar la venta de una propiedad.
    La propiedad se elimina de la base de datos y el jugador recibe un porcentaje del valor de compra.
    """
    propiedad = obtener_propiedad(propiedad_id)
    if propiedad and propiedad['usuario_id'] == usuario_id:
        suerte = propiedad['suerte']
        valor_venta = propiedad['valor_compra'] * (0.8 + suerte)
        saldo_actual = obtener_saldo_usuario(usuario_id)
        nuevo_saldo = saldo_actual + valor_venta
        actualizar_saldo_usuario(usuario_id, nuevo_saldo)
        eliminar_propiedad(propiedad_id)
    return nuevo_saldo


# Evento: Actualizar el desgaste de una propiedad
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

# Función: Aplicar desgaste automático
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

# Evento: Mejorar desgaste de propiedad
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
        

# Función: Calcular costo para dejar el desgaste en 0
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
        return costo_mejora

def pagar_renta_diaria(usuario_id):
    """
    Maneja el pago de la renta diaria de todas las propiedades del usuario.
    Las propiedades hogar que son residencia principal (es_residencia_principal=1) no generan renta.
    Solo las propiedades arrendadas generan renta diaria.
    """
    propiedades = obtener_propiedades_por_usuario(usuario_id)

    if propiedades:
        total_renta = 0.0
        global EVENTO_GLOBAL

        # Verificar si el inversionista está penalizado
        penalizado = verificar_estado_inversionista(usuario_id)

        for propiedad in propiedades:
            # Si es hogar y es la residencia principal, no genera renta
            if propiedad['tipo'] == 'hogar' and propiedad['es_residencia_principal'] == 1:
                continue

            # Solo propiedades arrendadas generan renta
            if not propiedad['arrendada']:
                continue

            renta_diaria = propiedad['renta_diaria']
            
            # Ajustar la renta según los eventos globales
            if EVENTO_GLOBAL == 'mal_dia_negocios':
                renta_diaria *= 0.95
            elif EVENTO_GLOBAL == 'buen_dia_negocios':
                renta_diaria *= 1.10

            # Ajustar renta si el inversionista está penalizado
            if penalizado:
                renta_diaria *= 0.85

            total_renta += renta_diaria

        saldo_actual = obtener_saldo_usuario(usuario_id)
        nuevo_saldo = saldo_actual + total_renta
        actualizar_saldo_usuario(usuario_id, nuevo_saldo)

# Evento: Pago de costo diario
def pagar_costo_diario(usuario_id):
    """
    Maneja el pago del costo diario de todas las propiedades del usuario.
    Si el saldo es insuficiente o el usuario está penalizado, se aplica la penalización.
    """
    if verificar_estado_inversionista(usuario_id):
        return

    propiedades = obtener_costo_diario_propiedades(usuario_id)
    if propiedades:
        saldo_usuario = obtener_saldo_usuario(usuario_id)
        total_costo_diario = sum(propiedad['costo_diario'] for propiedad in propiedades)

        if saldo_usuario < total_costo_diario:
            actualizar_saldo_usuario(usuario_id, 0.0)
            penalizar_propietario(usuario_id)
        else:
            nuevo_saldo = saldo_usuario - total_costo_diario
            actualizar_saldo_usuario(usuario_id, nuevo_saldo)

# Evento: Pago de costo de mantenimiento
def pagar_costo_mantenimiento(usuario_id):
    """
    Maneja el pago del costo de mantenimiento de todas las propiedades del usuario.
    """
    if verificar_estado_inversionista(usuario_id):
        return

    propiedades = obtener_mantencion_propiedades(usuario_id)
    if propiedades:
        saldo_usuario = obtener_saldo_usuario(usuario_id)
        total_costo_mantenimiento = sum(propiedad['costo_mantenimiento'] for propiedad in propiedades)

        if saldo_usuario < total_costo_mantenimiento:
            actualizar_saldo_usuario(usuario_id, 0.0)
            penalizar_propietario(usuario_id)
        else:
            nuevo_saldo = saldo_usuario - total_costo_mantenimiento
            actualizar_saldo_usuario(usuario_id, nuevo_saldo)

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

# Función: Obtener evento global
def obtener_evento_global():
    """
    Devuelve el evento global actual, si existe.
    """
    return EVENTO_GLOBAL
