from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from config import SCREEN_WIDTH, SCREEN_HEIGHT, STARTING_LIVES, EXTRA_LIFE_SCORE, MAX_PLAYER_BULLETS

DEFAULT_CONFIG_PATH = Path("data/config.json")


def _clamp_int(value: int, min_v: int, max_v: int) -> int:
	return max(min_v, min(max_v, int(value)))


def load_settings(path: Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
	# Defaults
	settings: Dict[str, Any] = {
		"screen": {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT},
		"gameplay": {
			"starting_lives": STARTING_LIVES,
			"extra_life_score": EXTRA_LIFE_SCORE,
			"max_player_bullets": MAX_PLAYER_BULLETS,
		},
		"audio": {"volume": 0.7, "mute": False},
		"controls": {},
	}
	if not path.exists():
		return settings
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
		# Merge shallowly with clamps
		s = data.get("screen", {})
		w = _clamp_int(s.get("width", settings["screen"]["width"]), 320, 3840)
		h = _clamp_int(s.get("height", settings["screen"]["height"]), 240, 2160)
		settings["screen"] = {"width": w, "height": h}

		g = data.get("gameplay", {})
		settings["gameplay"] = {
			"starting_lives": _clamp_int(g.get("starting_lives", STARTING_LIVES), 1, 9),
			"extra_life_score": _clamp_int(g.get("extra_life_score", EXTRA_LIFE_SCORE), 100, 1000000),
			"max_player_bullets": _clamp_int(g.get("max_player_bullets", MAX_PLAYER_BULLETS), 1, 10),
		}

		a = data.get("audio", {})
		vol = a.get("volume", 0.7)
		try:
			vol = float(vol)
		except Exception:
			vol = 0.7
		vol = max(0.0, min(1.0, vol))
		settings["audio"] = {"volume": vol, "mute": bool(a.get("mute", False))}

		controls = data.get("controls", {})
		if isinstance(controls, dict):
			settings["controls"] = controls
		return settings
	except Exception:
		return settings
