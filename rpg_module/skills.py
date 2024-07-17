class Skill:
    def __init__(self, name, description, main_attribute, secondary_attribute, skill_type, mana_cost, multiplier,damage):
        self.name = name
        self.description = description
        self.main_attribute = main_attribute
        self.secondary_attribute = secondary_attribute
        self.skill_type = skill_type
        self.mana_cost = mana_cost
        self.multiplier = multiplier
        self.damage = damage

    def can_use(self, player):
        main_attr_value = getattr(player, self.main_attribute, 0)
        secondary_attr_value = getattr(player, self.secondary_attribute, 0)
        return main_attr_value > 0 and secondary_attr_value > 0 and player.mana >= self.mana_cost

    def use(self, player):
        if self.can_use(player):
            player.mana -= self.mana_cost
            return getattr(player, self.main_attribute) * self.multiplier
        else:
            print("No tienes suficiente mana o no cumples con los requisitos para usar esta habilidad.")
            return 0
        
    def calculate_damage(self, player):
        if self.can_use(player):
            player.mana -= self.mana_cost
            return getattr(player, self.main_attribute) * self.multiplier + self.damage
        else:
            print("No tienes suficiente mana o no cumples con los requisitos para usar esta habilidad.")
            return 0