# Space Invaders Implementation Guide
## Step-by-Step Development Instructions

This document provides a sequential, step-by-step guide to implementing the Space Invaders game based on the design requirements.

---

## Phase 1: Project Setup and Foundation

### Step 1: Initialize Project Structure
1. Create the following directory structure:
   ```
   space-invaders/
   ├── main.py                 # Entry point
   ├── config.py              # Configuration constants
   ├── requirements.txt       # Python dependencies
   ├── README.md              # Project documentation
   ├── src/
   │   ├── __init__.py
   │   ├── game.py            # Main game class
   │   ├── game_state.py      # Game state manager
   │   ├── player.py          # Player cannon
   │   ├── bullet.py          # Player bullet
   │   ├── invader.py         # Individual invader
   │   ├── formation.py       # Invader formation manager
   │   ├── bomb.py            # Invader bomb
   │   ├── bunker.py          # Shield/bunker
   │   ├── saucer.py          # Mystery ship
   │   ├── hud.py             # Heads-up display
   │   ├── audio_manager.py   # Sound effects manager
   │   └── utils.py           # Helper functions
   ├── assets/
   │   ├── sprites/
   │   ├── sounds/
   │   └── fonts/
   ├── data/
   │   ├── config.json        # Game settings
   │   └── high_scores.json   # High score storage
   └── tests/
       └── test_invader_formation.py
   ```

### Step 2: Set Up Python Environment
1. Create `requirements.txt`:
   ```
   pygame>=2.5.0
   ```
2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

### Step 3: Create Basic Configuration
1. Create `config.py` with:
   - Screen dimensions (800x600 default)
   - Colors (RGB tuples)
   - Gameplay constants (lives, speeds, intervals)
   - Key bindings dictionary

### Step 4: Create Main Entry Point
1. Create `main.py`:
   - Initialize Pygame
   - Create game window
   - Set up main game loop skeleton
   - Handle window close events
   - Test that window opens and closes properly

---

## Phase 2: Core Game Loop and State Management

### Step 5: Implement Game State Manager
1. Create `src/game_state.py`:
   - Define enum or constants for game states: TITLE, PLAYING, PAUSED, GAME_OVER, WAVE_CLEARED
   - Implement `GameStateManager` class with:
     - Current state property
     - State transition methods
     - State-specific update/render routing

### Step 6: Create Main Game Class
1. Create `src/game.py`:
   - Initialize Pygame modules (display, mixer, font)
   - Set up clock for FPS control
   - Create state manager instance
   - Implement main loop:
     - Handle events
     - Update current state
     - Render current state
     - Tick clock at 60 FPS

### Step 7: Test Game Loop
1. Add placeholder rendering for each state
2. Implement state transitions (e.g., press Enter to start)
3. Verify FPS is locked at 60
4. Test pause functionality

---

## Phase 3: Player Implementation

### Step 8: Implement Player Cannon
1. Create `src/player.py`:
   - `Player` class inheriting from `pygame.sprite.Sprite`
   - Position at bottom of screen (configurable Y)
   - Movement: left/right with bounds clamping
   - Input handling: continuous movement on key hold
   - Rendering: simple rectangle or sprite
   - Properties: x position, rect, lives, invulnerability timer

### Step 9: Implement Player Bullet
1. Create `src/bullet.py`:
   - `Bullet` class inheriting from `pygame.sprite.Sprite`
   - Spawns at player position
   - Moves upward at fixed speed
   - Despawns when leaving screen top
   - Rendering: small rectangle or sprite

### Step 10: Connect Player and Bullet
1. In `Player` class:
   - Add `fire()` method that creates bullet
   - Track active bullets (max 5)
   - Prevent firing if 5 bullets already active
   - Fire on Space key press
2. In game loop:
   - Update all active bullets
   - Render all active bullets
   - Remove bullets when despawned or after collisions

### Step 11: Test Player Controls
1. Test movement with arrow keys or A/D
2. Test bounds clamping (can't move off screen)
3. Test bullet limit constraint (can't fire more than 5 bullets at once)
4. Verify bullet travels upward and despawns correctly

---

## Phase 4: Invader Formation

### Step 12: Create Individual Invader
1. Create `src/invader.py`:
   - `Invader` class inheriting from `pygame.sprite.Sprite`
   - Properties: row, column, invader_type (top/middle/bottom)
   - Animation: 2-frame sprite animation
   - Points value based on row/type
   - Health (1 hit to destroy)
   - Rendering with sprite frames

### Step 13: Implement Invader Formation Manager
1. Create `src/formation.py`:
   - `InvaderFormation` class:
     - Grid structure: list of lists or dictionary mapping (row, col) to Invader
     - Formation position and movement direction
     - Step timing and interval
     - Speed-up curve: calculate step interval based on remaining invaders
   - Methods:
     - `update(dt)`: handle movement, check boundaries
     - `reverse_and_step_down()`: when hitting side wall
     - `get_front_line_invaders()`: invaders eligible to fire (lowest in each column)
     - `get_speed_multiplier()`: speed-up calculation
     - `check_descend_limit()`: check if invaders reached player row
   - Rendering: iterate through all invaders and render

### Step 14: Implement Formation Movement Logic
1. Horizontal movement:
   - Move all invaders together
   - Check if any invader hits left/right boundary
   - On boundary hit: step down by fixed amount, reverse direction
   - Clamp formation position to screen bounds
2. Animation:
   - Toggle sprite frame at fixed interval (sync with movement or separate timer)
   - Increase animation speed as formation speeds up

### Step 15: Test Formation Movement
1. Verify all invaders move together
2. Test boundary reversal and step down
3. Test speed-up as invaders are destroyed
4. Verify animation alternates correctly

---

## Phase 5: Collisions and Combat

### Step 16: Implement Collision Detection
1. In main game loop or collision manager:
   - Player bullets vs. Invaders (use `pygame.sprite.groupcollide` or iterate bullets)
   - When hit occurs:
     - Remove invader from formation
     - Despawn the hitting bullet (only one bullet per collision)
     - Award points (based on invader row/type)
     - Play hit sound effect
     - Update formation (remove from grid)
   - Check if formation is empty → trigger wave cleared state

### Step 17: Implement Invader Bombs
1. Create `src/bomb.py`:
   - `Bomb` class inheriting from `pygame.sprite.Sprite`
   - Moves downward at configurable speed
   - Despawns on leaving screen bottom or collision

2. In `InvaderFormation`:
   - Track active bombs (limit based on remaining invaders)
   - Spawn logic: periodically select random front-line invader to fire
   - Only spawn if bomb limit not reached and eligible invader exists
   - Increase spawn rate as invaders decrease and wave increases

3. In game loop:
   - Update all active bombs
   - Render all active bombs

### Step 18: Implement Bomb Collisions
1. Collision checks:
   - Bombs vs. Player (lose life, respawn with invulnerability)
   - Bombs vs. Bunkers (damage bunker, despawn bomb)
2. Handle player death:
   - Decrement lives
   - If lives > 0: respawn after delay with invulnerability
   - If lives == 0: trigger game over

### Step 19: Test Combat System
1. Test player bullet hits invader (scoring works)
2. Test invader bombs spawn from front-line only
3. Test bomb hits player (lose life)
4. Test game over when lives reach 0

---

## Phase 6: Bunkers/Shields

### Step 20: Implement Destructible Bunkers
1. Create `src/bunker.py`:
   - `Bunker` class:
     - Use `pygame.mask.Mask` or grid-based damage system
     - Track damaged regions (pixels or cells)
     - Initial undamaged sprite/surface
   - Methods:
     - `damage(rect)` or `damage_at(point)`: mark area as destroyed
     - `is_colliding(rect)`: check if collision hits undamaged area
     - `render()`: draw bunker with damage applied

2. Implement bunker collision:
   - Player bullets: damage bunker at collision point, despawn bullet
   - Invader bombs: damage bunker at collision point, despawn bomb
   - Use mask collision or pixel-perfect checks for chipping effect

3. Create 4 bunkers spaced evenly above player area

### Step 21: Test Bunkers
1. Test player bullet damages bunker (creates visible chip)
2. Test invader bomb damages bunker
3. Test bullets/bombs pass through damaged areas
4. Verify visual appearance is correct

---

## Phase 7: Saucer (Mystery Ship)

### Step 22: Implement Saucer
1. Create `src/saucer.py`:
   - `Saucer` class inheriting from `pygame.sprite.Sprite`
   - Spawns at random interval (or fixed with randomness)
   - Moves horizontally (left-to-right or right-to-left, random)
   - Award points when shot (variable: 50, 100, 150, 200, 250, 300)
   - Despawns when leaving screen or hit
   - Render unique sprite

2. In game loop:
   - Track saucer spawn timer
   - Spawn saucer when timer expires (only if no active saucer)
   - Update and render saucer if active

### Step 23: Implement Saucer Collision and Scoring
1. Player bullet vs. Saucer:
   - Award variable points (use random or formula based on shot count)
   - Play saucer hit sound
   - Despawn saucer and bullet
   - Show hit effect

### Step 24: Test Saucer
1. Test saucer spawns periodically
2. Test saucer moves across screen
3. Test shooting saucer awards points
4. Test saucer despawns correctly

---

## Phase 8: Scoring, Lives, and HUD

### Step 25: Implement Scoring System
1. Track current score (integer)
2. Award points based on:
   - Invader type/row: Top=30, Middle=20, Bottom=10
   - Saucer: Variable (50-300)
3. Track high score (load from file, save on game over)
4. Extra life threshold: award life at score milestones (e.g., 1500)

### Step 26: Implement HUD
1. Create `src/hud.py`:
   - `HUD` class:
     - Render score (left-aligned)
     - Render high score (center-aligned)
     - Render lives (right-aligned, show icons or number)
     - Update on score/lives changes
   - Use Pygame font rendering

2. Integrate HUD into game loop:
   - Render after all game objects
   - Ensure HUD is always visible

### Step 27: Test Scoring and HUD
1. Verify points awarded correctly per invader type
2. Test high score updates and persists
3. Test extra life awarded at threshold
4. Verify HUD displays correctly and updates in real-time

---

## Phase 9: Waves and Difficulty Scaling

### Step 28: Implement Wave System
1. Track current wave number
2. On wave cleared (all invaders destroyed):
   - Increment wave number
   - Reset formation (full grid of invaders)
   - Increase base speed slightly
   - Increase bomb spawn rate
   - Increase saucer spawn frequency (optional)
   - Brief "Wave Cleared" message/state

3. Wave cleared state:
   - Show message for 2-3 seconds
   - Transition back to playing state with new wave

### Step 29: Implement Difficulty Scaling
1. Speed multipliers:
   - Base step interval decreases per wave
   - Formation speed-up curve also considers wave number
2. Bomb spawn rate:
   - Scale with both remaining invaders and wave number
3. Test progression feels balanced

### Step 30: Test Wave System
1. Clear first wave → verify second wave starts
2. Verify speed increases in later waves
3. Verify formation reset is correct
4. Test multiple waves in succession

---

## Phase 10: Audio System

### Step 31: Implement Audio Manager
1. Create `src/audio_manager.py`:
   - `AudioManager` class:
     - Preload sound effects (WAV/OGG files)
     - Sound effects dictionary mapping names to sounds
     - Global volume control
     - Methods: `play_sound(name)`, `set_volume(volume)`, `mute()`
   - Sound effects needed:
     - Player shot
     - Invader shot/bomb
     - Invader step (loop, tempo increases)
     - Invader hit
     - Player death
     - Saucer flyby
     - Saucer hit
     - Bunker chip

2. Integrate sounds:
   - Player fires → play shot sound
   - Invader hit → play hit sound
   - Bomb spawns → play bomb sound
   - Formation moves → play step sound (looping, speed up with tempo)
   - Player dies → play death sound
   - Saucer spawns → play flyby sound
   - Saucer hit → play saucer hit sound

### Step 32: Test Audio
1. Verify all sounds play at correct times
2. Test volume control works
3. Test mute toggle
4. Verify step sound tempo increases with formation speed

---

## Phase 11: Menus and Game States

### Step 33: Implement Title Screen
1. Title screen state:
   - Render game title/logo
   - Menu options: Start Game, High Scores, Settings, Quit
   - Navigation with arrow keys/Enter
   - Handle menu selection

### Step 34: Implement Pause Menu
1. Pause state:
   - Overlay semi-transparent background
   - Show "PAUSED" text
   - Options: Resume, Restart, Quit to Title
   - Press P to resume
   - Handle menu selection

### Step 35: Implement Game Over Screen
1. Game over state:
   - Show "GAME OVER" text
   - Display final score
   - Check if new high score (prompt for name if desired)
   - Options: Restart, High Scores, Quit to Title
   - Save high score to file

### Step 36: Implement High Scores Screen (Optional)
1. High scores state:
   - Load scores from file
   - Display top 10 scores
   - Show names (if implemented) or just scores
   - Back to title option

### Step 37: Test All Menus
1. Navigate through all menu states
2. Test all transitions work correctly
3. Verify high scores save and load
4. Test pause/resume functionality

---

## Phase 12: Persistence and Settings

### Step 38: Implement Configuration File
1. Create `data/config.json`:
   - Screen settings (width, height)
   - Gameplay settings (starting lives, extra life threshold)
   - Audio settings (volume, mute)
   - Key bindings

2. Load config on startup
3. Save config on changes (settings menu)

### Step 39: Implement Settings Menu (Optional)
1. Settings state:
   - Volume slider
   - Key rebinding options
   - Difficulty options
   - Save settings to file

### Step 40: Test Persistence
1. Verify config loads on startup
2. Test high scores persist after game restart
3. Test settings save correctly

---

## Phase 13: Visual Polish

### Step 41: Implement Visual Effects
1. Hit flashes:
   - Brief white flash on invader hit
   - Subtle screen shake on player death (optional)
2. Death animations:
   - Explosion sprite sequence when invader destroyed
   - Player death animation
3. Particle effects (optional):
   - Small particles on hits

### Step 42: Improve Sprite Rendering
1. Replace placeholder rectangles with actual sprites
2. Ensure sprite animations are smooth
3. Optimize sprite rendering (use sprite groups efficiently)
4. Test performance (should maintain 60 FPS)

### Step 43: Test Visual Polish
1. Verify all animations play correctly
2. Check hit effects are visible but not distracting
3. Test performance with all effects enabled

---

## Phase 14: Testing and Bug Fixing

### Step 44: Comprehensive Testing
1. Manual test checklist:
   - [ ] Player movement bounds correctly
   - [ ] Bullet limit (5 max) constraint works
   - [ ] Formation movement and speed-up works
   - [ ] Collisions work for all entities
   - [ ] Scoring is accurate
   - [ ] Extra lives awarded correctly
   - [ ] Waves progress correctly
   - [ ] Pause/resume works
   - [ ] Game over triggers correctly
   - [ ] High scores save/load
   - [ ] Audio plays correctly
   - [ ] Performance is smooth (60 FPS)

### Step 45: Write Unit Tests
1. Test formation movement logic:
   - Boundary reversal
   - Speed-up calculations
   - Front-line invader detection
2. Test collision detection
3. Test scoring calculations
4. Test bunker damage application

### Step 46: Fix Identified Bugs
1. Document any bugs found
2. Fix one at a time
3. Re-test after each fix
4. Verify no regressions

---

## Phase 15: Balance and Fine-Tuning

### Step 47: Balance Gameplay
1. Adjust speeds:
   - Player movement speed
   - Bullet speed
   - Formation speed curve
   - Bomb spawn rates
2. Adjust scoring:
   - Verify point values feel appropriate
   - Extra life threshold feels fair
3. Adjust difficulty progression:
   - Waves should increase difficulty gradually
   - Game should be challenging but fair

### Step 48: Playtesting
1. Play through multiple waves
2. Identify any frustrating mechanics
3. Adjust based on feedback
4. Aim for feel similar to classic Space Invaders

---

## Phase 16: Final Polish and Documentation

### Step 49: Code Cleanup
1. Review all code:
   - Remove debug print statements
   - Add docstrings to classes and methods
   - Ensure consistent code style
   - Remove unused imports/code
2. Organize imports
3. Add inline comments where logic is complex

### Step 50: Create README
1. Update `README.md` with:
   - Project description
   - Installation instructions
   - How to run
   - Controls
   - Features
   - Screenshots (if available)
   - Credits/attributions

### Step 51: Final Testing
1. Complete end-to-end playthrough
2. Test on different screen sizes (if configurable)
3. Verify all features work as expected
4. Prepare for release/demonstration

---

## Implementation Tips

1. **Start Simple**: Use rectangles/sprites for everything initially, polish later
2. **Test Frequently**: Test each feature as you implement it
3. **Use Version Control**: Commit after each major feature
4. **Debugging**: Use Pygame's drawing tools (`pygame.draw.rect`) to visualize collision boxes during development
5. **Performance**: Use sprite groups efficiently, limit per-frame allocations
6. **Assets**: Use placeholder graphics initially, replace with final assets later
7. **Incremental Development**: Follow the steps in order; each builds on the previous

---

## Estimated Timeline

- **Phase 1-2**: 1-2 hours (Setup and game loop)
- **Phase 3-4**: 2-3 hours (Player and invaders)
- **Phase 5-6**: 2-3 hours (Combat and bunkers)
- **Phase 7-8**: 1-2 hours (Saucer, scoring, HUD)
- **Phase 9**: 1 hour (Waves)
- **Phase 10**: 1-2 hours (Audio)
- **Phase 11**: 2-3 hours (Menus)
- **Phase 12**: 1 hour (Persistence)
- **Phase 13**: 2-3 hours (Polish)
- **Phase 14-15**: 3-5 hours (Testing and balance)
- **Phase 16**: 1-2 hours (Documentation)

**Total Estimated Time**: 18-28 hours (depending on experience and polish level)

---

Good luck with your implementation!

