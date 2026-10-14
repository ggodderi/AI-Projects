"""Deterministic Snake rules, independent of rendering and audio."""
from collections import deque
from random import Random

DIRECTIONS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
DIFFICULTIES = {"Easy": 7, "Normal": 10, "Hard": 14}


class SnakeGame:
    def __init__(self, width=30, height=22, rng=None):
        if width < 6 or height < 4:
            raise ValueError("Board must be at least 6 by 4 cells")
        self.width, self.height = width, height
        self.rng = rng or Random()
        self.reset()

    def reset(self):
        x, y = self.width // 2, self.height // 2
        self.snake = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = DIRECTIONS["right"]
        self.turns = deque()
        self.score = 0
        self.alive = True
        self.won = False
        self.food = self._food()

    def _food(self):
        occupied = set(self.snake)
        free = [(x, y) for y in range(self.height) for x in range(self.width)
                if (x, y) not in occupied]
        return self.rng.choice(free) if free else None

    def turn(self, name):
        """Queue at most two valid turns; reject reversal and repeat inputs."""
        if not self.alive or name not in DIRECTIONS or len(self.turns) >= 2:
            return False
        new = DIRECTIONS[name]
        previous = self.turns[-1] if self.turns else self.direction
        if new == previous or new == (-previous[0], -previous[1]):
            return False
        self.turns.append(new)
        return True

    def step(self):
        """Advance one cell; return move, eat, dead, won, or idle."""
        if not self.alive:
            return "idle"
        if self.turns:
            self.direction = self.turns.popleft()
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)
        growing = head == self.food
        body = self.snake if growing else self.snake[:-1]
        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height) or head in body:
            self.alive = False
            return "dead"
        self.snake.insert(0, head)
        if growing:
            self.score += 10
            self.food = self._food()
            if self.food is None:
                self.won, self.alive = True, False
                return "won"
            return "eat"
        self.snake.pop()
        return "move"
