from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table, MetaData
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE_CONFIG

# Definir la base para nuestros modelos
Base = declarative_base()

# Configuración de la base de datos usando DATABASE_CONFIG
DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}"

# Crear el motor de SQLAlchemy, asegurando que usamos InnoDB y el seguimiento de las consultas
engine = create_engine(DATABASE_URL, echo=True)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()

# Definir la tabla player_skills como tabla Many-to-Many entre jugadores y habilidades
player_skills = Table('player_skills', Base.metadata,
    Column('player_id', Integer, ForeignKey('players.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
)

# Modelo de Jugador
class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    level = Column(Integer, default=1)
    health = Column(Float, default=100)
    strength = Column(Float, default=10)
    intelligence = Column(Float, default=10)
    agility = Column(Float, default=10)
    mana = Column(Float, default=100)
    stats_points = Column(Integer, default=15)
    weapon_id = Column(Integer, ForeignKey('weapons.id', ondelete="SET NULL", onupdate="CASCADE"))
    armor_id = Column(Integer, ForeignKey('armors.id', ondelete="SET NULL", onupdate="CASCADE"))

    weapon = relationship("Weapon", back_populates="players")
    armor = relationship("Armor", back_populates="players")
    skills = relationship("Skill", secondary=player_skills, back_populates="players")

# Modelo de Habilidades
class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    mana_cost = Column(Float)
    multiplier = Column(Float)
    damage = Column(Float)

    players = relationship("Player", secondary=player_skills, back_populates="skills")

# Modelo de Armas
class Weapon(Base):
    __tablename__ = 'weapons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    base_damage = Column(Float)
    increase_stat = Column(String(255))
    increase_amount = Column(Float)

    players = relationship("Player", back_populates="weapon")

# Modelo de Armaduras
class Armor(Base):
    __tablename__ = 'armors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    defense_value = Column(Float)
    increase_stat = Column(String(255))
    increase_amount = Column(Float)

    players = relationship("Player", back_populates="armor")

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
