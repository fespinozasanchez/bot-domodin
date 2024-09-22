from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from utils.base import Base  # Importar desde base.py

class PlayerInventory(Base):
    __tablename__ = 'player_inventory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id', ondelete="CASCADE"))
    weapon_id = Column(Integer, ForeignKey('weapons.id', ondelete="SET NULL"), nullable=True)
    armor_id = Column(Integer, ForeignKey('armors.id', ondelete="SET NULL"), nullable=True)

    player = relationship("Player", back_populates="inventory")
    weapon = relationship("Weapon")
    armor = relationship("Armor")
