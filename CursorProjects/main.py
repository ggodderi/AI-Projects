import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")  # safe default if no audio device

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def main() -> None:
	pygame.init()
	pygame.display.set_caption("Space Invaders")
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	clock = pygame.time.Clock()
	running = True

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		screen.fill((0, 0, 0))
		pygame.display.flip()
		clock.tick(FPS)

	pygame.quit()


if __name__ == "__main__":
	main()
