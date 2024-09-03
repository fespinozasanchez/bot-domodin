# warrior_skill.py
from skills import Skill
import random as ra


class WarriorSkill(Skill):
    def __init__(self, name, description, secondary_attribute, skill_type, mana_cost, multiplier, damage_boost, stun_chance, damage, cooldown=0):
        """
        name: Nombre de la habilidad de guerrero.
        description: Descripción de la habilidad.
        secondary_attribute: Atributo secundario que afecta la habilidad.
        skill_type: Tipo de habilidad (ej. 'offensive').
        mana_cost: Costo de mana para usar la habilidad.
        multiplier: Multiplicador que se aplica al atributo principal (fuerza).
        damage_boost: Incremento adicional en el daño causado.
        stun_chance: Probabilidad de aturdir al enemigo (ej. 0.2 para 20%).
        damage: Daño base adicional que causa la habilidad.
        cooldown: Turnos de cooldown antes de que la habilidad pueda ser utilizada de nuevo.
        """
        super().__init__(name, description, "strength", secondary_attribute,
                         skill_type, mana_cost, multiplier, damage, cooldown=cooldown)
        self.damage_boost = damage_boost
        self.stun_chance = stun_chance

    def use(self, player, enemy=None):
        """
        Usa la habilidad del guerrero, causando daño y aplicando la probabilidad de aturdir al enemigo.
        """
        if not enemy:
            return 0

        if self.can_use(player):
            player.mana -= self.mana_cost
            damage = getattr(player, self.main_attribute) * \
                self.multiplier + self.damage_boost + self.damage

            if ra.random() < self.stun_chance:
                enemy.stunned = True

            self.current_cooldown = self.cooldown

            return max(damage, 0)
        else:
            return 0
