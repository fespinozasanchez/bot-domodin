# item.py

class Item:
    def __init__(self, name, item_type, description, increase_stat=None, increase_amount=0, effect=None):
        """
        name: Nombre del ítem.
        item_type: Tipo de ítem (ej. 'Weapon', 'Armor').
        description: Descripción del ítem.
        increase_stat: Atributo que aumenta al equipar el ítem (opcional).
        increase_amount: Cantidad que se incrementa al equipar el ítem (opcional).
        effect: Efecto adicional que puede tener el ítem (opcional, puede ser una función).
        """
        self.name = name
        self.item_type = item_type
        self.description = description
        self.increase_stat = increase_stat
        self.increase_amount = increase_amount
        self.effect = effect

    def apply_bonus(self, player):
        """
        Aplica el bono del ítem al jugador, incrementando las estadísticas o aplicando un efecto.
        """
        if self.increase_stat and self.increase_amount:
            setattr(player, self.increase_stat, getattr(
                player, self.increase_stat) + self.increase_amount)

        if self.effect:
            self.effect(player)

    def remove_bonus(self, player):
        """
        Remueve el bono del ítem cuando el jugador lo desequipa.
        """
        if self.increase_stat and self.increase_amount:
            setattr(player, self.increase_stat, getattr(
                player, self.increase_stat) - self.increase_amount)

    def use(self, player):
        """
        Método opcional para usar el ítem, si es aplicable (por ejemplo, pociones).
        """
        if self.effect:
            self.effect(player)
            print(f"{self.name} used on {player.name}.")
        else:
            print(f"{self.name} cannot be used directly.")
