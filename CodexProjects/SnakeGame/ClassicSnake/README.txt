CLASSIC SNAKE / 1.0.0

A complete offline desktop game built with Python and Pygame.
No downloaded art, music, services, accounts, or runtime network access.

QUICK START (WINDOWS)
Double-click Play.cmd. Python 3.10 or newer must be installed.
The first launch creates a local .venv and downloads the pinned Pygame dependency.
Subsequent launches work offline. Keep all files in this folder together.

MANUAL START (WINDOWS / MACOS / LINUX)
From this folder:
  python -m venv .venv
  Activate the environment:
    Windows: .venv\Scripts\activate
    macOS/Linux: source .venv/bin/activate
  python -m pip install -r requirements.txt
  python snake_game.py

Python 3.10-3.13 uses standard pygame 2.6.1. Python 3.14+ uses the
pygame-ce 2.5.8 distribution, which provides the same pygame import.
Use a supported Python release with an available binary dependency wheel.

HOW TO PLAY
Eat the coral food to grow and earn 10 points. Hitting a wall or your body ends
the round. Filling all 660 cells wins. You may enter a tail cell when the tail
is moving away. A reversal into your neck is ignored. Two quick turns may be
queued; key repeats cannot reverse the snake.

CONTROLS
Arrows / WASD       Move
Space / P / Escape Pause; same keys resume
Enter              Activate selected menu button
Up / Down / Tab    Select menu button
Left / Right       Change difficulty in main menu
Space              Start or play again
R                  Play again on game-over screen
M                  Toggle sound
F11                Toggle fullscreen
Escape             Return from game-over to menu; quit from main menu
Mouse              Select and click menu buttons

Easy starts at 7 moves/second, Normal at 10, Hard at 14. Speed increases by
1 every 50 points up to 22. High scores are kept separately by difficulty.
The game pauses when it loses focus. Resize the window freely; the board
maintains its shape. Audio hardware is optional; missing audio runs silently.

SAVED DATA
Windows: %LOCALAPPDATA%\ClassicSnake\settings.json
Other systems: $XDG_DATA_HOME/ClassicSnake/settings.json, or
~/.local/share/ClassicSnake/settings.json.
Set SNAKE_DATA_DIR to override the location. Writes are atomic. Corrupt data
falls back to defaults; a save failure is displayed without stopping play.

VERIFICATION
  python -m unittest discover -s tests -v
  python snake_game.py --smoke-test ../../work/screenshots
For unattended checks set SDL_VIDEODRIVER=dummy and SDL_AUDIODRIVER=dummy.
The smoke check renders screens and exercises actual Pygame input and states.

FILES
snake_game.py  Desktop interface, animation loop, audio, and input
snake_core.py  Pure game rules and food placement
storage.py     Preferences and high scores
tests/         Rules, persistence, and edge-case tests

Release scope: local single-player desktop game. No installer or code signing.
