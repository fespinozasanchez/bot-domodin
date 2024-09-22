from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from utils.base import Base  # Importar desde el nuevo módulo base.py
from config import DATABASE_CONFIG
from rpg_module.player import Player
from rpg_module.skills import Skill
from rpg_module.weapons import Weapon
from rpg_module.armors import Armor
from rpg_module.player_inventory import PlayerInventory

# Configuración de la base de datos usando DATABASE_CONFIG
DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}"

# Crear el motor de SQLAlchemy, asegurando que usamos InnoDB
engine = create_engine(DATABASE_URL, echo=True)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()

# Definir la tabla player_skills como tabla Many-to-Many entre jugadores y habilidades
player_skills = Table('player_skills', Base.metadata,
                      Column('player_id', Integer, ForeignKey('players.id', ondelete="CASCADE"), primary_key=True),
                      Column('skill_id', Integer, ForeignKey('skills.id', ondelete="CASCADE"), primary_key=True)
                      )

# Función para inicializar la base de datos y crear las tablas si no existen
def init_db():
    """Crea todas las tablas en la base de datos si no existen."""
    Base.metadata.create_all(engine)

# Funciones útiles para interactuar con la base de datos

def create_player(name):
    """Crea un nuevo jugador y lo guarda en la base de datos."""
    new_player = Player(name=name)
    session.add(new_player)
    session.commit()
    return new_player

def get_player_by_name(name):
    """Recupera un jugador por su nombre."""
    return session.query(Player).filter_by(name=name).first()

def get_player_by_id(player_id):
    """Recupera un jugador por su ID."""
    return session.query(Player).filter_by(id=player_id).first()

def create_weapon(name, description, base_damage, increase_stat, increase_amount):
    """Crea un arma y la guarda en la base de datos."""
    new_weapon = Weapon(name=name, description=description, base_damage=base_damage,
                        increase_stat=increase_stat, increase_amount=increase_amount)
    session.add(new_weapon)
    session.commit()
    return new_weapon

def get_weapon_by_name(name):
    """Recupera un arma por su nombre."""
    return session.query(Weapon).filter_by(name=name).first()

def get_weapon_by_id(weapon_id):
    """Recupera un arma por su ID."""
    return session.query(Weapon).filter_by(id=weapon_id).first()

def create_armor(name, description, defense_value, increase_stat, increase_amount):
    """Crea una armadura y la guarda en la base de datos."""
    new_armor = Armor(name=name, description=description, defense_value=defense_value,
                      increase_stat=increase_stat, increase_amount=increase_amount)
    session.add(new_armor)
    session.commit()
    return new_armor

def get_armor_by_name(name):
    """Recupera una armadura por su nombre."""
    return session.query(Armor).filter_by(name=name).first()

def get_armor_by_id(armor_id):
    """Recupera una armadura por su ID."""
    return session.query(Armor).filter_by(id=armor_id).first()

def add_item_to_inventory(player_id, item_id, item_type):
    inventory_item = PlayerInventory(player_id=player_id)
    if item_type == "weapon":
        inventory_item.weapon_id = item_id
    elif item_type == "armor":
        inventory_item.armor_id = item_id

    session.add(inventory_item)
    session.commit()
