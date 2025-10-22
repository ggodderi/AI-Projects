import json
from pathlib import Path
from typing import Any, Dict, List

from settings import HIGHSCORES_FILE, MAX_HIGHSCORES, SETTINGS_FILE


def _file_path(filename: str) -> Path:
    # Store in project directory by default
    return Path(__file__).resolve().parent.parent / filename


def load_json(filename: str, default: Any) -> Any:
    path = _file_path(filename)
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(filename: str, data: Any) -> None:
    path = _file_path(filename)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        # Best effort; ignore write failures in game loop
        pass


def load_settings() -> Dict[str, Any]:
    return load_json(SETTINGS_FILE, {})


def save_settings(settings: Dict[str, Any]) -> None:
    save_json(SETTINGS_FILE, settings)


def load_highscores() -> List[Dict[str, Any]]:
    data = load_json(HIGHSCORES_FILE, [])
    # Normalize
    if not isinstance(data, list):
        return []
    items: List[Dict[str, Any]] = []
    for it in data:
        if isinstance(it, dict) and "initials" in it and "score" in it:
            items.append({"initials": str(it["initials"])[:3].upper(), "score": int(it["score"])})
    items.sort(key=lambda d: d["score"], reverse=True)
    return items[:MAX_HIGHSCORES]


def submit_highscore(initials: str, score: int) -> List[Dict[str, Any]]:
    scores = load_highscores()
    scores.append({"initials": initials[:3].upper(), "score": int(score)})
    scores.sort(key=lambda d: d["score"], reverse=True)
    scores = scores[:MAX_HIGHSCORES]
    save_json(HIGHSCORES_FILE, scores)
    return scores
