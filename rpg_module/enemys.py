# enemys.py

class Enemy:
    def __init__(self, name, enemy_type, level, health, attack_power, defense, weaknesses=None, resistances=None):
        self.name = name
        self.enemy_type = enemy_type
        self.level = level
        self.health = health
        self.attack_power = attack_power
        self.defense = defense
        self.weaknesses = weaknesses if weaknesses is not None else []
        self.resistances = resistances if resistances is not None else []
        self.stunned = False  # Atributo para manejar el estado de aturdimiento

    def attack(self, target):
        damage = max(0, self.attack_power - target.defense)
        print(f"Enemy attacks! Calculated damage: {damage}")
        target.receive_damage(damage)
        return damage

    def defend(self, incoming_damage, damage_type=None):
        """
        Defiende contra un ataque y calcula el daño recibido, teniendo en cuenta las resistencias y debilidades.
        """
        if damage_type in self.weaknesses:
            incoming_damage *= 1.5  # Aumenta el daño si es débil al tipo de ataque
        elif damage_type in self.resistances:
            incoming_damage *= 0.5  # Reduce el daño si es resistente al tipo de ataque

        reduced_damage = max(0, incoming_damage - self.defense)
        self.health -= reduced_damage

        # Check for death
        if self.health <= 0:
            self.die()

        return reduced_damage

    def die(self):
        """
        Maneja la muerte del enemigo.
        """
        print(f"{self.name} has been defeated!")

    def is_alive(self):
        """
        Verifica si el enemigo sigue vivo.
        """
        return self.health > 0
