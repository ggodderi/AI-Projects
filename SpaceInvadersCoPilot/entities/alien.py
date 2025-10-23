from __future__ import annotations

import pygame

from settings import WHITE


class Alien:
    def __init__(self, x: int, y: int, w: int, h: int, value: int, color=(255,255,255)) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.value = value
        self.color = color
        self.alive = True

    def draw(self, surface: pygame.Surface) -> None:
        # Draw a simple pixel-art alien (classic shape) with color
        x, y, w, h = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        c = self.color
        # Body
        pygame.draw.rect(surface, c, (x + w // 8, y + h // 4, w * 3 // 4, h // 2))
        # Eyes
        pygame.draw.rect(surface, (0,0,0), (x + w // 4, y + h // 3, w // 8, h // 8))
        pygame.draw.rect(surface, (0,0,0), (x + w - w // 4 - w // 8, y + h // 3, w // 8, h // 8))
        # Antennae
        pygame.draw.rect(surface, c, (x + w // 3, y, w // 6, h // 6))
        # Legs
        pygame.draw.rect(surface, c, (x + w // 8, y + h - h // 6, w // 8, h // 6))
        pygame.draw.rect(surface, c, (x + w - w // 4, y + h - h // 6, w // 8, h // 6))
