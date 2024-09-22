from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from utils.rpg_data_manager import Base

class Weapon(Base):
    __tablename__ = 'weapons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    base_damage = Column(Float)
    increase_stat = Column(String(255))
    increase_amount = Column(Float)
    price = Column(Float, default=100)

    players = relationship("Player", back_populates="weapon")

    def apply_bonus(self, player):
        """
        Aplica el bono del arma al jugador, incrementando la estadística correspondiente.
        """
        if self.increase_stat and self.increase_amount:
            setattr(player, self.increase_stat, getattr(
                player, self.increase_stat) + self.increase_amount)

    def remove_bonus(self, player):
        """
        Remueve el bono del arma cuando se desequipa.
        """
        if self.increase_stat and self.increase_amount:
            setattr(player, self.increase_stat, getattr(
                player, self.increase_stat) - self.increase_amount)

    def calculate_damage(self, player):
        """
        Calcula el daño total del arma basado en el atributo principal del jugador y el daño base del arma.
        """
        main_attr_value = getattr(player, self.increase_stat, 0)
        total_damage = main_attr_value + self.base_damage
        return total_damage
