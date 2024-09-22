from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from utils.rpg_data_manager import Base

class Armor(Base):
    __tablename__ = 'armors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    defense_value = Column(Float)
    increase_stat = Column(String(255))
    increase_amount = Column(Float)
    price = Column(Float, default=100)

    players = relationship("Player", back_populates="armor")

    def apply_bonus(self, player):
        """
        Aplica los bonos de la armadura al jugador, incrementando las estadísticas correspondientes.
        """
        super().apply_bonus(player)  # Usa el método apply_bonus de la clase padre (Item)

        # Aplicar bono de defensa si está presente
        if self.defense_value:
            player.defense += self.defense_value

    def remove_bonus(self, player):
        """
        Elimina los bonos de la armadura cuando el jugador se la quita.
        """
        if self.increase_stat == "mana":
            player.mana -= self.increase_amount
        elif self.increase_stat == "health":
            player.health -= self.increase_amount

        if self.defense_value:
            player.defense -= self.defense_value
