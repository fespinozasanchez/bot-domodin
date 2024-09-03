import unittest
from armors import Armor
from enemys import Enemy
from items import Item
from mage_skill import MageSkill
from player import Player
from skills import Skill
from thief_skill import ThiefSkill
from warrior_skill import WarriorSkill
from weapons import Weapon

class TestArmor(unittest.TestCase):
    def setUp(self):
        # Ajusta los argumentos según la definición real de Armor
        self.armor = Armor(name="Steel Shield", defense_bonus=20)

    def test_apply_bonus(self):
        item = Item(name="Shield")
        self.armor.apply_bonus(item)
        # Añade la lógica específica de cómo aplicar el bonus
        # Por ejemplo, si el bonus se suma a un atributo del item
        self.assertEqual(item.defense_bonus, 20)

    def test_remove_bonus(self):
        item = Item(name="Shield", defense_bonus=20)
        self.armor.remove_bonus(item)
        # Verifica que el bonus se haya removido correctamente
        self.assertEqual(item.defense_bonus, 0)

class TestItem(unittest.TestCase):
    def setUp(self):
        # Ajusta los argumentos según la definición real de Item
        self.item = Item(name="Health Potion")

    def test_apply_bonus(self):
        # Implementa la lógica de prueba para aplicar un bonus
        self.item.apply_bonus()
        # Verifica el estado del item después de aplicar el bonus
        self.assertEqual(self.item.value, 30)  # Ajusta el valor esperado según sea necesario

    def test_remove_bonus(self):
        # Implementa la lógica de prueba para remover un bonus
        self.item.remove_bonus()
        # Verifica el estado del item después de remover el bonus
        self.assertEqual(self.item.value, 30)  # Ajusta el valor esperado según sea necesario

class TestSkill(unittest.TestCase):
    def setUp(self):
        # Ajusta los argumentos según la definición real de Skill
        self.skill = Skill(name="Fireball", mana_cost=20, damage=50, cooldown=5, description="A powerful fire spell", main_attribute="intelligence", secondary_attribute="agility", skill_type="magic", multiplier=1.5)
        self.player = Player(name="Mage", level=1, health=100, mana=100, strength=10, agility=10, intelligence=10)

    def test_can_use(self):
        self.assertTrue(self.skill.can_use(self.player))

    def test_use(self):
        damage = self.skill.use(self.player)
        self.assertEqual(damage, 50)  # Ajusta según el comportamiento real
        self.assertEqual(self.player.mana, 80)

class TestMageSkill(unittest.TestCase):
    def setUp(self):
        # Ajusta los argumentos según la definición real de MageSkill
        self.mage_skill = MageSkill(name="Fireball", mana_cost=20, damage=50, cooldown=5, description="Fire spell", main_attribute="intelligence", secondary_attribute="agility", skill_type="magic", multiplier=1.5, elemental_type="Fire")
        self.player = Player(name="Mage", level=1, health=100, mana=100, strength=10, agility=10, intelligence=10)

    def test_increase_damage_by_intelligence(self):
        self.mage_skill.increase_damage_by_intelligence(self.player)
        expected_damage = 50 + (self.player.intelligence * 0.1)
        self.assertEqual(self.mage_skill.damage, expected_damage)

    def test_can_use(self):
        self.assertTrue(self.mage_skill.can_use(self.player))

class TestThiefSkill(unittest.TestCase):
    def setUp(self):
        # Ajusta los argumentos según la definición real de ThiefSkill
        self.thief_skill = ThiefSkill(name="Backstab", mana_cost=15, damage=40, cooldown=3, description="Sneaky attack", main_attribute="agility", secondary_attribute="strength", skill_type="physical", multiplier=2.0, crit_chance=0.2)
        self.player = Player(name="Thief", level=1, health=100, mana=100, strength=10, agility=10, intelligence=10)

    def test_chance(self):
        chance = self.thief_skill.chance()
        self.assertIn(chance, [True, False])

    def test_use(self):
        damage = self.thief_skill.use(self.player)
        self.assertTrue(damage >= 40)  # Ajusta el valor mínimo según el comportamiento real

class TestWarriorSkill(unittest.TestCase):
    def setUp(self):
        # Ajusta los argumentos según la definición real de WarriorSkill
        self.warrior_skill = WarriorSkill(name="Berserk", mana_cost=30, damage=80, cooldown=10, description="Fury attack", main_attribute="strength", secondary_attribute="agility", skill_type="physical", multiplier=1.8, damage_boost=30, stun_chance=0.1)
        self.player = Player(name="Warrior", level=1, health=100, mana=100, strength=20, agility=10, intelligence=5)

    def test_use(self):
        damage = self.warrior_skill.use(self.player)
        self.assertEqual(damage, 80)  # Ajusta según el comportamiento real
        self.assertEqual(self.player.mana, 70)

class TestWeapon(unittest.TestCase):
    def setUp(self):
        # Ajusta los argumentos según la definición real de Weapon
        self.weapon = Weapon(name="Sword", damage_bonus=30)
        self.player = Player(name="Warrior", level=1, health=100, mana=100, strength=10, agility=10, intelligence=10)

    def test_apply_bonus(self):
        self.weapon.apply_bonus(self.player)
        self.assertEqual(self.player.strength, 40)  # Ajusta según el comportamiento real

    def test_remove_bonus(self):
        self.weapon.remove_bonus(self.player)
        self.assertEqual(self.player.strength, 10)  # Ajusta según el comportamiento real

if __name__ == '__main__':
    unittest.main()
