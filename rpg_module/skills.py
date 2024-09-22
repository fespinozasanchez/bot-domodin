from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from utils.rpg_data_manager import Base

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    mana_cost = Column(Float)
    multiplier = Column(Float)
    damage = Column(Float)

    players = relationship("Player", secondary='player_skills', back_populates="skills")

    def can_use(self, player):
        """
        Verifica si la habilidad se puede usar basándose en los atributos del jugador y el costo de mana.
        """
        main_attr_value = getattr(player, self.main_attribute, 0)
        secondary_attr_value = getattr(player, self.secondary_attribute, 0)
        return main_attr_value > 0 and secondary_attr_value >= 0 and player.mana >= self.mana_cost and self.current_cooldown == 0

    def use(self, player, target=None):
        """
        Usa la habilidad, aplicando daño y efectos si es posible.
        """
        if self.can_use(player):
            player.mana -= self.mana_cost
            damage = getattr(player, self.main_attribute) * \
                self.multiplier + self.damage

            # Aplicar efecto adicional si existe
            if self.effect and target:
                self.effect(target)

            # Activar el cooldown
            self.current_cooldown = self.cooldown

            return damage
        else:
            return 0

    def calculate_damage(self, player):
        """
        Calcula el daño total que causaría la habilidad basándose en los atributos del jugador.
        """
        if self.can_use(player):
            return getattr(player, self.main_attribute) * self.multiplier + self.damage
        else:
            return 0

    def reduce_cooldown(self):
        """
        Reduce el cooldown de la habilidad al final de cada turno.
        """
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def apply_effect(self, target):
        """
        Aplica el efecto adicional de la habilidad, si existe.
        """
        if self.effect:
            self.effect(target)
