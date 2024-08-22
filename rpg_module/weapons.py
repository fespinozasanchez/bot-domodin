# weapon.py
from items import Item


class Weapon(Item):
    def __init__(self, name, description, increase_stat, increase_amount, weapon_type, base_damage):
        """
        name: Nombre del arma.
        description: Descripción del arma.
        increase_stat: Atributo que incrementa al equipar el arma (ej. 'strength').
        increase_amount: Cantidad que se incrementa al equipar el arma.
        weapon_type: Tipo de arma (ej. 'Sword', 'Bow').
        base_damage: Daño base que inflige el arma.
        """
        super().__init__(name, "Weapon", description, increase_stat, increase_amount)
        self.weapon_type = weapon_type
        self.base_damage = base_damage

    def apply_bonus(self, player):
        """
        Aplica el bono del arma al jugador, incrementando la estadística correspondiente.
        """
        if self.increase_stat and self.increase_amount:
            setattr(player, self.increase_stat, getattr(
                player, self.increase_stat) + self.increase_amount)
        print(f"{player.name} equipped {self.name}, increasing {
              self.increase_stat} by {self.increase_amount}.")

    def remove_bonus(self, player):
        """
        Remueve el bono del arma cuando se desequipa.
        """
        if self.increase_stat and self.increase_amount:
            setattr(player, self.increase_stat, getattr(
                player, self.increase_stat) - self.increase_amount)
        print(f"{player.name} unequipped {self.name}, reducing {
              self.increase_stat} by {self.increase_amount}.")

    def calculate_damage(self, player):
        """
        Calcula el daño total del arma basado en el atributo principal del jugador y el daño base del arma.
        """
        main_attr_value = getattr(player, self.increase_stat, 0)
        total_damage = main_attr_value + self.base_damage
        return total_damage
