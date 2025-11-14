import os
# Only set dummy audio driver if explicitly requested (for headless testing)
# Remove this line or set environment variable SDL_AUDIODRIVER=dummy if you need it
# os.environ.setdefault("SDL_AUDIODRIVER", "dummy")  # Commented out to allow real audio

import pygame

from src.game import Game


def main() -> None:
	pygame.init()
	pygame.display.set_caption("Space Invaders")
	
	game = Game()
	game.run()
	
	pygame.quit()


if __name__ == "__main__":
	main()
