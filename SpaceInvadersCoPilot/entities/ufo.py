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
            x, y, w, h = self.rect.x, self.rect.y, self.rect.width, self.rect.height
            # UFO body (oval)
            pygame.draw.ellipse(surface, (255,0,0), (x, y + h // 4, w, h // 2))
            # Dome
            pygame.draw.ellipse(surface, (255,255,255), (x + w // 4, y, w // 2, h // 2))
            # Lights (multi-color)
            colors = [(255,255,0), (0,255,255), (0,255,0)]
            for i in range(3):
                lx = x + w // 4 + i * w // 6
                ly = y + h * 3 // 4
                pygame.draw.circle(surface, colors[i], (lx, ly), h // 10)
