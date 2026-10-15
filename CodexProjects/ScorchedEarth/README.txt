SCORCHED EARTH / PYTHON ARTILLERY EDITION 1.0

A complete two-tank artillery game inspired by the classic Scorched Earth.
This is an independent remake with original code, generated scenery, and
synthesized sound. It does not include the original game's code or assets.

PLAY ON THIS COMPUTER
Double-click Play.cmd. A Python 3.10 + Pygame environment is already prepared
in this folder. This game is independent of the earlier Snake project.

INSTALL ON ANOTHER WINDOWS COMPUTER
Extract the source ZIP to a writable folder. Install Python 3.10 or newer
with the Python launcher. Double-click Play.cmd. First launch creates .venv
and installs the pinned Pygame dependency; later launches work offline.

MANUAL INSTALL (WINDOWS / MACOS / LINUX)
From this folder:
  python -m venv .venv
  Activate it:
    Windows: .venv\Scripts\activate
    macOS/Linux: source .venv/bin/activate
  python -m pip install -r requirements.txt
  python scorched_earth.py

Python 3.10-3.13 uses pygame 2.6.1. Python 3.14+ uses pygame-ce 2.5.8,
which provides the pygame import. Use a Python release with a compatible
binary wheel. Windows with Python 3.10 is the verified release environment.

FEATURES
- Solo against three AI levels, or two-player hotseat on one keyboard/mouse.
- Three-, five-, or seven-round campaigns on new procedural terrain.
- Gravity, changing wind, swept projectile collision, and destructible ground.
- Blast damage, falling damage, shields, and friendly fire.
- Unlimited basic shells plus Heavy, Cluster, and Atomic ammunition.
- Credits earned from damage and round bonuses, with a between-round shop.
- Persistent preferences and solo career wins/matches.
- Mouse and keyboard controls, pause, focus-loss pause, resize, fullscreen.
- Generated sound and particle effects, both optional. No external assets.

CONTROLS
Left / Right or A / D   Rotate barrel (left increases the angle)
Up / Down or W / S     Increase / decrease launch power
Shift                  Fine aiming adjustments
Space / Enter          Fire once
Tab                    Cycle available weapons
1 / 2 / 3 / 4          Shell / Heavy / Cluster / Atomic
Mouse                  Click battlefield to aim; drag angle or power slider
Escape / P             Pause (Escape resumes from pause)
H / F1                 Field manual
M                      Toggle sound
F11                    Toggle fullscreen
Menus: Tab / Up / Down to select; Enter / Space to activate; or click.

RULES AND STRATEGY
Angles measure counterclockwise from the right: 45 degrees fires right,
135 degrees fires left. The wind accelerates shells horizontally and changes
each turn. The dotted sight shows only the beginning of the trajectory.
Shots above the screen continue flying; an indicator shows their status.
A shell crossing a side boundary is lost, even if the wind could bring it back.

Shell: unlimited, blast radius 38. Heavy: radius 65, greater damage.
Cluster: five bomblets split at the apex; impact before the apex still explodes.
Atomic: radius 115, very high damage. Any weapon can hurt its own tank.
Explosions remove ground. A fall over 22 pixels causes additional damage.
Shields absorb incoming blast and falling damage before health is reduced.

Each tank begins a round with 100 HP. Starting supplies: 3 Heavy, 2 Cluster,
no Atomic, 900 credits. Ammunition and credits carry between rounds. Bought
shields (40 each, up to 80) apply to the next round only. Health resets.

Damage to the enemy earns 4 credits per actual HP/shield point removed.
Both tanks earn 400 per completed round. The round winner gets another 700.
At turn 40, the highest remaining HP + shield wins; equal strength is a draw.
Simultaneous destruction also draws. Starting player alternates each round.
The match winner has the most round wins; enemy damage breaks a tie.
If both are equal, the campaign ends in a draw. A completed solo campaign
counts once in the saved career; hotseat games do not change solo records.

PROFILE AND SAVE BEHAVIOR
Preferences and completed solo career records are saved automatically.
Active campaigns are session-only; leaving or closing abandons that campaign.
The pause menu confirms before returning to the main menu.

Windows: %LOCALAPPDATA%\ScorchedEarthPython\profile.json
Other: $XDG_DATA_HOME/ScorchedEarthPython/profile.json, or
~/.local/share/ScorchedEarthPython/profile.json.
SCORCHED_DATA_DIR overrides the base directory for testing/portable profiles.
Atomic writes protect the profile from partial saves. Invalid data falls back
to defaults. If saving is unavailable, the game continues and shows a message.
Missing audio hardware falls back to silent play.

VERIFICATION
From this folder with the environment active:
  python -m unittest discover -s tests -v
  python scorched_earth.py --smoke-test ../../work/scorched-screens
For headless tests, set SDL_VIDEODRIVER=dummy and SDL_AUDIODRIVER=dummy.
Tests cover ballistics, collision, terrain, ammunition, shields, shops,
round/match outcomes, AI shots, a complete AI campaign, and profile recovery.
The smoke test drives real Pygame input/rendering through the campaign UI.

DEVELOPMENT
core.py             Rules, terrain, projectiles, AI search, campaign economy
scorched_earth.py   Pygame interface, rendering, input, synthesized sound
persistence.py     Validated preferences and atomic profile storage
tests/             Deterministic automated tests (standard-library unittest)
requirements.txt   Pinned runtime dependencies

The simulation uses fixed 120 Hz steps and constant acceleration. AI search
yields after each candidate angle so the event loop stays responsive.
Scenery caches are invalidated when terrain changes. Cosmetic randomness is
separate from the simulation random generator, keeping tests reproducible.

RELEASE SCOPE
A local desktop game, supplied as Python source with a Windows launcher.
No network multiplayer, original proprietary assets, signed installer, or
standalone executable. Other operating systems require the manual install
and have not been tested in this environment.
