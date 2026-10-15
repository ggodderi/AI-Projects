import math
from random import Random
import unittest

from core import (GRAVITY, SHOP, STEP, TURN_LIMIT, WEAPONS, WORLD_H, WORLD_W,
                  Match, Projectile, Tank, Terrain, advance, launch)


def drain(generator):
    for _ in generator:
        pass


def resolve(match):
    for _ in range(2200):
        match.tick()
        if match.phase != "flight":
            break
    if match.phase == "flight":
        raise AssertionError("Projectile failed to terminate")
    match.end_turn()


class TerrainTests(unittest.TestCase):
    def test_generation_is_bounded_and_reproducible(self):
        a, b = Terrain(Random(18)), Terrain(Random(18))
        self.assertEqual(a.heights, b.heights)
        self.assertEqual(len(a.heights), WORLD_W)
        self.assertTrue(all(150 <= y <= 420 for y in a.heights))

    def test_crater_only_removes_ground_and_respects_floor(self):
        terrain = Terrain(Random(4))
        before = terrain.heights.copy()
        terrain.crater(500, terrain.ground(500), 65)
        self.assertTrue(all(a >= b for a, b in zip(terrain.heights, before)))
        self.assertGreater(terrain.ground(500), before[500])
        terrain.crater(500, WORLD_H, 500)
        self.assertLessEqual(max(terrain.heights), WORLD_H - 15)

    def test_airburst_does_not_dig_through_gap(self):
        terrain = Terrain(Random(4))
        before = terrain.heights.copy()
        terrain.crater(500, 0, 25)
        self.assertEqual(before, terrain.heights)

    def test_boundary_craters_and_launch_pads(self):
        terrain = Terrain(Random(7))
        terrain.platform(100)
        self.assertEqual(len(set(terrain.heights[80:121])), 1)
        for x in (-50, 0, WORLD_W - 1, WORLD_W + 50):
            terrain.crater(x, 400, 80)
        self.assertEqual(len(terrain.heights), WORLD_W)


class PhysicsTests(unittest.TestCase):
    def setUp(self):
        self.terrain = Terrain(Random(1))
        self.terrain.heights = [480.0] * WORLD_W

    def test_analytic_gravity_and_wind(self):
        p = Projectile(100, 100, 50, -50, 0, 0)
        self.assertEqual(advance(p, .1, 20, self.terrain, []), "flying")
        self.assertAlmostEqual(p.x, 105.1)
        self.assertAlmostEqual(p.y, 96.15)
        self.assertAlmostEqual(p.vx, 52)
        self.assertAlmostEqual(p.vy, -27)

    def test_integration_independent_of_timestep(self):
        a, b = Projectile(100, 100, 50, -60, 0, 0), Projectile(100, 100, 50, -60, 0, 0)
        for _ in range(30):
            advance(a, 1 / 60, -12, self.terrain, [])
        for _ in range(60):
            advance(b, STEP, -12, self.terrain, [])
        self.assertAlmostEqual(a.x, b.x, places=8)
        self.assertAlmostEqual(a.y, b.y, places=8)

    def test_swept_collision_catches_thin_hill(self):
        self.terrain.heights[150] = 50
        p = Projectile(100, 100, 700, 0, 0, 0)
        self.assertEqual(advance(p, .15, 0, self.terrain, []), "impact")
        self.assertLess(abs(p.x - 150), 2)

    def test_tank_collision_and_world_exit(self):
        p = Projectile(100, 200, 500, 0, 0, 0)
        tank = Tank(150, 210, 90)
        self.assertEqual(advance(p, .1, 0, self.terrain, [tank]), "impact")
        p = Projectile(1119, 100, 700, 0, 0, 0)
        self.assertEqual(advance(p, .1, 0, self.terrain, []), "miss")

    def test_dead_tanks_do_not_block_shells(self):
        p = Projectile(100, 200, 500, 0, 0, 0)
        self.assertEqual(advance(p, .1, 0, self.terrain, [Tank(150, 210, 90, hp=0)]), "flying")

    def test_launch_direction_and_limits(self):
        a, b = launch(Tank(100, 300, 45), 0, 0), launch(Tank(1000, 300, 135), 0, 1)
        self.assertGreater(a.vx, 0)
        self.assertLess(b.vx, 0)
        self.assertLess(a.vy, 0)
        self.assertLess(b.vy, 0)


class MatchTests(unittest.TestCase):
    def setUp(self):
        self.match = Match(seed=12)

    def test_invalid_settings(self):
        for args in ({"rounds": 0}, {"rounds": 3.0}, {"mode": "bad"}, {"skill": "bad"}):
            with self.assertRaises(ValueError):
                Match(**args)

    def test_shot_consumes_one_ammo_and_rejects_double_fire(self):
        match = self.match
        match.tanks[0].weapon = 1
        ammo = match.players[0].ammo[1]
        self.assertTrue(match.fire())
        self.assertFalse(match.fire())
        self.assertEqual(match.players[0].ammo[1], ammo - 1)
        resolve(match)
        self.assertIn(match.phase, ("aim", "round_over"))

    def test_empty_weapon_falls_back_to_unlimited_shell(self):
        match = self.match
        match.tanks[0].weapon = 3
        self.assertTrue(match.fire())
        self.assertEqual(match.tanks[0].weapon, 0)
        self.assertEqual(match.players[0].ammo[0], -1)

    def test_weapon_cycle_skips_empty_ammunition(self):
        self.match.select_weapon(1)
        self.assertEqual(self.match.tanks[0].weapon, 1)
        self.match.select_weapon(1)
        self.assertEqual(self.match.tanks[0].weapon, 2)
        self.match.select_weapon(1)
        self.assertEqual(self.match.tanks[0].weapon, 0)

    def test_shield_absorbs_damage_and_credit_is_capped(self):
        match = self.match
        match.tanks[1].shield = 40
        match.damage(1, 65, 0)
        self.assertEqual(match.tanks[1].shield, 0)
        self.assertEqual(match.tanks[1].hp, 75)
        self.assertEqual(match.players[0].damage, 65)
        match.damage(1, 1000, 0)
        self.assertEqual(match.players[0].damage, 140)
        self.assertEqual(match.players[0].cash, 900 + 140 * 4)

    def test_friendly_fire_does_not_earn_cash(self):
        before = self.match.players[0].cash
        self.match.damage(0, 35, 0)
        self.assertEqual(self.match.tanks[0].hp, 65)
        self.assertEqual(self.match.players[0].cash, before)

    def test_explosion_deforms_terrain_and_drops_tank(self):
        match = self.match
        target = match.tanks[1]
        old_y = target.y
        match.explode(Projectile(target.x, target.y, 0, 0, 1, 0))
        self.assertGreater(target.y, old_y + 40)
        self.assertLess(target.hp, 100)
        self.assertGreater(match.players[0].damage, 0)

    def test_cluster_splits_exactly_once(self):
        match = self.match
        match.phase = "flight"
        match.projectiles = [Projectile(500, 10, 70, -1, 2, 0)]
        match.tick(.02)
        self.assertEqual(len(match.projectiles), 5)
        self.assertTrue(all(p.pellet for p in match.projectiles))
        self.assertEqual(len({p.vx for p in match.projectiles}), 5)
        match.tick(.02)
        self.assertEqual(len(match.projectiles), 5)
        resolve(match)

    def test_simultaneous_destruction_is_draw(self):
        match = self.match
        for tank in match.tanks:
            tank.hp = 0
        match.phase = "settle"
        match.end_turn()
        self.assertIsNone(match.round_winner)
        self.assertEqual(match.phase, "round_over")
        self.assertEqual([p.wins for p in match.players], [0, 0])

    def test_turn_limit_prefers_remaining_strength(self):
        match = self.match
        match.turn = TURN_LIMIT
        match.tanks[1].hp = 30
        match.phase = "settle"
        match.end_turn()
        self.assertEqual(match.round_winner, 0)

    def test_turn_limit_tie_is_draw(self):
        match = self.match
        match.turn = TURN_LIMIT
        match.phase = "settle"
        match.end_turn()
        self.assertIsNone(match.round_winner)

    def test_shop_constraints_and_round_reset(self):
        match = self.match
        self.assertFalse(match.buy(0, 0))
        match.finish_round(0)
        match.players[0].cash = 3000
        self.assertTrue(match.buy(0, 3))
        self.assertTrue(match.buy(0, 3))
        before = match.players[0].cash
        self.assertFalse(match.buy(0, 3))
        self.assertEqual(match.players[0].cash, before)
        self.assertTrue(match.buy(0, 0))
        ammo = match.players[0].ammo.copy()
        match.tanks[0].hp = 1
        match.start_round()
        self.assertEqual(match.tanks[0].hp, 100)
        self.assertEqual(match.tanks[0].shield, 80)
        self.assertEqual(match.players[0].next_shield, 0)
        self.assertEqual(match.players[0].ammo, ammo)
        self.assertEqual(match.active, 1)

    def test_shop_rejects_unaffordable_items(self):
        match = self.match
        match.finish_round(None)
        match.players[0].cash = 0
        self.assertFalse(match.buy(0, 0))
        self.assertEqual(match.players[0].cash, 0)

    def test_match_tiebreak_uses_damage(self):
        match = self.match
        match.round = 3
        match.players[0].wins = match.players[1].wins = 1
        match.players[1].damage = 200
        match.finish_round(None)
        self.assertTrue(match.match_over)
        self.assertEqual(match.winner, 1)
        self.assertFalse(match.buy(0, 0))

    def test_ai_finds_useful_shots_across_terrains(self):
        scores = []
        for seed in range(4):
            match = Match(seed=seed, skill="Expert")
            match.active = 1
            drain(match.ai_search())
            self.assertTrue(5 <= match.tanks[1].angle <= 175)
            self.assertTrue(10 <= match.tanks[1].power <= 100)
            match.fire()
            resolve(match)
            scores.append(match.players[1].damage)
        self.assertGreater(sum(scores), 120, scores)

    def test_complete_ai_campaign_terminates(self):
        match = Match(seed=19, skill="Expert")
        shots = 0
        while not match.match_over:
            if match.phase == "aim":
                drain(match.ai_search())
                self.assertTrue(match.fire())
                shots += 1
                resolve(match)
            elif match.phase == "round_over":
                for owner in (0, 1):
                    match.buy(owner, 3)
                    match.buy(owner, 0)
                match.start_round()
            self.assertLessEqual(shots, TURN_LIMIT * 3)
        self.assertEqual(match.round, 3)
        self.assertGreater(sum(p.damage for p in match.players), 100)


if __name__ == "__main__":
    unittest.main()
