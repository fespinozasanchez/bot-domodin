class Player:
    from utils.data_manager import load_items
    items = load_items()

    def __init__(self, name, level=1, health=100, strength=10, intelligence=10, agility=10, mana=100, stats_points=15,
                 weapon=None, armor=None, boots=None, helmet=None, exp=0):
        self.name = name
        self.level = level
        self.health = health
        self.strength = strength
        self.intelligence = intelligence
        self.agility = agility
        self.mana = mana + (self.intelligence * 0.3)
        self.stats_points = stats_points
        self.weapon = weapon if weapon else Player.items[0] if Player.items else None
        self.armor = armor if armor else Player.items[1] if len(Player.items) > 1 else None
        self.boots = boots if boots else Player.items[4] if len(Player.items) > 4 else None
        self.helmet = helmet  if helmet else Player.items[2] if len(Player.items) > 2 else None
        self.exp = exp
        self.inventory = []

        if self.weapon:
            self.inventory.append(self.weapon)
        if self.armor:
            self.inventory.append(self.armor)
        if self.boots:
            self.inventory.append(self.boots)
        if self.helmet:
            self.inventory.append(self.helmet)

        self.skills = []

    def attack(self):
        if self.strength>self.intelligence and self.strength>self.agility:
            damage = self.strength * 1.5
        elif self.intelligence>self.strength and self.intelligence>self.agility:
            damage = self.intelligence * 1.5
        elif self.agility>self.strength and self.agility>self.intelligence:
            damage = self.agility * 1.5
        return damage

    def recieve_damage(self, damage):
        damage-= self.agility * 0.4
        self.health -= damage


    def use_stat_point(self, stat):
        if self.stats_points > 0:
            if stat == "str":
                self.strength += 1
            elif stat == "int":
                self.intelligence += 1
                self.mana += 3
            elif stat == "agi":
                self.agility += 1
            self.stats_points -= 1
        else:
            print("No tienes mas puntos para usar")   

    
    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        self.inventory.remove(item)

    def show_inventory(self):
        return [item.name for item in self.inventory]
    
    def show_skills(self):
        return [skill.name for skill in self.skills]


    def level_up(self):
        if self.exp > 100:
            self.exp = 0
            self.level += 1
            self.health += 10
            self.strength += 2
            self.intelligence += 2
            self.agility += 2
            self.stats_points += 5

    def show_stats(self):
        return {
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "strength": self.strength,
            "intelligence": self.intelligence,
            "agility": self.agility,
            "mana": self.mana,
            "stats_points": self.stats_points,
        }
