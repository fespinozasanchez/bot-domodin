# skill.py

class Skill:
    def __init__(self, name, description, main_attribute, secondary_attribute, skill_type, mana_cost, multiplier, damage, effect=None, cooldown=0):
        """
        name: Nombre de la habilidad.
        description: Descripción de la habilidad.
        main_attribute: Atributo principal que afecta el poder de la habilidad (ej. 'strength', 'intelligence').
        secondary_attribute: Atributo secundario que puede influir en la habilidad (opcional).
        skill_type: Tipo de habilidad (ej. 'offensive', 'defensive').
        mana_cost: Costo de mana para usar la habilidad.
        multiplier: Multiplicador que se aplica al atributo principal para calcular el daño.
        damage: Daño base adicional que causa la habilidad.
        effect: Efecto adicional que puede aplicar la habilidad (opcional, puede ser una función).
        cooldown: Turnos de cooldown antes de que la habilidad pueda ser utilizada de nuevo.
        """
        self.name = name
        self.description = description
        self.main_attribute = main_attribute
        self.secondary_attribute = secondary_attribute
        self.skill_type = skill_type
        self.mana_cost = mana_cost
        self.multiplier = multiplier
        self.damage = damage
        self.effect = effect  # Efecto adicional que la habilidad puede aplicar
        self.cooldown = cooldown
        self.current_cooldown = 0

    def can_use(self, player):
        """
        Verifica si la habilidad se puede usar basándose en los atributos del jugador y el costo de mana.
        """
        main_attr_value = getattr(player, self.main_attribute, 0)
        secondary_attr_value = getattr(player, self.secondary_attribute, 0)
        return main_attr_value > 0 and secondary_attr_value >= 0 and player.mana >= self.mana_cost and self.current_cooldown == 0

    def use(self, player, target=None):
        """
        Usa la habilidad, aplicando daño y efectos si es posible.
        """
        if self.can_use(player):
            player.mana -= self.mana_cost
            damage = getattr(player, self.main_attribute) * \
                self.multiplier + self.damage

            # Aplicar efecto adicional si existe
            if self.effect and target:
                self.effect(target)

            # Activar el cooldown
            self.current_cooldown = self.cooldown

            return damage
        else:
            return 0

    def calculate_damage(self, player):
        """
        Calcula el daño total que causaría la habilidad basándose en los atributos del jugador.
        """
        if self.can_use(player):
            return getattr(player, self.main_attribute) * self.multiplier + self.damage
        else:
            return 0

    def reduce_cooldown(self):
        """
        Reduce el cooldown de la habilidad al final de cada turno.
        """
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def apply_effect(self, target):
        """
        Aplica el efecto adicional de la habilidad, si existe.
        """
        if self.effect:
            self.effect(target)
