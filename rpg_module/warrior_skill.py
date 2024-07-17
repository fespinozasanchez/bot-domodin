# warrior_skill.py
from skills import Skill
import random as ra

class WarriorSkill(Skill):
    def __init__(self, name, description, secondary_attribute, skill_type, mana_cost, multiplier, damage_boost, stun_chance,damage):
        super().__init__(name, description, "strength", secondary_attribute, skill_type, mana_cost, multiplier,damage)
        self.damage_boost = damage_boost
        self.stun_chance = stun_chance

    def use(self, player, enemy=None):
        if not enemy:
            print("No enemy target provided for WarriorSkill.")
            return 0
        
        if self.can_use(player):
            player.mana -= self.mana_cost
            damage = getattr(player, self.main_attribute) * self.multiplier + self.damage_boost
            actual_damage = max(damage, 0)
            # Apply stun based on stun_chance
            if ra.randint(1,2) < self.stun_chance:
                enemy.stunned = True
                print(f"Enemy {enemy.name} is stunned!")
            return actual_damage
        else:
            print("No tienes suficiente mana o no cumples con los requisitos para usar esta habilidad.")
        return 0
