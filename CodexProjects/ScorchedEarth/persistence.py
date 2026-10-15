"""Versioned, validated preferences and local career records."""
import json
import os
from pathlib import Path
import tempfile


class Store:
    def __init__(self, path=None):
        base = Path(os.environ.get("SCORCHED_DATA_DIR") or
                    os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or
                    str(Path.home() / ".local" / "share"))
        self.path = Path(path) if path else base / "ScorchedEarthPython" / "profile.json"
        self.mode, self.skill, self.rounds = "Solo", "Veteran", 3
        self.sound, self.effects = True, True
        self.matches, self.wins = 0, 0
        self.error = None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return
            for key, options in [("mode", ("Solo", "Hotseat")), ("skill", ("Cadet", "Veteran", "Expert")),
                                 ("rounds", (3, 5, 7))]:
                value = data.get(key)
                if value in options and (key != "rounds" or type(value) is int):
                    setattr(self, key, value)
            for key in ("sound", "effects"):
                if type(data.get(key)) is bool:
                    setattr(self, key, data[key])
            for key in ("matches", "wins"):
                if type(data.get(key)) is int and 0 <= data[key] <= 10_000_000:
                    setattr(self, key, data[key])
            self.wins = min(self.wins, self.matches)
        except (OSError, ValueError, TypeError):
            pass

    def save(self):
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".profile-", suffix=".tmp", delete=False) as handle:
                temporary = handle.name
                json.dump({"version": 1, **{k: getattr(self, k) for k in
                          ("mode", "skill", "rounds", "sound", "effects", "matches", "wins")}}, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            self.error = None
            return True
        except OSError:
            self.error = "Profile could not be saved; this session will still work."
            return False
        finally:
            if temporary:
                try:
                    Path(temporary).unlink(missing_ok=True)
                except OSError:
                    pass
