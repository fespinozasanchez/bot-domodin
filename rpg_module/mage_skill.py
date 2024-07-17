from skills import Skill

class MageSkill(Skill):
    def __init__(self, name, description, secondary_attribute, skill_type, mana_cost, multiplier, elemental_type, cooldown,damage):
        super().__init__(name, description, "intelligence", secondary_attribute, skill_type, mana_cost, multiplier,damage)
        self.elemental_type = elemental_type
        self.cooldown = cooldown
        self.current_cooldown = 0

    def use(self, player):
        if self.current_cooldown == 0 and self.can_use(player):
            player.mana -= self.mana_cost
            self.current_cooldown = self.cooldown
            return getattr(player, self.main_attribute) * self.multiplier
        elif self.current_cooldown > 0:
            print(f"Skill {self.name} is on cooldown for {self.current_cooldown} more turn(s).")
        else:
            print("No tienes suficiente mana o no cumples con los requisitos para usar esta habilidad.")
        return 0

    def reduce_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1