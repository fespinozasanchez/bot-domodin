from .enemy import Enemy
from random import randint,choices
from .enemy_const import  ENEMY_BOSS_NAMES
class BossEnemy(Enemy):
    def __init__(self, level, tier='S++'):
        super().__init__(level, tier)
        self.health = round(self.health *1.1)
        self.damage = round(self.damage * 1.01)
        self.experience = round(self.experience * 3)
        self.name =  self.name = choices(ENEMY_BOSS_NAMES[1])[0]
        self.tier = tier
        self.level = max(1, randint(level - 10, level + 10))
        self.boss_message = f"¡Te has encontrado con un jefe! {self.name} es un enemigo formidable que no te lo pondrá fácil."

    def calculate_health(self):
        return round(super().calculate_health() * 1.1)

    def calculate_damage(self):
        return round(super().calculate_damage() * 1)

    def calculate_enemy_experience(self, enemy_level, enemy_tier):
        # Llamamos al método de la clase padre y lo multiplicamos por 2
        return round(super().calculate_enemy_experience(enemy_level, enemy_tier) * 3)
