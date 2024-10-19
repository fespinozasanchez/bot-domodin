
NOMBRES_ENEMIGO = {
    1: ['Goblin', 'Bandido', 'Rata Gigante', 'Esqueleto'],
    2: ['Orco', 'Mercenario', 'Ogro', 'Guerrero Esqueleto'],
    3: ['Troll', 'Mago Oscuro', 'Elemental de Fuego', 'Gárgola'],
    4: ['Dragón Juvenil', 'Liche', 'Gigante', 'Señor Vampiro'],
    5: ['Dragón Anciano', 'Archidemonio', 'Titán', 'El Enemigo']
}

TIERS = {
    'F': -0.15,
    'E': -0.05,
    'D': 0,
    'C': 0.08,
    'B': 0.14,
    'A': 0.30,
    'S': 0.50,
    'S+': 0.65,
    'S++': 0.80
}

TIER_WEIGHTS = [0.04, 0.13, 0.20, 0.30, 0.25, 0.05, 0.02, 0.00007, 0.00003]

VALORES_BASE_NIVEL = {
    1: (10, 1_000),
    2: (1_001, 10_000),
    3: (80_000, 300_000),
    4: (1_000_000, 100_000_000),
    5: (1_000_000_000, 50_000_000_000)
}

NIVEL_WEIGHTS = [0.39, 0.40, 0.17, 0.03, 0.01]


