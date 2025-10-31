import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")  # safe default if no audio device

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
