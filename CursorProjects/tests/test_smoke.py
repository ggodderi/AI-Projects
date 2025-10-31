import pygame


def test_smoke_window_init_and_quit():
	# pygame.display.init() is called by conftest fixture
	screen = pygame.display.set_mode((1, 1))
	assert screen.get_size() == (1, 1)
	# If no exception until here, pass
	assert True
