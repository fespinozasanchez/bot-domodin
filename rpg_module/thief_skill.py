# thief_skill.py
from skills import Skill
import random as ra


class ThiefSkill(Skill):
    def __init__(self, name, description, secondary_attribute, skill_type, mana_cost, multiplier, crit_chance, evasion_boost, damage, cooldown=0):
        """
        name: Nombre de la habilidad de ladrón.
        description: Descripción de la habilidad.
        secondary_attribute: Atributo secundario que afecta la habilidad.
        skill_type: Tipo de habilidad (ej. 'offensive').
        mana_cost: Costo de mana para usar la habilidad.
        multiplier: Multiplicador que se aplica al atributo principal (agilidad).
        crit_chance: Probabilidad de hacer un golpe crítico (ej. 0.2 para 20%).
        evasion_boost: Incremento temporal en la evasión del jugador al usar la habilidad.
        damage: Daño base adicional que causa la habilidad.
        cooldown: Turnos de cooldown antes de que la habilidad pueda ser utilizada de nuevo.
        """
        super().__init__(name, description, "agility", secondary_attribute,
                         skill_type, mana_cost, multiplier, damage, cooldown=cooldown)
        self.crit_chance = crit_chance
        self.evasion_boost = evasion_boost

    def use(self, player, target=None):
        """
        Usa la habilidad del ladrón, aplicando daño y aumentando la evasión del jugador temporalmente.
        """
        if self.can_use(player):
            player.mana -= self.mana_cost
            damage = getattr(player, self.main_attribute) * \
                self.multiplier + self.damage

            if ra.random() < self.crit_chance:
                damage *= 2
                print(f"Critical hit! {player.name} dealt {damage} damage.")

            player.evasion += self.evasion_boost
            print(f"{player.name}'s evasion increased by {
                  self.evasion_boost}!")
            self.current_cooldown = self.cooldown

            return damage
        else:
            print(
                "No tienes suficiente mana o no cumples con los requisitos para usar esta habilidad.")
            return 0

    def apply_critical_hit(self, damage):
        """
        Aplica un golpe crítico doblando el daño si la probabilidad de crítico se cumple.
        """
        if ra.random() < self.crit_chance:
            return damage * 2
        return damage
