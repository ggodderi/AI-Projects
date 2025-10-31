# Space Invaders — Unit Test Plan

This plan maps unit-testable steps from the implementation guide to specific, automatable tests. It focuses on logic, rules, and determinism; rendering and complex I/O are covered by manual tests.

Conventions:
- Framework: `pytest`
- Pygame: use headless mode via `os.environ["SDL_VIDEODRIVER"] = "dummy"` in test setup
- Time: pass `dt` explicitly or mock clock where needed
- Collisions: prefer Pygame rect/mask operations; isolate logic behind methods that can be unit tested
- Filesystem: mock I/O for high scores and config

---

## Phase 1: Project Setup and Foundation

### Step 3: Basic Configuration (`config.py`)
- Tests:
  - Loads default screen size, colors, gameplay constants
  - Key bindings contain required actions (move_left, move_right, fire, pause)
- Methods: direct import and attribute assertions
- Pass Criteria: All constants present and valid types/ranges

---

## Phase 2: Core Loop and State Management

### Step 5: `GameStateManager`
- Tests:
  - Initial state is TITLE (or configured default)
  - Valid transitions: TITLE→PLAYING, PLAYING→PAUSED, PAUSED→PLAYING, PLAYING→GAME_OVER, WAVE_CLEARED→PLAYING
  - Invalid transitions are rejected or no-op with log (define behavior)
  - State-specific callbacks invoked (update/render routing stubs)
- Methods: instantiate, call `set_state(next_state)`, verify `current_state` and callbacks via spies/mocks
- Pass Criteria: Transitions follow allowed graph; callbacks fired exactly once

### Step 6–7: FPS Clamp and Loop Glue
- Tests:
  - Utility `clamp_dt(dt)` caps extremes (e.g., > 0.1 → 0.1)
- Methods: pure function test
- Pass Criteria: Values clamped within expected bounds

---

## Phase 3: Player

### Step 8: `Player` Movement and Bounds
- Tests:
  - Moving left/right changes `rect.x` appropriately with held input
  - Clamped to playfield bounds
  - Invulnerability timer counts down and toggles hit eligibility
- Methods: call `player.update(dt, inputs)`, assert `rect` and flags
- Pass Criteria: Movement, clamping, and timers behave deterministically

### Step 9–10: Bullet Constraints
- Tests:
  - `fire()` spawns a bullet if fewer than 5 active bullets exist
  - Can fire up to 5 bullets in succession
  - 6th `fire()` call ignored when 5 bullets already active
  - Each bullet moves upward independently by `speed * dt`
  - Bullets despawn when off-screen or after collision
- Methods: create `Player`, call `fire()` multiple times, tick updates, assert bullet lifecycle and limit
- Pass Criteria: Maximum 5 bullets constraint always enforced

---

## Phase 4: Invader Formation

### Step 12: `Invader` Properties
- Tests:
  - Points value per row/type is correct
  - Animation frame toggles on `tick_animation()` cadence
- Methods: instantiate with row/type; call toggle method; assert `frame_index`
- Pass Criteria: Values and toggling match config

### Step 13–14: `InvaderFormation` Movement and Descent
- Tests:
  - Formation translates horizontally each update with given direction
  - On boundary contact: `reverse_and_step_down()` called; direction flips; y increases by step size
  - Speed-up curve: fewer invaders → lower step interval/more movement per second
  - `get_front_line_invaders()` returns only lowest invader per non-empty column
  - `check_descend_limit()` detects threshold crossing
- Methods: inject mock screen bounds; set known invader grid; run `update(dt)`; assert position/direction; remove invaders and assert speed multiplier changes
- Pass Criteria: Movement rules and front-line logic match spec

---

## Phase 5: Collisions and Combat

### Step 16: Bullet vs. Invader Collision
- Tests:
  - First collision along bullet path removes the correct invader and despawns bullet
  - Score increases by invader’s point value
  - Formation grid updates (slot empty)
- Methods: place bullet and invader rects to intersect; call collision resolver; assert removals and score
- Pass Criteria: Single-hit resolution correct and idempotent

### Step 17–18: Bomb Logic
- Tests:
  - Active bomb cap enforced (based on remaining invaders/difficulty)
  - Bombs spawn only from front-line invaders
  - Bombs move downward; despawn off-screen
  - Bomb–player hit reduces lives and triggers respawn sequence flag
  - Bomb–bunker hit applies damage and despawns bomb
- Methods: control formation front line; tick spawn timers; simulate movement and collisions with stubs/mocks
- Pass Criteria: Spawn eligibility and caps always honored; collisions update state as specified

---

## Phase 6: Bunkers

### Step 20: Bunker Damage Model
- Tests:
  - `damage_at(point)` removes material in expected neighborhood/shape
  - `is_colliding(rect)` returns False in already-damaged regions, True in solid regions
  - Repeated hits expand damage
- Methods: create bunker with known mask; apply damage; query collisions
- Pass Criteria: Deterministic mask updates and collision queries

### Step 21: Projectile Interactions with Bunkers
- Tests:
  - Player bullet hitting intact bunker despawns and applies damage
  - Bomb hitting intact bunker despawns and applies damage
  - Projectiles traverse through fully damaged openings
- Methods: position rects to contact bunker; run resolver; assert outcomes
- Pass Criteria: Consistent behavior across projectile types

---

## Phase 7: Saucer

### Step 22–23: Saucer Spawn and Scoring
- Tests:
  - Spawn timer emits saucer only when none active
  - Saucer moves across screen and despawns off-screen
  - On bullet hit: saucer despawns and awards one of allowed point values
  - Optional: point selection rule tied to shot count modulo produces expected sequence
- Methods: mock timer; simulate movement; collide with test bullet; assert score and lifecycle
- Pass Criteria: Exactly one saucer active; scoring valid set

---

## Phase 8: Scoring, Lives, HUD

### Step 25: Scoring Rules
- Tests:
  - Invader scores: bottom/middle/top award 10/20/30
  - Saucer awards allowed values (50–300)
  - Bunker hits award 0
  - Extra life granted at threshold; max lives cap respected
- Methods: call scoring API with event types; assert totals and lives
- Pass Criteria: Totals match reference values; thresholds honored

### Step 26: HUD Data Formatting (Logic Only)
- Tests:
  - Score, high score, lives formatting strings correct
  - Life icon count matches lives (provide count via method without rendering)
- Methods: test pure formatting helpers
- Pass Criteria: Strings and counts match inputs

---

## Phase 9: Waves and Difficulty

### Step 28–29: Wave Progression and Scaling
- Tests:
  - Clearing all invaders triggers wave-cleared state and increments wave number
  - New wave resets formation to full grid
  ￼- Base speed and bomb rate increase with wave number per config
- Methods: remove all invaders; call wave transition; assert state and parameters
- Pass Criteria: Deterministic wave transitions and parameter scaling

---

## Phase 10: Audio

### Step 31: Audio Manager API (Mocked)
- Tests:
  - `play_sound(name)` looks up existing sounds; ignores/mocks missing
  - Volume set/mute toggles internal state
  - Step tempo calculation correlates with formation speed (logic unit)
- Methods: inject fake sound dict; call methods; assert flags and call counts
- Pass Criteria: No crashes on missing sounds; flags updated correctly

---

## Phase 11: Menus and States (Logic)

### Step 33–37: Menu Navigation Logic
- Tests:
  - Up/Down selection wraps or clamps per spec
  - Enter activates selected item, causing correct state transition
  - Pause toggles between PLAYING and PAUSED
- Methods: call menu controller with synthetic inputs; assert selection index and state
- Pass Criteria: Navigation deterministic; transitions correct

---

## Phase 12: Persistence and Settings

### Step 38–40: Config and High Scores (I/O Mocked)
- Tests:
  - Load config with defaults merged; invalid values clamped
  - Save config writes expected JSON structure
  - High scores: load top N, insert new score, persist sorted and truncated
- Methods: mock file reads/writes; validate payloads
- Pass Criteria: Correct merging, clamping, and ordering

---

## Phase 13: Visual Polish (Logic Hooks)

### Step 41–42: Effect Triggers
- Tests:
  - Hit events enqueue flash/shake effects with correct durations
  - Animation state machines advance frames over time
- Methods: call effect manager with events; tick timers; assert queues/indices
- Pass Criteria: Timers and frame indices match elapsed time

---

## Phase 14–16: Testing, Balance, Docs (Logic)

### Step 44–48: Balance Curves
- Tests:
  - Formation speed table/curve monotonic with fewer invaders and higher waves
  - Bomb spawn interval decreases monotonically with difficulty
- Methods: evaluate functions across ranges; assert monotonicity
- Pass Criteria: Functions satisfy invariants

---

## Test Files and Structure

- `tests/test_config.py`
- `tests/test_state_manager.py`
- `tests/test_player.py`
- `tests/test_bullet.py`
- `tests/test_invader.py`
- `tests/test_formation.py`
- `tests/test_collisions.py`
- `tests/test_bomb.py`
- `tests/test_bunker.py`
- `tests/test_saucer.py`
- `tests/test_scoring.py`
- `tests/test_hud_logic.py`
- `tests/test_waves.py`
- `tests/test_audio_manager.py`
- `tests/test_menus.py`
- `tests/test_persistence.py`
- `tests/test_effects.py`
- `tests/test_balance.py`

Each file should initialize Pygame in dummy mode in `conftest.py`:

```python
import os
import pygame
import pytest

@pytest.fixture(scope="session", autouse=True)
def init_pygame_headless():
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.display.init()
    pygame.font.init()
    yield
    pygame.quit()
```

---

## Pass/Fail Reporting

- Use descriptive test names (Given/When/Then style)
- Include property-based checks for curves (e.g., `hypothesis` optional)
- CI (optional): run `pytest -q` on push; artifact coverage report

---

## Out of Scope for Unit Tests (Manual/Integration)
- Sprite rendering fidelity and animations’ visual quality
- Audio playback quality and mixing on real hardware
- Full-screen/window management and DPI scaling
- Controller input devices

These are covered in manual test checklist within the implementation guide.
