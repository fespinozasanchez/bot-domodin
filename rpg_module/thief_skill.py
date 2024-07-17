# thief_skill.py
from skills import Skill
import random as ra

class ThiefSkill(Skill):
    def __init__(self, name, description, secondary_attribute, skill_type, mana_cost, multiplier, crit_chance, evasion_boost,damage):
        super().__init__(name, description, "agility", secondary_attribute, skill_type, mana_cost, multiplier,damage)
        self.crit_chance = crit_chance
        self.evasion_boost = evasion_boost

    def use(self, player):
        if self.can_use(player):
            player.mana -= self.mana_cost
            damage = getattr(player, self.main_attribute) * self.multiplier
            # Apply critical hit based on crit_chance
            if ra.randint(1,2) < self.crit_chance:
                damage *= 2
                print("Critical hit!")
            # Temporarily boost player's evasion
            player.evasion += self.evasion_boost
            return damage
        else:
            print("No tienes suficiente mana o no cumples con los requisitos para usar esta habilidad.")
        return 0
