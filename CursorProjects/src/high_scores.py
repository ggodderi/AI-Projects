from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

DEFAULT_PATH = Path("data/high_scores.json")
MAX_ENTRIES = 10


def load_high_scores(path: Path = DEFAULT_PATH) -> list[int]:
	if not path.exists():
		return []
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
		return list(map(int, data.get("scores", [])))[:MAX_ENTRIES]
	except Exception:
		return []


def save_high_scores(scores: List[int], path: Path = DEFAULT_PATH) -> None:
	sorted_scores = sorted((int(s) for s in scores), reverse=True)[:MAX_ENTRIES]
	payload = {"scores": sorted_scores}
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def submit_score(score: int, path: Path = DEFAULT_PATH) -> list[int]:
	scores = load_high_scores(path)
	scores.append(int(score))
	save_high_scores(scores, path)
	return load_high_scores(path)
