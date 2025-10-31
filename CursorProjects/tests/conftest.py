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
