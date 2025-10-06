"""Core, testable game logic for Space Invaders."""
from dataclasses import dataclass, field
from typing import List, Tuple

Point = Tuple[int, int]

@dataclass
class Bullet:
    x: int
    y: int
    dy: int
    owner: str  # 'player' or 'invader'
    alive: bool = True

    def update(self):
        if not self.alive:
            return
        self.y += self.dy

@dataclass
class Invader:
    x: int
    y: int
    w: int = 16
    h: int = 12
    alive: bool = True

    def rect(self):
        return (self.x, self.y, self.w, self.h)

@dataclass
class Player:
    x: int
    y: int
    w: int = 20
    h: int = 12

    def rect(self):
        return (self.x, self.y, self.w, self.h)

@dataclass
class GameState:
    width: int = 400
    height: int = 600
    player: Player = field(default_factory=lambda: Player(190, 560))
    invaders: List[Invader] = field(default_factory=list)
    bullets: List[Bullet] = field(default_factory=list)
    invader_dx: int = 10
    invader_direction: int = 1
    invader_speed_timer: int = 0
    game_over: bool = False

    def spawn_invader_grid(self, rows=4, cols=8, start_x=40, start_y=40, spacing_x=36, spacing_y=28):
        self.invaders = []
        for r in range(rows):
            for c in range(cols):
                self.invaders.append(Invader(start_x + c * spacing_x, start_y + r * spacing_y))

    def player_shoot(self):
        # Only allow one player bullet at a time
        for b in self.bullets:
            if b.owner == 'player' and b.alive:
                return None
        b = Bullet(self.player.x + self.player.w // 2, self.player.y, dy=-8, owner='player')
        self.bullets.append(b)
        return b

    def update(self):
        if self.game_over:
            return

        # update bullets
        for b in self.bullets:
            if not b.alive:
                continue
            b.update()
            # remove bullets off-screen
            if b.y < 0 or b.y > self.height:
                b.alive = False

        # invader movement timer (simple)
        self.invader_speed_timer += 1
        if self.invader_speed_timer >= 30:
            self.invader_speed_timer = 0
            # compute next positions
            dx = self.invader_dx * self.invader_direction
            will_hit_edge = False
            for inv in self.invaders:
                if not inv.alive:
                    continue
                nx = inv.x + dx
                if nx < 0 or nx + inv.w > self.width:
                    will_hit_edge = True
                    break
            if will_hit_edge:
                # descend and reverse
                for inv in self.invaders:
                    if inv.alive:
                        inv.y += inv.h
                self.invader_direction *= -1
            else:
                for inv in self.invaders:
                    if inv.alive:
                        inv.x += dx

        # collisions: bullets vs invaders
        for b in self.bullets:
            if not b.alive or b.owner != 'player':
                continue
            for inv in self.invaders:
                if not inv.alive:
                    continue
                if self._rect_collision((b.x, b.y, 2, 4), inv.rect()):
                    inv.alive = False
                    b.alive = False
                    break

        # check invaders reach player
        for inv in self.invaders:
            if inv.alive and inv.y + inv.h >= self.player.y:
                self.game_over = True

    @staticmethod
    def _rect_collision(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw < bx or ax > bx + bw or ay + ah < by or ay > by + bh)
