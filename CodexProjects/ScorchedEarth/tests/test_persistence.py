import json
from pathlib import Path
import tempfile
import unittest

from persistence import Store


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "data" / "profile.json"

    def test_round_trip(self):
        store = Store(self.path)
        store.mode, store.skill, store.rounds = "Hotseat", "Expert", 7
        store.sound, store.effects = False, False
        store.matches, store.wins = 5, 3
        self.assertTrue(store.save())
        loaded = Store(self.path)
        for field in ("mode", "skill", "rounds", "sound", "effects", "matches", "wins"):
            self.assertEqual(getattr(loaded, field), getattr(store, field))
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])

    def test_missing_corrupt_and_invalid_profiles(self):
        self.assertEqual(Store(self.path).matches, 0)
        self.path.parent.mkdir()
        values = ["null", "[]", "not JSON", json.dumps({"mode": [], "rounds": {}, "skill": 99,
                    "sound": "yes", "effects": 1, "matches": True, "wins": -12})]
        for value in values:
            with self.subTest(value=value):
                self.path.write_text(value)
                loaded = Store(self.path)
                self.assertEqual(loaded.mode, "Solo")
                self.assertEqual(loaded.skill, "Veteran")
                self.assertEqual(loaded.rounds, 3)
                self.assertTrue(loaded.sound)
                self.assertTrue(loaded.effects)
                self.assertEqual(loaded.matches, 0)
                self.assertEqual(loaded.wins, 0)

    def test_career_is_consistent(self):
        self.path.parent.mkdir()
        self.path.write_text(json.dumps({"matches": 4, "wins": 12}))
        self.assertEqual(Store(self.path).wins, 4)

    def test_fractional_round_setting_cannot_break_interface(self):
        self.path.parent.mkdir()
        self.path.write_text(json.dumps({"rounds": 5.0}))
        loaded = Store(self.path)
        self.assertIs(type(loaded.rounds), int)
        self.assertEqual(loaded.rounds, 3)

    def test_read_only_location_does_not_crash(self):
        blocker = Path(self.directory.name) / "not-a-folder"
        blocker.write_text("blocked")
        store = Store(blocker / "profile.json")
        self.assertFalse(store.save())
        self.assertIsNotNone(store.error)


if __name__ == "__main__":
    unittest.main()
