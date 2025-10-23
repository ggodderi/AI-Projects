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
        # Draw a spider-like alien creature
        x, y, w, h = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        c = self.color
        # Body (oval)
        pygame.draw.ellipse(surface, c, (x + w // 8, y + h // 4, w * 3 // 4, h // 2))
        # Eyes (black)
        pygame.draw.circle(surface, (0,0,0), (x + w // 3, y + h // 2), w // 10)
        pygame.draw.circle(surface, (0,0,0), (x + w - w // 3, y + h // 2), w // 10)
        # Fangs (white)
        pygame.draw.rect(surface, (255,255,255), (x + w // 2 - w // 12, y + h // 2 + h // 6, w // 24, h // 8))
        pygame.draw.rect(surface, (255,255,255), (x + w // 2 + w // 24, y + h // 2 + h // 6, w // 24, h // 8))
        # Legs (8 legs)
        leg_color = (40,40,40)
        leg_len = w // 3
        for i in range(4):
            # Left legs
            start = (x + w // 4, y + h // 2 + i * h // 10)
            end = (start[0] - leg_len, start[1] + leg_len // 2)
            pygame.draw.line(surface, leg_color, start, end, 2)
            # Right legs
            start = (x + w - w // 4, y + h // 2 + i * h // 10)
            end = (start[0] + leg_len, start[1] + leg_len // 2)
            pygame.draw.line(surface, leg_color, start, end, 2)
