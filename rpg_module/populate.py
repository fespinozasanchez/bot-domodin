
import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from utils.rpg_data_manager import session
from rpg_module.weapons import Weapon
from rpg_module.armors import Armor

# Lista de posibles nombres de armas
weapon_names = [
    "Sword of Power", "Axe of Fury", "Bow of Precision", 
    "Dagger of Speed", "Mace of Destruction", "Spear of Destiny"
]

armor_names = ["Iron Armor", "Steel Armor", "Leather Armor", "Chainmail Armor", "Plate Armor"]

# Lista de posibles stats a incrementar
stats = ["strength", "intelligence", "agility"]

# Función para generar armas aleatorias
def generate_random_weapon():
    name = random.choice(weapon_names)
    base_damage = round(random.uniform(10, 100), 2)
    increase_stat = random.choice(stats)
    increase_amount = round(random.uniform(1, 10), 2)
    price = round(random.uniform(100, 1000), 2)

    weapon = {
        "name": name,
        "description": "",
        "base_damage": base_damage,
        "increase_stat": increase_stat,
        "increase_amount": increase_amount
    }
    return weapon


def generate_random_armor():
    name = random.choice(armor_names)
    defense_value = round(random.uniform(1, 10), 2)
    increase_stat = random.choice(stats)
    increase_amount = round(random.uniform(1, 10), 2)
    price = round(random.uniform(100, 1000), 2)

    armor = {
        "name": name,
        "description": "",
        "defense_value": defense_value,
        "increase_stat": increase_stat,
        "increase_amount": increase_amount
    }
    return armor

# Generar y agregar armas a la base de datos
def populate_weapons_table(num_weapons=10):
    for _ in range(num_weapons):
        weapon_data = generate_random_weapon()
        new_weapon = Weapon(**weapon_data)
        session.add(new_weapon)
    
    session.commit()
    print(f"{num_weapons} weapons have been added to the database.")


def populate_armors_table(num_armors=10):
    for _ in range(num_armors):
        armor_data = generate_random_armor()
        new_armor = Armor(**armor_data)
        session.add(new_armor)
    
    session.commit()
    print(f"{num_armors} armors have been added to the database.")
# Ejecutar la función
if __name__ == "__main__":
    populate_weapons_table(10)
    populate_armors_table(10)
