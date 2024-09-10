import random
from market_module.const_market import TIERS, VALORES_BASE_NIVEL
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
    suerte_factor = (1.0 - suerte) + 0.5  # A mayor suerte, menor valor de compra
    tier_factor = 1.0 + TIERS[tier]  # Factor basado en el tier de la propiedad
    
    return valor_base * multiplicador_tamaño * multiplicador_pisos * suerte_factor * tier_factor

# Función para calcular la renta diaria con controladores ajustados
def calcular_renta_diaria(nivel, tier, suerte, desgaste, controladores, porcentajes, color, valor_compra):
    valor_base = 0.25 * suerte + 0.1 # Entre 10% y 35% del valor base de compra
    base_rent = valor_compra * valor_base
    suerte_factor = suerte * 1.5  # A mayor suerte, mayor renta diaria
    desgaste_factor = (1.0 - desgaste) + 0.5 # A mayor desgaste, menor renta
    tier_factor = 1.0 + TIERS[tier] * nivel # Factor basado en el tier

    # Ajustes por controladores
    if controladores[0] == 1:
        base_rent *= 1.15  # Aumenta un 15% si se tiene más del 50% del color en el barrio
    if controladores[2] == 1:
        base_rent *= 0.80  # Disminuye un 20% si se tiene menos del 20% del color

    # Transferencia de renta al color con más del 80% del barrio
    if porcentajes.get(color, 0) < 20 and controladores[1] == 1:
        base_rent *= 1.20

    return base_rent * suerte_factor * desgaste_factor * tier_factor

# Función para calcular el costo diario
def calcular_costo_diario(nivel, tier, tamaño, pisos, suerte,renta_diaria):
    valor_base = 0.1 *(1-suerte)  +0.05 # Entre el 05% y 15% de la renta diaria
    base_cost = renta_diaria * valor_base + (tamaño/pisos) * valor_base  # Influencia del tamaño y pisos
    suerte_factor = (1.0 - suerte) + 0.5  # A mayor suerte, menor costo diario
    tier_factor = 1.0 + TIERS[tier] * nivel  # Factor basado en el tier y nivel

    # Posibilidad de que el costo diario sea mayor si la suerte es muy baja
    if random.random() < (1 - float(suerte)):
        base_cost *= random.uniform(1.1, 1.3)

    return base_cost * suerte_factor * tier_factor

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


