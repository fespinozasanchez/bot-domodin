# armor.py
from items import Item


class Armor(Item):
    def __init__(self, name, description, increase_stat, increase_amount, defense_value=0):
        """
        name: Nombre de la armadura.
        description: Descripción de la armadura.
        increase_stat: El atributo que se verá incrementado al equipar la armadura (ej. 'mana', 'health').
        increase_amount: La cantidad que se incrementará al equipar la armadura.
        defense_value: El valor de defensa que otorga la armadura (opcional).
        """
        super().__init__(name, "Armor", description, increase_stat, increase_amount)
        # Valor de defensa adicional que proporciona la armadura
        self.defense_value = defense_value

    def apply_bonus(self, player):
        """
        Aplica los bonos de la armadura al jugador, incrementando las estadísticas correspondientes.
        """
        super().apply_bonus(player)  # Usa el método apply_bonus de la clase padre (Item)

        # Aplicar bono de defensa si está presente
        if self.defense_value:
            player.defense += self.defense_value

    def remove_bonus(self, player):
        """
        Elimina los bonos de la armadura cuando el jugador se la quita.
        """
        if self.increase_stat == "mana":
            player.mana -= self.increase_amount
        elif self.increase_stat == "health":
            player.health -= self.increase_amount

        if self.defense_value:
            player.defense -= self.defense_value
