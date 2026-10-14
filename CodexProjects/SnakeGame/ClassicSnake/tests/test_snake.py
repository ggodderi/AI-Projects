import json
from pathlib import Path
from random import Random
import tempfile
import unittest

from snake_core import DIRECTIONS, SnakeGame
from storage import Store


class RulesTests(unittest.TestCase):
    def setUp(self):
        self.game = SnakeGame(rng=Random(12))

    def test_initial_state_and_reset(self):
        self.assertEqual(len(self.game.snake), 3)
        self.assertNotIn(self.game.food, self.game.snake)
        self.game.turn("up")
        self.game.step()
        self.game.reset()
        self.assertEqual(self.game.snake[0], (15, 11))
        self.assertFalse(self.game.turns)
        self.assertEqual(self.game.score, 0)

    def test_eat_and_growth(self):
        self.game.food = (16, 11)
        self.assertEqual(self.game.step(), "eat")
        self.assertEqual(self.game.score, 10)
        self.assertEqual(len(self.game.snake), 4)
        self.assertNotIn(self.game.food, self.game.snake)

    def test_queue_prevents_reversal_and_keeps_two_turns(self):
        self.assertFalse(self.game.turn("left"))
        self.assertTrue(self.game.turn("up"))
        self.assertFalse(self.game.turn("up"))
        self.assertFalse(self.game.turn("down"))
        self.assertTrue(self.game.turn("left"))
        self.assertFalse(self.game.turn("down"))
        self.game.step()
        self.assertEqual(self.game.snake[0], (15, 10))
        self.game.step()
        self.assertEqual(self.game.snake[0], (14, 10))

    def test_wall_collision_and_terminal_noop(self):
        self.game.snake = [(29, 2), (28, 2), (27, 2)]
        before = self.game.snake.copy()
        self.assertEqual(self.game.step(), "dead")
        self.assertEqual(self.game.snake, before)
        self.assertEqual(self.game.step(), "idle")
        self.assertFalse(self.game.turn("up"))

    def test_body_collision(self):
        self.game.snake = [(3, 3), (3, 4), (4, 4), (4, 3), (5, 3)]
        self.assertEqual(self.game.step(), "dead")

    def test_vacating_tail_is_legal(self):
        self.game.snake = [(3, 3), (3, 4), (4, 4), (4, 3)]
        self.game.food = (20, 20)
        self.assertEqual(self.game.step(), "move")
        self.assertEqual(self.game.snake[0], (4, 3))

    def test_complete_board_wins(self):
        game = SnakeGame(6, 4, Random(3))
        game.snake = [(4, 0)] + [(x, y) for y in range(4) for x in range(6)
                                        if (x, y) not in ((4, 0), (5, 0))]
        game.food = (5, 0)
        self.assertEqual(game.step(), "won")
        self.assertTrue(game.won)
        self.assertFalse(game.alive)
        self.assertIsNone(game.food)
        self.assertEqual(len(set(game.snake)), 24)

    def test_all_wall_directions(self):
        for direction, head in [("up", (4, 0)), ("down", (4, 21)),
                                ("left", (0, 4)), ("right", (29, 4))]:
            with self.subTest(direction=direction):
                game = SnakeGame()
                game.snake = [head]
                game.direction = DIRECTIONS[direction]
                self.assertEqual(game.step(), "dead")


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "data" / "settings.json"

    def test_round_trip(self):
        store = Store(self.path)
        store.best["Hard"] = 120
        store.difficulty = "Hard"
        store.sound = False
        self.assertTrue(store.save())
        loaded = Store(self.path)
        self.assertEqual(loaded.best["Hard"], 120)
        self.assertEqual(loaded.difficulty, "Hard")
        self.assertFalse(loaded.sound)
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])

    def test_corrupt_and_invalid_data(self):
        self.path.parent.mkdir()
        for data in ["broken json", "null", "[]", json.dumps({"difficulty": "bad", "sound": "yes",
                          "best": {"Easy": -5, "Normal": True, "Hard": 999999}})]:
            with self.subTest(data=data):
                self.path.write_text(data)
                loaded = Store(self.path)
                self.assertEqual(loaded.difficulty, "Normal")
                self.assertTrue(loaded.sound)
                self.assertEqual(loaded.best, {"Easy": 0, "Normal": 0, "Hard": 0})

    def test_failed_save_is_nonfatal(self):
        blocker = Path(self.directory.name) / "file"
        blocker.write_text("block")
        store = Store(blocker / "settings.json")
        self.assertFalse(store.save())
        self.assertIsNotNone(store.error)


if __name__ == "__main__":
    unittest.main()
