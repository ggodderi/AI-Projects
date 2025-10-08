#!/usr/bin/env python3
"""
Space Invaders Game
A classic arcade-style Space Invaders game implementation in Python using Pygame.
"""

import pygame
import sys
import os
from game.space_invaders import SpaceInvadersGame

def main():
    """Main entry point for the Space Invaders game."""
    try:
        game = SpaceInvadersGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
