import random
from venv import logger
from market_module.const_market import TIERS, VALORES_BASE_NIVEL, SUERTE_FACTORES
# from utils.market_data_manager import obtener_proporciones_barrio

# Función para generar un valor aleatorio basado en suerte


def calcular_suerte():
    return random.uniform(0, 1)

# Función para calcular el desgaste de la propiedad en función del tiempo


def calcular_desgaste():
    return random.uniform(0, 1)


def ajustar_pesos_por_suerte(pesos, suerte):
    """
    Ajusta los pesos originales en función de la suerte.
    A mayor suerte, aumenta la probabilidad de elegir opciones con mayores índices (valores más altos).
    """
    pesos_ajustados = []

    for i, peso in enumerate(pesos):
        # Aumentar los pesos de los valores altos cuando la suerte es alta
        factor = 1 + (suerte * (i + 1) / len(pesos))  # Incremento lineal según la posición
        pesos_ajustados.append(peso * factor)

    # Normalizar los pesos ajustados para que sumen 1
    suma_ajustada = sum(pesos_ajustados)
    return [peso_ajustado / suma_ajustada for peso_ajustado in pesos_ajustados]


def elegir_valor_ponderado_por_suerte(opciones, pesos, suerte):
    """
    Elige un valor ponderado en función de la suerte.
    A mayor suerte, se favorecen las opciones con mayores índices.
    """
    # Ajustar los pesos originales en función de la suerte
    pesos_ajustados = ajustar_pesos_por_suerte(pesos, suerte)

    # Elegir un valor aleatoriamente con los pesos ajustados
    return random.choices(opciones, weights=pesos_ajustados, k=1)[0]

# Función no lineal para calcular el valor de compra


def calcular_valor_compra(nivel, tier, tamaño, pisos, suerte):
    min_valor, max_valor = VALORES_BASE_NIVEL[nivel]  # Valor base según nivel
    valor_base = min_valor + (1 - suerte) * (max_valor - min_valor)
    multiplicador_tamaño = tamaño * 0.5
    multiplicador_pisos = pisos * 1.2
    tier_factor = 1.0 + TIERS[tier]  # Factor basado en el tier de la propiedad

    return valor_base * multiplicador_tamaño * multiplicador_pisos * tier_factor


# Ajustes en la fórmula de renta diaria


def calcular_renta_diaria(nivel, tier, suerte, desgaste, controladores, porcentajes, color, valor_compra):
    valor_base = SUERTE_FACTORES['SUERTE_MIN_FACTOR'] * suerte + SUERTE_FACTORES['SUERTE_MIN_FACTOR']  # Ajustado el rango base (entre 10% y 20%)
    base_rent = valor_compra * valor_base

    # Factor suerte más controlado  0.1                                                                             0.8
    desgaste_factor = max(SUERTE_FACTORES['DESGASTE_MIN_FACTOR'], min((1.0 - desgaste) + 0.2, SUERTE_FACTORES['DESGASTE_MAX_FACTOR']))  # Limitar impacto de desgaste
    tier_factor = 1.0 + TIERS[tier] * nivel  # Factor basado en el tier y nivel

    # Ajustes por controladores
    if controladores[0] == 1:
        base_rent *= 1.10  # Aumenta un 10% si se tiene más del 50% del color en el barrio
    if controladores[2] == 1:
        base_rent *= 0.90  # Disminuye un 10% si se tiene menos del 20% del color

    # Transferencia de renta al color con más del 80% del barrio
    if porcentajes.get(color, 0) < 20 and controladores[1] == 1:
        base_rent *= 1.10  # Se ajusta el incremento a un 10%

    # Renta ajustada final
    return base_rent * desgaste_factor * tier_factor


def calcular_costo_diario(tier, tamaño, pisos, renta_diaria):
    # Cálculo del costo diario basado en la renta diaria, tier, tamaño y pisos
    # obtiene un porcentaje segun el tier, mejor tier, menor porcentaje,
    try:
        base_costo = (renta_diaria*0.4)
        factor_tier = (1 - ((TIERS[tier]))) * (1 - ((TIERS[tier])))/(2)
        factor_tamano = (1+((tamaño/500)+(pisos/10))) * (1-(TIERS[tier]))
        base_costo_factor = base_costo * factor_tamano * factor_tier
        return base_costo_factor
    except Exception as e:
        logger.error(f"Error al calcular el costo diario: {e}")
        return 0


# Función para calcular el costo de mantenimiento (más no lineal, influenciado por tamaño y pisos)
def calcular_costo_mantenimiento(nivel, tier, tamaño, pisos, suerte):
    base_cost = tamaño * pisos * 1.5  # Influencia más fuerte del tamaño y pisos
    suerte_factor = (1.0 - suerte) + 0.3  # A mayor suerte, menor costo
    tier_factor = 1.0 + TIERS[tier] * nivel  # Factor basado en el tier y nivel

    return base_cost * suerte_factor * tier_factor

# Función para generar los controladores al crear una nueva propiedad


def generar_controladores():
    """
    Genera un array de controladores iniciales.
    Los primeros 4 controladores se inicializan en 0.
    Los últimos 2 controladores son aleatorios con valores entre 0 y 1.
    """
    controladores = [0, 0, 0, 0]  # Inicializamos los primeros 4 controladores a 0
    controladores += [random.choice([0, 1]) for _ in range(2)]  # Los últimos 2 controladores son aleatorios (0 o 1)
    return controladores
