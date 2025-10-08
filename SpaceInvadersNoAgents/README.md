# Space Invaders (Python / pygame)

This repository contains a Space-Invaders-like game implemented in Python using pygame. It was built to follow the design in `space_invaders_design.md`.

Requirements satisfied:
- Python + pygame
- Pixel-style invader and player sprites generated procedurally
- Sound for shots and hits (generated at runtime)
- Bullets stop on hit; up to 5 bullets in air; 170 bullets per level
- Score, HUD with bullets remaining, level; game over and replay prompt
- Levels increase invader speed and count up to 12; invaders speed up as count decreases
- A small background thread and a sound worker thread are used to keep sound playback off the main loop

Run locally:

1. Create a Python virtual environment (recommended) and install requirements:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Run the game:

```powershell
python space_invaders.py
```

Controls:
- Left / A: move left
- Right / D: move right
- Space: shoot (limited by in-air and per-level bullets)
- Y/N when prompted to replay

Notes and limitations:
- This is a focused implementation meant to match the provided design quickly. Graphics are simple pixel art drawn at runtime.
- Sound files are generated as small WAV files at first run and played via pygame.mixer in a background thread.
- The game has not been extensively profiled across platforms but uses a decoupled sound thread and light-weight drawing.

If you'd like a web build or packaged executable, I can add build scripts or export instructions next.
