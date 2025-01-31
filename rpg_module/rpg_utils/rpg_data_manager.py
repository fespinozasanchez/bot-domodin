from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_CONFIG
from rpg_module.rpg_utils.base import Base

# Importar todas las clases de modelo que definen las tablas
from rpg_module.Players.warrior import Warrior
from rpg_module.Players.mage import Mage
from rpg_module.Players.thieve import Thieve
from rpg_module.Players.player import Player  # Importar Player también
from rpg_module.Enemy.enemy import Enemy
from sqlalchemy.exc import SQLAlchemyError

# Crear el motor de SQLAlchemy
DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}"
engine = create_engine(DATABASE_URL, echo=True, connect_args={'connect_timeout': 180}, pool_pre_ping=True, pool_recycle=10800)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()


def init_alchemy_db():
    """Crea todas las tablas en la base de datos si no existen."""
    Base.metadata.create_all(engine)

# Función para registrar un jugador
def register_player(name, player_class):
    """Registra un nuevo jugador en la base de datos."""
    try:
        session.connection(execution_options={'timeout':30})
        if player_class.lower() == 'warrior':
            new_player = Warrior(name=name)
        elif player_class.lower() == 'mage':
            new_player = Mage(name=name)
        elif player_class.lower() == 'thieve':
            new_player = Thieve(name=name)
        else:
            raise ValueError("Clase de jugador no válida. Debe ser 'warrior', 'mage' o 'thieve'.")
        
        session.add(new_player)
        session.commit()
        return new_player  # Retorna el jugador registrado
    
    except Exception as e:
        session.rollback()
        raise e

# Función para obtener un jugador por nombre
def get_player_by_name(name):
    """Obtiene un jugador de la base de datos usando su nombre."""
    try:
        player = session.query(Player).filter_by(name=name).first()
        return player
    except SQLAlchemyError as e:
        session.rollback()
        raise e


# Función para obtener todos los jugadores
def get_all_players():
    """Obtiene todos los jugadores de la base de datos."""
    try:
        players = session.query(Player).order_by(Player.level.desc()).all()
        return players
    except SQLAlchemyError as e:
        session.rollback()
        raise e




def level_up_player(player):
    """Sube de nivel al jugador si tiene suficientes puntos de estadísticas."""
    required_points = player.calculate_experience_for_next_level()
    try:        
        if player.experience >= required_points:
            player.level += 1
            player.health += 10
            player.mana += 10
            player.strength += 1
            player.intelligence += 1
            player.agility += 1
            player.defense += 1
            player.evasion += 0.1
            if player.class_player == 'warrior':
                player.strength += 1
            elif player.class_player == 'mage':
                player.intelligence += 1
            elif player.class_player == 'thieve':
                player.agility += 1
            player.stats_points +=1
            session.commit()
            return f"{player.name} ha subido al nivel {player.level}! "
        else:
            return f"{player.name} no tiene suficientes puntos de experiencia para subir de nivel. Necesitas {required_points - player.experience} puntos."
    
    except SQLAlchemyError as e:
        session.rollback()
        raise e
   
def revive_player(player):
    """Revive al jugador si tiene suficientes puntos de estadísticas."""
    
    required_points = 100*player.level
    try:
        session.connection(execution_options={'timeout': 30}) 
        if player.experience >= required_points:
            player.current_health = player.health
            player.current_mana = player.mana
            player.experience -= required_points
            session.commit()
            return f"Has sido revivido! "
        else:
            return f"No tienes suficientes puntos de experiencia para revivir. Necesita {required_points} puntos."
    except SQLAlchemyError as e:
        session.rollback()
        raise e


init_alchemy_db()
