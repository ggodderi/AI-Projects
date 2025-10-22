from __future__ import annotations

import random

import pygame

from settings import WINDOW_WIDTH, UFO_WIDTH, UFO_HEIGHT, UFO_SPEED, WHITE


class UFO:
    def __init__(self, y: int = 48) -> None:
        self.rect = pygame.Rect(-UFO_WIDTH, y, UFO_WIDTH, UFO_HEIGHT)
        self.speed = UFO_SPEED
        self.active = False
        self.value = random.choice([50, 100, 150, 300])
        self.direction = 1

    def spawn(self) -> None:
        self.active = True
        self.direction = random.choice([-1, 1])
        if self.direction > 0:
            self.rect.x = -self.rect.width
        else:
            self.rect.x = WINDOW_WIDTH

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.rect.x += int(self.direction * self.speed * dt)
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.active:
            pygame.draw.rect(surface, WHITE, self.rect, 2)
