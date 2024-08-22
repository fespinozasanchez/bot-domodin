# mage_skill.py
from skills import Skill


class MageSkill(Skill):
    def __init__(self, name, description, secondary_attribute, skill_type, mana_cost, multiplier, elemental_type, cooldown, damage):
        """
        name: Nombre de la habilidad mágica.
        description: Descripción de la habilidad.
        secondary_attribute: Atributo secundario que afecta la habilidad.
        skill_type: Tipo de habilidad (ej. 'offensive').
        mana_cost: Costo de mana para usar la habilidad.
        multiplier: Multiplicador que se aplica al atributo principal (inteligencia).
        elemental_type: Tipo de elemento de la habilidad (ej. 'Fire', 'Ice').
        cooldown: Turnos de cooldown antes de que la habilidad pueda ser utilizada de nuevo.
        damage: Daño base adicional que causa la habilidad.
        """
        super().__init__(name, description, "intelligence", secondary_attribute,
                         skill_type, mana_cost, multiplier, damage, cooldown=cooldown)
        self.elemental_type = elemental_type

    def use(self, player, target=None):
        if self.can_use(player):
            player.mana -= self.mana_cost
            total_damage = getattr(
                player, self.main_attribute) * self.multiplier + self.damage

            if target:
                # Aplica el daño principal
                target.health -= total_damage

                # Aplica efectos elementales, si corresponde
                if self.elemental_type:
                    self.apply_elemental_effect(target)

                # Asegúrate de que la salud del enemigo no caiga por debajo de 0
                target.health = max(0, target.health)
                print(f"Mage skill used! Total damage: {
                      total_damage}, Enemy health: {target.health}")

            self.current_cooldown = self.cooldown
            return total_damage
        elif self.current_cooldown > 0:
            print(f"Skill {self.name} is on cooldown for {
                  self.current_cooldown} more turn(s).")
        else:
            print(
                "No tienes suficiente mana o no cumples con los requisitos para usar esta habilidad.")
        return 0

    def apply_elemental_effect(self, target):
        """
        Aplica efectos elementales al objetivo, dependiendo del tipo de elemento.
        """
        if self.elemental_type == "Fire":
            target.health -= 5  # Ejemplo de efecto de quemadura
            print(f"{target.name} is burned by {self.elemental_type}!")
        elif self.elemental_type == "Ice":
            target.stunned = True  # Ejemplo de efecto de congelación
            print(f"{target.name} is frozen by {self.elemental_type}!")

    def reduce_cooldown(self):
        """
        Reduce el cooldown de la habilidad al final de cada turno.
        """
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
