from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from rpg_module.Interfaces.interfaces import Attacker, SkillUser, ItemEquipper, ItemUser, DamageReceiver

Base = declarative_base()

# Clase abstracta Player
class Player(Base, Attacker, SkillUser, ItemEquipper, ItemUser, DamageReceiver):
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
    experience = Column(Integer, default=0)
    class_player = Column(String(50))  # Identificador del tipo de jugador

    __mapper_args__ = {
        'polymorphic_identity': 'player',
        'polymorphic_on': class_player
    }

    def attack(self):
        raise NotImplementedError

    def use_special_ability(self):
        raise NotImplementedError

    def equip_item(self, item):
        raise NotImplementedError

    def use_item(self, item):
        raise NotImplementedError

    def receive_damage(self, damage):
        raise NotImplementedError

    def die(self):
        raise NotImplementedError


    def calculate_experience_for_next_level(self):
        player_level=self.level
        # Factores para el cálculo
        base_experience = 100  # Experiencia base para el primer nivel
        growth_factor = 2.6  # Factor de crecimiento polinómico

        # Cálculo de la experiencia necesaria para el siguiente nivel
        experience_needed = base_experience * (player_level ** growth_factor)

        return int(experience_needed)