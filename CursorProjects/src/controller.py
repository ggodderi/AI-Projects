from __future__ import annotations

import pygame
from typing import Optional


def init_controllers() -> None:
	pygame.joystick.init()
	for i in range(pygame.joystick.get_count()):
		pygame.joystick.Joystick(i).init()


def get_primary_controller() -> Optional[pygame.joystick.Joystick]:
	if pygame.joystick.get_count() == 0:
		return None
	return pygame.joystick.Joystick(0)
