from __future__ import annotations

import pygame

from settings import WHITE


class Alien:
    def __init__(self, x: int, y: int, w: int, h: int, value: int) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.value = value
        self.alive = True

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, WHITE, self.rect, 1)
