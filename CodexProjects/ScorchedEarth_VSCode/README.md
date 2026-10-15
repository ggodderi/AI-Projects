# Scorched Earth

A polished, asset-free Python/Pygame artillery duel inspired by the classic
Scorched Earth. Two tanks trade shots across deformable procedural terrain.

## Run

```powershell
py -m pip install -r requirements.txt
py scorched_earth.py
```

## Controls

- Left / Right: adjust barrel angle
- Up / Down: adjust shot power
- Space: fire
- R: restart after a match
- Escape: quit

The player controls the left tank. The CPU takes its turn automatically after
each impact. Wind is shown in the top-right and changes after every shot.

## Test

```powershell
py -m unittest discover -s tests -v
```

