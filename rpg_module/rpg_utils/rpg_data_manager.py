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
engine = create_engine(DATABASE_URL, echo=True, connect_args={'connect_timeout': 10})

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
    session.connection(execution_options={'timeout':30})
    session = Session()
    try:
        return session.query(Player).all()
    finally:
        session.close()




def level_up_player(player):
    """Sube de nivel al jugador si tiene suficientes puntos de estadísticas."""
    required_points = player.calculate_experience_for_next_level()
    try:        
        if player.experience >= required_points:
            player.level += 1
            player.health += 10
            player.mana += 10
            player.strength += 5
            player.intelligence += 5
            player.agility += 5
            if player.class_player == 'warrior':
                player.strength += 5
            elif player.class_player == 'mage':
                player.intelligence += 5
            elif player.class_player == 'thieve':
                player.agility += 5
            player.stats_points +=15
            session.commit()
            return f"{player.name} ha subido al nivel {player.level}! "
        else:
            return f"{player.name} no tiene suficientes puntos de experiencia para subir de nivel. Necesitas {required_points} puntos."
    
    except SQLAlchemyError as e:
        session.rollback()
        raise e
   
def revive_player(player):
    """Revive al jugador si tiene suficientes puntos de estadísticas."""
    
    required_points = 100*player.level
    try:
        session.connection(execution_options={'timeout': 30}) 
        if player.experience >= required_points:
            player.health = 100
            player.mana = 100
            player.experience -= required_points
            session.commit()
            return f"Has sido revivido! "
        else:
            return f"No tienes suficientes puntos de stats para revivir. Necesita {required_points} puntos."
    except SQLAlchemyError as e:
        session.rollback()
        raise e


init_alchemy_db()
