# player.py

from weapons import Weapon
from armors import Armor
from mage_skill import MageSkill
from warrior_skill import WarriorSkill
from thief_skill import ThiefSkill

class Player:

    def __init__(self, name, level=1, health=100, strength=10, intelligence=10, agility=10, mana=100, stats_points=15,
                 weapon=None, armor=None, boots=None, helmet=None, exp=0):
        self.name = name
        self.level = level
        self.health = health
        self.strength = strength
        self.intelligence = intelligence
        self.agility = agility
        self.mana = mana + (self.intelligence * 0.3)
        self.stats_points = stats_points
        self.weapon = weapon
        self.armor = armor
        self.boots = boots
        self.helmet = helmet
        self.exp = exp
        self.inventory = []

        self.equip_initial_items()

        self.skills = []
        self.evasion = 0

    def equip_initial_items(self):
        if self.weapon:
            self.weapon.apply_bonus(self)
            self.inventory.append(self.weapon)
        if self.armor:
            self.armor.apply_bonus(self)
            self.inventory.append(self.armor)
        if self.boots:
            self.inventory.append(self.boots)
        if self.helmet:
            self.inventory.append(self.helmet)

    def attack(self):
        if self.strength > self.intelligence and self.strength > self.agility:
            damage = self.strength * 1.5
        elif self.intelligence > self.strength and self.intelligence > self.agility:
            damage = self.intelligence * 1.5
        elif self.agility > self.strength and self.agility > self.intelligence:
            damage = self.agility * 1.5
        return damage

    def receive_damage(self, damage):
        damage -= self.agility * 0.4
        self.health -= damage

    def use_stat_point(self, stat):
        if self.stats_points > 0:
            if stat == "str":
                self.strength += 1
                self.health += 15
            elif stat == "int":
                self.intelligence += 1
                self.mana += 3
            elif stat == "agi":
                self.agility += 1
            self.stats_points -= 1
        else:
            print("No tienes más puntos para usar")

    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        self.inventory.remove(item)

    def get_inventory(self):
        return [item.name for item in self.inventory]

    def add_skill(self, skill):
        self.skills.append(skill)

    def remove_skill(self, skill):
        self.skills.remove(skill)

    def get_skills(self):
        return [skill.name for skill in self.skills]

    def level_up(self):
        if self.exp > 100:
            self.exp = 0
            self.level += 1
            self.health += 10
            self.strength += 2
            self.intelligence += 2
            self.agility += 2
            self.stats_points += 5

    def get_stats(self):
        return {
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "strength": self.strength,
            "intelligence": self.intelligence,
            "agility": self.agility,
            "mana": self.mana,
            "stats_points": self.stats_points,
        }

    def use_skill(self, skill_name, enemy=None):
        for skill in self.skills:
            if skill.name == skill_name:
                if isinstance(skill, WarriorSkill):
                    damage = skill.use(self, enemy)
                else:
                    damage = skill.use(self)
                return f"{self.name} uses {skill_name}, causing {damage} damage!"
        return f"{self.name} doesn't have the skill {skill_name}."

    def end_turn(self):
        for skill in self.skills:
            if isinstance(skill, MageSkill):
                skill.reduce_cooldown()
        # Reset evasion boost after turn ends
        self.evasion = 0