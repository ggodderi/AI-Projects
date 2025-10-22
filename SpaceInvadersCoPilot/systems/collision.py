from __future__ import annotations

import random
from typing import List, Tuple

import pygame


def rect_collision(a: pygame.Rect, b: pygame.Rect) -> bool:
    return a.colliderect(b)


def any_collision(rect: pygame.Rect, rects: List[pygame.Rect]) -> Tuple[bool, int]:
    for i, r in enumerate(rects):
        if rect.colliderect(r):
            return True, i
    return False, -1
