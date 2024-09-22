COLORS = [
    '#FF0000',  # Rojo (Red)
    '#0000FF',  # Azul (Blue)
    '#00FF00',  # Verde (Green)
    '#FFFF00',  # Amarillo (Yellow)
    '#FFA500',  # Naranja (Orange)
    '#800080',  # Morado (Purple)
    '#FFC0CB'   # Rosa (Pink)
]


BARRIOS = list(range(1, 11))
BARRIO_WEIGHTS = [0.3, 0.2, 0.15, 0.1, 0.1, 0.05, 0.03, 0.03, 0.02, 0.02]


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


TIER_WEIGHTS = [0.04, 0.13, 0.20, 0.30, 0.25, 0.05, 0.02, 0.00007, 0.00003]

VALORES_BASE_NIVEL = {
    1: (10, 1000),
    2: (1001, 10000),
    3: (80000, 300000),
    4: (1000000, 100000000),
    5: (1000000000, 50000000000)
}


NIVEL_WEIGHTS = [0.39, 0.40, 0.17, 0.03, 0.01]
