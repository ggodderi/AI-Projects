# Space Invaders (Pygame) — Design and Requirements

## 1) Project Overview
This project recreates the classic Space Invaders arcade gameplay using Python and Pygame, emphasizing faithful mechanics with modern code quality. The scope includes a complete, polished single-player experience with configurable difficulty, sound, and robust input handling.

## 2) Core Game Loop and States
- Game States: Splash/Title, Playing, Paused, WaveCleared/Between-Waves, GameOver, HighScores (optional), Settings (optional).
- Loop Phases per frame: Handle Input → Update Simulation → Resolve Collisions/Scoring → Render → Play/Queue Sounds.
- Frame Rate Target: 60 FPS. Logic step uses a fixed timestep or clamped delta for stable movement.

## 3) Screen, Layout, and Coordinates
- Resolution: 800×600 (configurable). Logical playfield margins: 32 px left/right, 64 px bottom safety zone, 24 px top margin.
- Coordinate System: Origin at top-left; +x right, +y down.
- Playfield Regions:
  - Top UI band: score, high score, lives.
  - Middle play area: invader formation, saucer path, bunkers.
  - Bottom area: player cannon movement track and death animation space.

## 4) Player Cannon
- Movement: Left/Right only along bottom of the screen; clamped to playfield bounds.
- Speed: Configurable; baseline tuned for responsive play at 60 FPS.
- Firing: Up to 5 bullets on screen at a time. Subsequent shots are ignored until the number of active bullets drops below the limit.
- Lives: Start with 3 (configurable). Lose one on hit by invader bomb or invader collision with player row.
- Respawn: Brief invulnerability window after death (e.g., 1.0–1.5 s), no firing during death animation.
- Controls: Left/Right arrows or A/D; Space to fire; P to pause; Esc to quit to menu.

## 5) Player Bullet
- Count: Max 5 active bullets.
- Travel: Upwards at fixed speed; despawns on leaving screen or hitting invader, shield, or saucer.
- Collision Priority: Each bullet independently checks collisions; first object encountered along its path is hit; bullet then despawns.

## 6) Invaders (Formation and Movement)
- Formation: 5 columns × 11 rows (55 total) typical; rows differ by sprite and score value. Configurable rows/cols.
- Movement Pattern: Whole formation marches horizontally; when any invader hits a side bound, formation steps down and reverses direction.
- Speed-Up Mechanic: Horizontal movement speed and step cadence increase as invaders are destroyed (fewer invaders = faster formation).
- Descend Limit/End Condition: If any invader reaches the player row (or passes a descent threshold), the player loses a life (or game over if no lives remain).
- Animation: Invaders animate between 2 frames at a fixed cadence that also speeds up with game pace.

## 7) Invader Bombs (Enemy Projectiles)
- Bomb Types: Straight down shots (baseline). Optional variants (zig-zag/slow drips) can be added later.
- Firing Logic: A limited number of bombs can be active concurrently (e.g., 1–4 scaling with remaining invaders and difficulty).
- Spawn Columns: Bombs may only spawn from invaders that have no other invaders below them in the same column (front-line rule).
- Collision: Bombs destroy player on hit, chip bunkers, and despawn on leaving the screen.

## 8) Bunkers (Shields)
- Count: Typically 4 bunkers above the player track (configurable 3–4), evenly spaced.
- Structure: Each bunker is destructible by discrete cells/tiles or mask-based damage; hits remove small chunks.
- Damage Sources: Player bullet, invader bombs, and invaders themselves (if reached) can chip bunkers.
- Rendering: Use sprites or generated surfaces with mask operations to visually reveal chipping.

## 9) Saucer (Mystery Ship)
- Spawns: Periodically at the top, travels horizontally left-to-right or right-to-left across the screen.
- Timing: Random or interval-based (e.g., every 15–25 s, with some randomness).
- Scoring: Award variable points on hit (legacy: values in 50–300 range in steps of 50; can be random or based on player shot count modulo rule).

## 10) Scoring and Extra Lives
- Invader Row Values (classic-inspired):
  - Top row: 30 points
  - Middle rows: 20 points
  - Bottom rows: 10 points
- Saucer: 50–300 variable points.
- Bunker hits by player grant no points.
- Extra Life: Earn at a score threshold (e.g., 1500 or configurable). Maximum lives limit may apply (e.g., 6).
- HUD: Display Score, High Score, Lives.

## 11) Waves and Difficulty Progression
- Wave Completion: When all invaders are destroyed, start next wave.
- Next Wave: Reset full formation, slightly increase base speed and bomb rate; maintain player score/lives.
- Difficulty Scaling: Parameters that increase per wave: formation speed, descent cadence, bomb count, saucer frequency (optional).

## 12) Game Over Conditions
- Player loses all lives.
- Invaders reach the player row/threshold.
- Game over screen shows final score; option to restart or return to title.

## 13) Input and Controls
- Keyboard:
  - Left/Right arrows or A/D: Move.
  - Space: Fire.
  - P: Pause/Unpause.
  - Esc: Back/Quit to menu.
- Controller (optional): Map D-pad/left stick to movement, A/B to fire, Start to pause.
-
Input should be debounced via Pygame event queue with continuous movement on key hold.

## 14) Visuals and Rendering
- Style: Pixel-art or simple vector placeholders initially; support for replacing with sprite assets.
- Layers: Background → Bunkers → Invader bombs → Player and invaders → HUD.
- Flash/Effects: Brief hit flash on invaders; explosion sprites for deaths; saucer hit effect.
- Screen Shake (optional, subtle) on player death.

## 15) Audio
- Sounds: Player shot, invader shot, invader step loop (tempo increases as formation speeds up), invader hit, player death, saucer flyby, saucer hit, bunker chip.
- Mixer: Preload short WAV/OGG files. Limit overlapping to avoid distortion.
- Volume: Global volume setting; mute toggle.

## 16) Collision and Physics
- Bounding Box or Mask collisions:
  - Player bullet vs. invaders, saucer, bunkers.
  - Invader bombs vs. player, bunkers.
  - Invaders vs. bunkers (chip) and descent threshold (loss condition).
- Collision Resolution Order (per frame):
  1) Player bullet interactions.
  2) Invader bomb interactions.
  3) Invader formation descent/bounds check → state transitions.

## 17) Data Structures and Entities
- Entity Components (classes):
  - GameStateManager
  - PlayerCannon
  - Bullet (player)
  - Invader (with row/type metadata)
  - InvaderFormation (manages grid, direction, step timing, speed-up curve)
  - Bomb (invader projectile)
  - Bunker (grid/mask for damage)
  - Saucer
  - HUD (score, lives, high score)
  - AudioManager
- Use Pygame `sprite.Group` for batching updates/renders where useful; keep formation logic centralized to avoid per-invader drift.

## 18) Timing, Pace, and Speed Curves
- Base formation step interval (e.g., 0.6 s) decreases as remaining invaders drop; map remaining count to step interval via a curve/table.
- Invader bomb spawn interval inversely scales with invader count and wave number.
- Player move speed constant tuned for crossing screen in ~2–3 s.

## 19) Configuration and Difficulty Settings
- Config file (e.g., `config.yaml` or Python dict) with:
  - Screen: width, height, fullscreen flag.
  - Gameplay: starting lives, extra life threshold, wave speed increment, max bombs, saucer interval.
  - Controls: key bindings.
  - Audio: volume, mute.
  - Accessibility: colorblind-friendly palette, reduced flashes.

## 20) Persistence
- High Scores: Save top N (e.g., 10) to a local file (JSON). Load at startup; update on game over.
- Settings: Save user settings (volume, keys, difficulty) to a file.

## 21) Menus and HUD
- Title Screen: Start Game, High Scores, Settings, Quit.
- Pause Overlay: Resume, Restart Wave (optional), Quit to Title.
- HUD: Left-justified Score, centered High Score, right-justified Lives icons.

## 22) Assets and Technical Specs
- Sprites (initial placeholders permitted):
  - Player cannon: ~16×16 or 24×16.
  - Invaders: 2-frame animations per type (crab/octopus/squid analogs), ~16×12 each.
  - Saucer: ~24×12.
  - Bombs/Bullets: 2–4×8 px.
  - Explosions: 4–6 frames at ~12–16 px.
- Audio: Short WAV/OGG files; ensure levels normalized.
- Fonts: Pixel font for HUD or Pygame default for prototype.

## 23) Performance Targets
- 60 FPS steady on modest hardware.
- Avoid per-frame allocations; reuse surfaces where possible.
- Batch drawing with sprite groups; limit alpha blending and expensive per-pixel ops.

## 24) Testing Strategy
- Unit tests for:
  - Formation movement and boundary descent logic.
  - Bullet limit constraint (max 5 active).
  - Bomb spawn eligibility (front-line rule).
  - Bunker damage application.
  - Scoring per invader row and saucer variability.
- Manual test checklist:
  - Movement clamping, firing rate constraint, pause/resume.
  - Speed-up feels correct as invaders are eliminated.
  - Game over when invaders reach threshold.
  - Extra life award timing.

## 25) Error Handling and Resilience
- Fail gracefully if assets missing: show placeholders, log warnings.
- Clamp impossible values in config and log corrections.
- Handle window focus lost by auto-pausing (optional).

## 26) Accessibility and UX
- Options: Reduced flashing, master volume, rebinding keys.
- Clear visual feedback: hit flashes, death animations, pause overlay.
- Consistent color contrast; sufficient size for sprites and HUD.

## 27) Non-Goals (Initial Version)
- Online multiplayer or netplay.
- Complex particle systems.
- Mobile touch controls.
- AI companions or power-ups beyond the classic design.

## 28) Milestones
1) Prototype core loop: player move + fire, invader formation marches, collisions, scoring.
2) Add bombs, bunkers with destructible masks, saucer.
3) Implement waves, speed curve, audio loop, and SFX.
4) Menus, HUD polish, high scores, settings.
5) Balance pass and test suite.

## 29) Implementation Notes (Pygame)
- Use `pygame.time.Clock().tick(60)` and a clamped `dt` for stability.
- Prefer integer pixel positions for crisp sprite movement; accumulate sub-pixel in floats if needed.
- Keep formation authoritative state in `InvaderFormation`; invaders query it for step timing and direction.
- Use `pygame.mask` or per-tile damage for bunkers.

## 30) Glossary
- Formation: The group of invaders that move as one unit left/right and descend.
- Front-line invader: Lowest invader in a given column eligible to fire bombs.
- Bomb: Enemy projectile.


