# interfaces.py

class Attacker:
    def attack(self):
        raise NotImplementedError("Subclasses should implement this!")

class SkillUser:
    def use_special_ability(self):
        raise NotImplementedError("Subclasses should implement this!")

class ItemEquipper:
    def equip_item(self, item):
        raise NotImplementedError("Subclasses should implement this!")

class ItemUser:
    def use_item(self, item):
        raise NotImplementedError("Subclasses should implement this!")

class DamageReceiver:
    def receive_damage(self, damage):
        raise NotImplementedError("Subclasses should implement this!")
