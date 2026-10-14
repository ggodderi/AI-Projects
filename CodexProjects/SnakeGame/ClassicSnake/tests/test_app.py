import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snake_game import App, pygame
from storage import Store


class ScoreTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        environment.start()
        self.addCleanup(environment.stop)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "settings.json"
        self.app = App(Store(self.path))
        self.addCleanup(pygame.quit)
        self.app.start()
        self.app.game.food = (16, 11)
        self.app.update(.11)
        self.assertEqual(self.app.game.score, 10)

    def test_pause_menu_preserves_record_after_restart(self):
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
        self.app.perform("menu")
        self.app.start()
        self.assertEqual(self.app.game.score, 0)
        self.assertEqual(Store(self.path).best["Normal"], 10)

    def test_close_during_play_preserves_record(self):
        self.close_and_check_record()

    def test_close_while_paused_preserves_record(self):
        self.app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
        self.close_and_check_record()

    def close_and_check_record(self):
        with patch.object(pygame.event, "get", return_value=[pygame.event.Event(pygame.QUIT)]):
            self.app.run()
        self.assertFalse(self.app.running)
        self.assertEqual(Store(self.path).best["Normal"], 10)

    def test_leaving_lower_score_preserves_existing_record(self):
        self.app.store.best["Normal"] = 100
        self.app.perform("menu")
        self.assertEqual(Store(self.path).best["Normal"], 100)

    def test_menu_best_uses_selected_difficulty(self):
        self.app.perform("menu")
        self.app.perform("difficulty")
        self.assertEqual(self.app.store.difficulty, "Hard")
        with patch.object(self.app, "text", wraps=self.app.text) as text:
            self.app.render()
        displayed_best = [call.args[0] for call in text.call_args_list
                          if call.args[3] == (730, 60)]
        self.assertEqual(displayed_best, ["0000"])
        loaded = Store(self.path)
        self.assertEqual(loaded.best["Normal"], 10)
        self.assertEqual(loaded.best["Hard"], 0)

    def test_game_over_still_announces_new_record(self):
        self.app.game.snake = [(29, 11), (28, 11), (27, 11)]
        self.app.update(.11)
        self.assertEqual(self.app.state, "over")
        self.assertTrue(self.app.new_best)
        self.assertEqual(Store(self.path).best["Normal"], 10)


if __name__ == "__main__":
    unittest.main()
