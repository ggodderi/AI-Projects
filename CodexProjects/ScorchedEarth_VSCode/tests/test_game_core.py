import unittest

from game_core import Battle, Projectile, Terrain


class TerrainTests(unittest.TestCase):
    def test_crater_lowers_the_surface(self):
        terrain = Terrain(seed=1)
        before = terrain.surface_y(600)
        terrain.crater(600, before, 40)
        self.assertGreater(terrain.surface_y(600), before)


class BattleTests(unittest.TestCase):
    def test_fire_creates_a_projectile(self):
        battle = Battle(seed=1)
        self.assertTrue(battle.fire())
        self.assertIsNotNone(battle.projectile)

    def test_projectile_resolves_and_turn_changes(self):
        battle = Battle(seed=2)
        battle.fire()
        for _ in range(1000):
            battle.update(1 / 60)
            battle.update_effects(1 / 60)
            if battle.turn == 1 and battle.projectile is None:
                break
        self.assertEqual(battle.turn, 1)
        self.assertIsNone(battle.projectile)

    def test_damage_is_clamped(self):
        battle = Battle(seed=3)
        battle.tanks[1].health = 1
        battle.projectile = Projectile(battle.tanks[1].x, battle.tank_y(battle.tanks[1]), 0, 0, 0)
        battle.resolve_impact(battle.tanks[1].x, battle.tank_y(battle.tanks[1]), 1)
        self.assertEqual(battle.tanks[1].health, 0)
        self.assertTrue(battle.game_over)


if __name__ == "__main__":
    unittest.main()

