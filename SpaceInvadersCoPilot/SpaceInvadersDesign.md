# Space Invaders (Pygame) — Product & Technical Requirements

## Overview
A modern-yet-faithful Space Invaders clone built with Python and Pygame. The player controls a cannon at the bottom of the screen, shooting descending waves of aliens while protecting themselves with shields. The game features multiple waves, scoring, high score persistence, responsive controls, simple animations, and classic sound effects.

Assumptions:
- Platform: Windows first (works cross‑platform where Pygame is supported).
- Python 3.10+ and Pygame 2.5+.
- Fixed timestep targeting 60 FPS.

## Goals
- Faithful core gameplay loop: player, alien formation, shields, UFO, scoring, and wave progression.
- Smooth controls and consistent difficulty curve.
- Minimal, clean code architecture that’s easy to extend.
- Local high score persistence.

## Non‑Goals
- Online multiplayer or net play.
- Advanced graphics (3D, shaders) or complex physics.
- Complex asset pipeline or external level editors.

## Dependencies
- Python 3.10 or later
- Pygame 2.5 or later

Optional (dev):
- pytest for unit tests
- mypy/ruff or flake8/black for linting/formatting

## Display & Performance Targets
- Window size: 800×600 (configurable via settings).
- Target frame rate: 60 FPS.
- Input latency under ~50ms; no dropped frames on modest hardware.

## Game Flow & States
- Boot → Main Menu → Gameplay → (Pause) → Game Over → High Scores → Main Menu.
- State manager handles transitions; each state owns its event/update/draw routines.

States:
- Main Menu: Start Game, View High Scores, Quit.
- Gameplay: Core loop.
- Pause: Overlay with Resume/Quit.
- Game Over: Shows score; allow initials entry if high score achieved.
- High Scores: Top N scores list.

## Controls (Keyboard)
- Left/Right arrows or A/D: Move.
- Space: Fire.
- Enter/Escape: Confirm/Back in menus.
- P or Esc: Pause/Resume during gameplay.

Accessibility options (nice-to-have):
- Remappable keys (v1 optional).
- Volume controls.

## Entities & Systems

### Player Cannon
- Position: Bottom of screen; constrained to horizontal bounds.
- Speed: Configurable pixels/sec.
- Lives: 3 (configurable). Lose one on collision with alien or alien projectile; game over on 0.
- Shooting: One player bullet on-screen at a time (classic); cooldown configurable.

### Alien Formation
- Grid: 5–6 rows, 11 columns (configurable). Row types (top to bottom) affect sprite & score value.
- Movement: Horizontal marching; on hitting screen edge, drop down and reverse direction; speed increases as aliens are eliminated.
- Firing: Random alien(s) fire at intervals; rate scales with remaining aliens.
- Win condition: Wave cleared when all aliens destroyed → next wave spawns with increased difficulty.
- Lose condition: Any alien reaches shield line or bottom boundary, or the player loses all lives.

### Shields (Bunkers)
- 3–4 bunkers positioned above the player.
- Destructible: Each bullet collision removes small chunks.
- Implementation options:
  - Pixel mask eroded on impact, or
  - Grid of blocks; destroy impacted cells.

### UFO (Mystery Ship)
- Spawns periodically at top; moves horizontally; despawns when off-screen or if hit.
- Score: Random among set values (e.g., 50/100/150/300) or pattern-based.

### Projectiles
- Player bullets: Travel upward; one on-screen at a time.
- Alien bullets: Travel downward; limited concurrent count; simple straight movement.
- Collisions: With aliens, player, shields, and UFO; resolve on first hit.

### Effects
- Simple explosion animation/sprite swap and/or particle flickers on hit.
- Minimal screen shake (optional, off by default to stay faithful).

## Collision Rules
- Rect or mask-based checks using Pygame rects/masks.
- Priority: Projectile hits resolve and remove projectile + apply damage.
- Player hit by alien bullet: lose life, brief invulnerability window on respawn.
- Alien reaches bottom boundary: immediate game over.

## Scoring
- Alien rows have distinct values (e.g., bottom row: 10, middle: 20, top: 30).
- UFO awards variable points.
- Display: HUD shows score, high score, and lives.
- Extra life threshold (optional): e.g., every 10,000 points.

## Difficulty & Progression
- Each wave increases:
  - Alien horizontal speed and/or drop distance.
  - Alien fire rate.
  - Reduced player shot cooldown (optional).
- Cap difficulty to keep playable.

## UI/UX Requirements
- Main Menu: Title, options list, simple keyboard navigation.
- HUD: Score (left), High Score (center), Lives (right icons).
- Pause overlay: Dim screen, display menu.
- Game Over: Final score, optional initials input for high score.
- High Scores screen: Top 10 entries; stored locally.
- Visual style: Clean pixel-art or simple geometric shapes if no assets.

## Audio
- SFX: Player shot, alien shot, alien hit, player hit, shield hit, UFO spawn/hit, step/march loop.
- Music: Optional low-volume background loop; classic marching tones preferred.
- Volume: Master and SFX sliders; saved to settings file.

## Persistence
- Config file (JSON): window size, volume, controls, difficulty tweaks.
- High scores file (JSON): list of {initials, score, date}; keep top 10.
- Files stored locally next to game or in user’s home/AppData.

## Error Handling & Edge Cases
- Graceful handling if assets missing: fall back to simple shapes/beeps.
- Window resize disabled in v1 (fixed size); if enabled later, layout scales or letterboxes.
- Prevent player from firing when a bullet is already active (classic rule).
- Clamp spawn positions within screen; handle zero aliens without crashes.

## Technical Architecture

### Module Layout (proposed)
- `main.py`: Entry point, game loop bootstrap.
- `settings.py`: Constants, tunables, and configurable options.
- `assets.py`: Asset loading utilities; fallbacks if files missing.
- `scenes/`
  - `menu.py`, `gameplay.py`, `pause.py`, `game_over.py`, `high_scores.py`.
- `entities/`
  - `player.py`, `alien.py`, `formation.py`, `projectile.py`, `shield.py`, `ufo.py`, `effects.py`.
- `systems/`
  - `collision.py`, `score.py`, `persistence.py`, `audio.py`.
- `assets/` (optional): images/, sounds/, fonts/.
- `tests/` (optional): unit tests for pure logic.

### Game Loop Contract
- Inputs: Pygame events; time delta from clock.
- Update order: handle input → update entities/systems → resolve collisions → remove dead → spawn new → compose draw list.
- Draw order: background → shields → aliens → player → projectiles → HUD/overlays.
- Timing: Fixed tick at 60 FPS using `Clock.tick(60)`; entity speeds in pixels/tick.

### Data Structures
- Formation: 2D list or list of rows of aliens; track direction, edge bounds, step timer, drop amount.
- Shields: 2D mask/grid; erode cells on impact; render by iterating alive cells or blitting pre-eroded surfaces.
- Projectiles: Bounded list with active flag; reuse objects to avoid GC churn (optional).
- High scores: List of dicts sorted by score desc; capped at 10.

### Collision Implementation
- Use `pygame.Rect` intersects for coarse; optional `pygame.mask` for pixel-precise on shields.
- Maintain spatial buckets by rows (aliens) to limit checks.

## Assets & Licensing
- Prefer self-created minimal assets or CC0/public domain.
- Document source and license in `assets/README.md` if third-party used.

## Testing & QA
- Unit tests (where practical):
  - Formation movement logic at edges and drops.
  - Shield erosion function (pure logic if grid-based).
  - Scoring and high score insertion/sorting.
  - Cooldowns and single-bullet rule.
- Manual test checklist:
  - Controls responsive; no stutter at 60 FPS.
  - Aliens reverse/drop at edges; speed scales with count.
  - Collisions behave predictably; no phantom hits.
  - High score persists across runs; menu navigation stable.

## Telemetry (optional)
- Simple logging for errors and key events (wave start/end, game over).

## Configuration & Build
- Run locally via `python main.py` after installing dependencies.
- Settings in `settings.py` with optional `settings.json` override.

## Acceptance Criteria
- Start → Play → Game Over loop is fully functional without crashes.
- Player can move and fire; limited to one on-screen player bullet.
- Aliens march, reverse on edges, drop down, speed up as their count decreases.
- Aliens fire; player can be hit and lose lives; game ends at 0 lives or if aliens reach bottom.
- Shields erode when hit by any projectile.
- UFO occasionally appears and awards points when destroyed.
- HUD shows score, high score, lives; high score persists across runs.
- Pause/resume works; menus are navigable by keyboard.
- Runs at ~60 FPS on modest hardware at 800×600.

## Stretch Goals (Nice-to-Have)
- Power-ups (temporary double shot, speed boost).
- Multiple visual themes; CRT scanline effect toggle.
- Gamepad support.
- Adjustable difficulty modes.
- Rebindable keys UI.
- Window scaling and fullscreen toggle.

## Risks & Mitigations
- Performance with many collisions → use row-based checks, limit projectile count.
- Asset availability → ship with simple shapes and synthesized sounds fallback.
- Input inconsistency on varying FPS → fixed timestep; movement based on ticks.

---
This document defines the minimal faithful clone with clear boundaries and room to extend. Implementation can proceed by scaffolding modules, then building gameplay state, entities, and systems iteratively while validating each acceptance criterion.
