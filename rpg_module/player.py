from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from utils.rpg_data_manager import Base

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    level = Column(Integer, default=1)
    health = Column(Float, default=100)
    strength = Column(Float, default=10)
    intelligence = Column(Float, default=10)
    agility = Column(Float, default=10)
    mana = Column(Float, default=100)
    stats_points = Column(Integer, default=15)
    weapon_id = Column(Integer, ForeignKey('weapons.id', ondelete="SET NULL"))
    armor_id = Column(Integer, ForeignKey('armors.id', ondelete="SET NULL"))

    weapon = relationship("Weapon", back_populates="players")
    armor = relationship("Armor", back_populates="players")
    skills = relationship("Skill", secondary='player_skills', back_populates="players")

    inventory = relationship("PlayerInventory", back_populates="player")

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
        

        # Actualizar efectos de estado al final del turno
        self.update_status_effects()

        # Reset evasion boost after turn ends
        self.evasion = 0


