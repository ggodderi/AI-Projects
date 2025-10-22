from __future__ import annotations

import pygame


class Projectile:
    def __init__(self, x: int, y: int, w: int, h: int, vy: float, color=(255, 255, 255)) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.vy = vy
        self.color = color
        self.alive = True

    def update(self, dt: float) -> None:
        self.rect.y += int(self.vy * dt)
        if self.rect.bottom < 0 or self.rect.top > 2000:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
