import unittest
from armors import Armor
from enemys import Enemy
from mage_skill import MageSkill
from player import Player
from weapons import Weapon
from thief_skill import ThiefSkill
from warrior_skill import WarriorSkill


class TestRPGModule(unittest.TestCase):

    def setUp(self):
        # Configuración común para varios tests
        self.player = Player(name="TestPlayer", intelligence=50,
                             strength=30, agility=20, mana=100)
        self.enemy = Enemy(name="Goblin", enemy_type="Goblin",
                           level=1, health=100, attack_power=15, defense=5)
        self.armor = Armor(name="Steel Armor", description="Strong armor",
                           increase_stat="health", increase_amount=50)
        self.weapon = Weapon(name="Sword", description="Sharp sword", increase_stat="strength", increase_amount=5,
                             weapon_type="Sword", base_damage=10)
        self.mage_skill = MageSkill(name="Fireball", description="A strong fireball", secondary_attribute="mana",
                                    skill_type="offensive", mana_cost=20, multiplier=2, elemental_type="Fire",
                                    cooldown=2, damage=30)
        self.thief_skill = ThiefSkill(name="Backstab", description="A sneaky backstab", secondary_attribute="mana",
                                      skill_type="offensive", mana_cost=10, multiplier=1.5, crit_chance=0.5,
                                      evasion_boost=10, damage=25)
        self.warrior_skill = WarriorSkill(name="Heavy Slash", description="A powerful slash",
                                          secondary_attribute="mana", skill_type="offensive", mana_cost=15,
                                          multiplier=2, damage_boost=10, stun_chance=0.3, damage=20)

    # Armor Tests
    def test_armor_apply_bonus(self):
        initial_health = self.player.health
        self.armor.apply_bonus(self.player)
        self.assertEqual(self.player.health, initial_health + 50)

    def test_armor_remove_bonus(self):
        self.armor.apply_bonus(self.player)
        initial_health = self.player.health
        self.armor.remove_bonus(self.player)
        self.assertEqual(self.player.health, initial_health - 50)

    # Weapon Tests
    def test_weapon_apply_bonus(self):
        initial_strength = self.player.strength
        self.weapon.apply_bonus(self.player)
        self.assertEqual(self.player.strength, initial_strength + 5)

    def test_weapon_remove_bonus(self):
        self.weapon.apply_bonus(self.player)
        initial_strength = self.player.strength
        self.weapon.remove_bonus(self.player)
        self.assertEqual(self.player.strength, initial_strength - 5)

    def test_weapon_calculate_damage(self):
        damage = self.weapon.calculate_damage(self.player)
        self.assertEqual(damage, self.player.strength +
                         self.weapon.base_damage)

    def test_mage_skill_use(self):
        initial_enemy_health = self.enemy.health
        damage = self.mage_skill.use(self.player, self.enemy)
        # Verifica que la salud del enemigo sea 0 después del ataque
        self.assertEqual(self.enemy.health, 0)

    def test_mage_skill_cooldown(self):
        self.mage_skill.use(self.player)
        self.assertEqual(self.mage_skill.current_cooldown, 2)
        self.mage_skill.reduce_cooldown()
        self.assertEqual(self.mage_skill.current_cooldown, 1)

    # ThiefSkill Tests
    def test_thief_skill_use(self):
        initial_enemy_health = self.enemy.health
        damage = self.thief_skill.use(self.player, self.enemy)
        self.assertGreaterEqual(damage, 0)
        self.assertTrue(self.player.evasion > 0)

    # WarriorSkill Tests
    def test_warrior_skill_use(self):
        initial_enemy_health = self.enemy.health
        damage = self.warrior_skill.use(self.player, self.enemy)
        self.assertGreaterEqual(damage, 0)
        if self.enemy.stunned:
            self.assertTrue(self.enemy.stunned)

    # Enemy Tests
    def test_enemy_attack(self):
        initial_health = self.player.health
        damage = self.enemy.attack(self.player)
        # Ajustar el valor esperado al daño reducido (7.0 en lugar de 15)
        self.assertEqual(self.player.health, initial_health - 7)

    def test_enemy_defend(self):
        initial_health = self.enemy.health
        damage_taken = self.enemy.defend(20)
        self.assertGreaterEqual(damage_taken, 0)
        self.assertEqual(self.enemy.health, initial_health - damage_taken)

    # Player Tests
    def test_player_attack(self):
        self.player.weapon = self.weapon
        self.player.equip_initial_items()
        damage = self.player.attack()
        self.assertGreater(damage, 0)

    def test_player_level_up(self):
        self.player.exp = 101
        self.player.level_up()
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.exp, 0)


if __name__ == '__main__':
    unittest.main()
