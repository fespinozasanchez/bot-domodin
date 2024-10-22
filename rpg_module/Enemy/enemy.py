from random import choices
import numpy as np
from .enemy_const import  TIERS, TIER_WEIGHTS, NOMBRES_ENEMIGO, LEVEL_RANGE

class Enemy:
    def __init__(self, level=None, tier=None):
        self.level = level if level is not None else self.calculate_enemy_level()
        self.tier = tier if tier is not None else choices(list(TIERS.keys()), TIER_WEIGHTS)[0]
        self.name = choices(NOMBRES_ENEMIGO[1])[0]
        self.health = self.calculate_health()
        self.damage = self.calculate_damage()
        self.experience = self.calculate_enemy_experience(self.level, self.tier)

    def generate_level_weights(self,min_level,max_level):
        levels=np.arange(min_level, max_level+1)
        weights=1/np.sqrt(levels)
        normalized_weights=weights/weights.sum()
        return normalized_weights

    def calculate_enemy_level(self):
        levels=list(range(LEVEL_RANGE['min_level'],LEVEL_RANGE['max_level']+1))
        level_weights=self.generate_level_weights(LEVEL_RANGE['min_level'],LEVEL_RANGE['max_level'])
        return choices(levels,level_weights,k=1)[0]   

    def calculate_health(self):
        # Constantes de la fórmula polinómica
        a = 3
        b = 6
        c = 10

        base_health = a * (self.level ** 2) + b * self.level + c
        tier_modifier = 1 + TIERS[self.tier]
        return round(base_health * tier_modifier)

    def calculate_damage(self):
        # Constantes de la fórmula polinómica
        a = 4  # Factor de crecimiento cuadrático
        b = 7  # Factor de crecimiento lineal
        c = 10  # Daño base

        # Fórmula polinómica para calcular el daño
        base_damage = a * (self.level ** 2) + b * self.level + c

        # Modificador de tier para ajustar el daño según la categoría del enemigo
        tier_modifier = 1 + TIERS[self.tier]

        # Daño final ajustado por el tier
        return round(base_damage * tier_modifier)
    
    def calculate_enemy_experience(self,enemy_level, enemy_tier):
        # Factores para el cálculo
        a = 100  # Experiencia base
        b = 1.1  # Factor de crecimiento exponencial

        # Modificador basado en el tier del enemigo

        tier_modifier = TIERS.get(enemy_tier, 0)  # Obtiene el modificador de tier

        # Cálculo de la experiencia usando una fórmula exponencial
        experience_given = round((a * (b ** enemy_level) * (1 + tier_modifier))*0.5)

        return round(experience_given)

    def attack(self, player):
        print(f"{self.name} attacks {player.name} causing {self.damage:.2f} damage!")
        player.receive_damage(self.damage)

    def receive_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return self.die()
        return f"{self.name} received {damage:.2f} damage, remaining health: {self.health:.2f}"

    def die(self):
        return f"{self.name} has been defeated!"
    