import random
import numpy as np  # Librería para cálculos numéricos y estadísticos


# Lista de colores disponibles para las propiedades
COLORS = ['Rojo', 'Azul', 'Verde', 'Amarillo', 'Naranja', 'Morado', 'Rosa']

# Distribución de probabilidad para los barrios (no lineal)
BARRIOS = list(range(1, 11))
BARRIO_WEIGHTS = [0.3, 0.2, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02]

# Nombres según tipo y nivel de propiedad
NOMBRES_HOGAR = {
    1: ['Puente', 'Calle', 'Esquina', 'Paradero', 'Terminal', 'Feria', 'Casa Abandonada', 'Un Árbol', 'Dos Árboles', 'Carpa', 'Baño'],
    2: ['Casa', 'Departamento', 'Piso Compartido', 'La Posada', 'Hostal', 'Cabaña'],
    3: ['Habitación de Hotel', 'Departamento Del Levano', 'Casa Grande', 'Cabaña Grande'],
    4: ['Mansión', 'Casa Gigante', 'Penthouse'],
    5: ['Chichén Itzá', 'El Coliseo', 'Cristo Redentor', 'La Gran Muralla China', 'Machu Picchu', 'Petra', 'Taj Mahal', 'La casa del felipe', 'Choza del duende', 'La moto del Caro']
}

NOMBRES_TIENDA = {
    1: ['Tienda Pequeña', 'Kiosco', 'Puesto en Feria', 'Almacén'],
    2: ['Mercado', 'Panadería', 'Farmacia', 'Frutería'],
    3: ['Supermercado', 'Restaurante', 'Boutique'],
    4: ['Centro Comercial', 'Edificio Corporativo', 'Fábrica'],
    5: ['Rascacielos', 'Compañía Internacional', 'Centro Financiero']
}

# Tiers de calidad y multiplicadores
TIERS = {
    'F': -0.30,
    'E': -0.15,
    'D': 0,
    'C': 0.05,
    'B': 0.20,
    'A': 0.45,
    'S': 0.60,
    'S+': 0.70,
    'S++': 0.90
}

# Pesos de probabilidad para los tiers
TIER_WEIGHTS = [0.04, 0.13, 0.20, 0.30, 0.25, 0.05, 0.02, 0.007, 0.003]

# Rango de valores de compra basado en el nivel
VALORES_BASE_NIVEL = {
    1: (10, 1000),
    2: (1001, 10000),
    3: (80000, 300000),
    4: (1000000, 100000000),
    5: (1000000000, 50000000000)
}

# Pesos de probabilidad para los niveles
NIVEL_WEIGHTS = [0.39, 0.40, 0.17, 0.03, 0.01]
