# Space Invaders Game

A classic arcade-style Space Invaders game implementation in Python using Pygame, based on the original 1978 arcade game.

## Features

- **Authentic Graphics**: Pixel-perfect invader sprites and player ship design
- **Sound Effects**: Laser shots and hit sounds for immersive gameplay
- **Progressive Difficulty**: 12 levels with increasing speed and challenge
- **Bullet Management**: Limited bullets per level (170) with HUD display
- **Collision Detection**: Precise hit detection between bullets and invaders
- **Game Over Conditions**: Multiple ways to end the game (invaders reach bottom, hit player, bullets exhausted)
- **Performance Optimized**: Multithreaded audio and efficient rendering
- **Score System**: Points awarded based on invader type destroyed

## Requirements

- Python 3.7+
- Pygame 2.5.2+
- NumPy 1.24.3+

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python main.py
   ```

2. **Controls:**
   - **Arrow Keys** or **A/D**: Move left/right
   - **Spacebar**: Shoot
   - **Escape**: Quit game
   - **Y/N**: Play again/Quit (on game over screen)

3. **Objective:**
   - Destroy all spider invaders before they reach the bottom
   - Each spider type gives different points:
     - Top row (large spiders): 30 points
     - Middle rows (medium spiders): 20 points  
     - Bottom rows (small spiders): 10 points
   - Complete 12 levels to win the game

4. **Game Mechanics:**
   - You have 170 bullets per level
   - Maximum 5 bullets on screen at once
   - Invaders speed up as their numbers decrease
   - Each level increases invader speed
   - Invaders periodically drop bombs that can destroy your tank
   - You can shoot bombs to destroy them before they hit your tank
   - Game ends if invaders reach the bottom, hit your tank, or a bomb hits your tank

## Game Structure

```
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── game/
│   ├── __init__.py
│   ├── space_invaders.py   # Main game engine
│   ├── config.py          # Game configuration
│   ├── entities/          # Game objects
│   │   ├── __init__.py
│   │   ├── player.py      # Player ship
│   │   ├── invader.py     # Invader sprites and group
│   │   ├── bullet.py      # Bullet system
│   │   └── explosion.py   # Explosion effects
│   ├── ui/                # User interface
│   │   ├── __init__.py
│   │   ├── hud.py         # Heads-up display
│   │   └── game_over_screen.py
│   └── audio/             # Sound system
│       ├── __init__.py
│       └── sound_manager.py
```

## Technical Features

- **Multithreading**: Audio playback runs in separate threads to prevent game lag
- **Efficient Rendering**: Optimized sprite rendering and collision detection
- **Modular Design**: Clean separation of concerns with entity-component architecture
- **Configurable**: Easy to modify game parameters through config.py
- **Performance Monitoring**: Built-in frame rate management

## Customization

You can easily modify game parameters in `game/config.py`:
- Screen dimensions
- Colors
- Game speeds
- Bullet limits
- Invader formations
- Sound volumes

## Troubleshooting

If you encounter issues:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check that you're using Python 3.7 or higher
3. Verify pygame is properly installed: `python -c "import pygame; print(pygame.version.ver)"`

## Credits

Based on the original Space Invaders arcade game (1978) by Taito Corporation.
Implemented as a tribute to classic arcade gaming.
