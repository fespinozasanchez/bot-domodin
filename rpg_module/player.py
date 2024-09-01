# player.py

from weapons import Weapon
from armors import Armor
from mage_skill import MageSkill
from warrior_skill import WarriorSkill
from thief_skill import ThiefSkill


class Player:

    def __init__(self, name, level=1, health=100, strength=10, intelligence=10, agility=10, mana=100, stats_points=15,
                 weapon=None, armor=None, boots=None, helmet=None, exp=0):
        """
        name: Nombre del jugador.
        level: Nivel del jugador.
        health: Salud del jugador.
        strength: Fuerza del jugador.
        intelligence: Inteligencia del jugador.
        agility: Agilidad del jugador.
        mana: Mana del jugador.
        stats_points: Puntos de estadísticas disponibles para mejorar.
        weapon: Arma inicial del jugador (opcional).
        armor: Armadura inicial del jugador (opcional).
        boots: Botas iniciales del jugador (opcional).
        helmet: Casco inicial del jugador (opcional).
        exp: Experiencia inicial del jugador.
        """
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
        self.skills = []
        self.evasion = 0
        self.defense = 0  # Atributo de defensa que puede ser modificado por armaduras
        self.status_effects = []  # Efectos de estado que afectan al jugador

        self.equip_initial_items()

    def equip_initial_items(self):
        """
        Equipa los ítems iniciales del jugador y aplica sus bonos.
        """
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
        if self.weapon:
            damage = self.weapon.calculate_damage(self)
        else:
            # Si no tiene un arma equipada, el ataque es solo basado en la fuerza
            damage = self.strength * 1.5
        return damage

    def receive_damage(self, damage):
        # La defensa del jugador y la agilidad reducen el daño recibido
        reduced_damage = max(0, damage - (self.defense + self.agility * 0.4))
        self.health -= reduced_damage
        return reduced_damage

    def receive_damage(self, damage):
        reduced_damage = max(0, damage - (self.defense + self.agility * 0.4))
        self.health -= reduced_damage
        return reduced_damage

        # Chequea si el jugador ha muerto
        if self.health <= 0:
            self.die()

    def die(self):
        """
        Maneja la muerte del jugador.
        """
        return (f"{self.name} has been defeated!")

    def use_stat_point(self, stat):
        """
        Usa un punto de estadísticas para mejorar un atributo.
        """
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
            return("No tienes más puntos para usar")

    def add_item(self, item):
        """
        Añade un ítem al inventario del jugador.
        """
        self.inventory.append(item)

    def remove_item(self, item):
        """
        Remueve un ítem del inventario del jugador.
        """
        if item in self.inventory:
            item.remove_bonus(self)  # Revertir el efecto del ítem al removerlo
            self.inventory.remove(item)

    def get_inventory(self):
        """
        Retorna una lista con los nombres de los ítems en el inventario.
        """
        return [item.name for item in self.inventory]

    def add_skill(self, skill):
        """
        Añade una habilidad al conjunto de habilidades del jugador.
        """
        self.skills.append(skill)

    def remove_skill(self, skill):
        """
        Remueve una habilidad del conjunto de habilidades del jugador.
        """
        if skill in self.skills:
            self.skills.remove(skill)

    def get_skills(self):
        """
        Retorna una lista con los nombres de las habilidades del jugador.
        """
        return [skill.name for skill in self.skills]

    def level_up(self):
        """
        Mejora el nivel del jugador al ganar suficiente experiencia.
        """
        if self.exp >= 100:
            self.exp = 0
            self.level += 1
            self.health += 10
            self.strength += 2
            self.intelligence += 2
            self.agility += 2
            self.stats_points += 5
            return (f"{self.name} has leveled up to level {self.level}!")

    def get_stats(self):
        """
        Retorna las estadísticas del jugador como un diccionario.
        """
        return {
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "strength": self.strength,
            "intelligence": self.intelligence,
            "agility": self.agility,
            "mana": self.mana,
            "stats_points": self.stats_points,
            "defense": self.defense,
        }

    def use_skill(self, skill_name, enemy=None):
        """
        Usa una habilidad del jugador contra un enemigo o por sí mismo.
        """
        for skill in self.skills:
            if skill.name == skill_name:
                if isinstance(skill, WarriorSkill):
                    damage = skill.use(self, enemy)
                else:
                    damage = skill.use(self)
                return f"{self.name} uses {skill_name}, causing {damage} damage!"
        return f"{self.name} doesn't have the skill {skill_name}."

    def apply_status_effect(self, effect):
        """
        Aplica un efecto de estado al jugador.
        """
        self.status_effects.append(effect)

    def update_status_effects(self):
        """
        Actualiza los efectos de estado activos, eliminando los que hayan expirado.
        """
        for effect in self.status_effects:
            effect.apply(self)
            if not effect.is_active():
                self.status_effects.remove(effect)

    def end_turn(self):
        """
        Lógica de fin de turno, como reducir el cooldown de las habilidades y actualizar efectos de estado.
        """
        for skill in self.skills:
            if isinstance(skill, MageSkill):
                skill.reduce_cooldown()

        # Actualizar efectos de estado al final del turno
        self.update_status_effects()

        # Reset evasion boost after turn ends
        self.evasion = 0
