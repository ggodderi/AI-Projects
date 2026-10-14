"""Validated preferences with atomic writes and graceful read-only fallback."""
import json
import os
from pathlib import Path
import tempfile

from snake_core import DIFFICULTIES


def default_path():
    override = os.environ.get("SNAKE_DATA_DIR")
    if override:
        return Path(override) / "settings.json"
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME")
    return (Path(base) if base else Path.home() / ".local" / "share") / "ClassicSnake" / "settings.json"


class Store:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else default_path()
        self.difficulty = "Normal"
        self.sound = True
        self.best = {name: 0 for name in DIFFICULTIES}
        self.error = None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return
            if data.get("difficulty") in DIFFICULTIES:
                self.difficulty = data["difficulty"]
            if isinstance(data.get("sound"), bool):
                self.sound = data["sound"]
            scores = data.get("best", {})
            if isinstance(scores, dict):
                for name in self.best:
                    value = scores.get(name, 0)
                    if type(value) is int and 0 <= value <= 6570:
                        self.best[name] = value
        except (OSError, ValueError, TypeError):
            pass

    def save(self):
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".snake-", suffix=".tmp", delete=False) as handle:
                temporary = handle.name
                json.dump({"version": 1, "difficulty": self.difficulty,
                           "sound": self.sound, "best": self.best}, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            self.error = None
            return True
        except OSError:
            self.error = "Scores and settings could not be saved."
            return False
        finally:
            if temporary:
                try:
                    Path(temporary).unlink(missing_ok=True)
                except OSError:
                    pass
