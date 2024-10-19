from random import randint, choices
from .enemy_const import NIVEL_WEIGHTS, TIERS, TIER_WEIGHTS, NOMBRES_ENEMIGO, VALORES_BASE_NIVEL
class Enemy:
    def __init__(self, level=None, tier=None):
        self.level = level if level is not None else choices(list(VALORES_BASE_NIVEL.keys()), NIVEL_WEIGHTS)[0]
        self.tier = tier if tier is not None else choices(list(TIERS.keys()), TIER_WEIGHTS)[0]
        self.name = choices(NOMBRES_ENEMIGO[self.level])[0]
        self.health = self.calculate_health()
        self.damage = self.calculate_damage()

    def calculate_health(self):
        base_health = self.level * 10.0
        tier_modifier = 1 + TIERS[self.tier]
        return base_health * tier_modifier

    def calculate_damage(self):
        base_damage = self.level * 2.0
        tier_modifier = 1 + TIERS[self.tier]
        return base_damage * tier_modifier

    def attack(self, player):
        print(f"{self.name} attacks {player.name} causing {self.damage} damage!")
        player.receive_damage(self.damage)

    def receive_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return self.die()
        return f"{self.name} received {damage} damage, remaining health: {self.health}"

    def die(self):
        return f"{self.name} has been defeated!"