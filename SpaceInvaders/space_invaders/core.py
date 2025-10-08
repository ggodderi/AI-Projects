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
    invader_move_delay: int = 30
    game_over: bool = False
    score: int = 0
    level: int = 1
    max_levels: int = 12
    # base move delay is the reference for level; invader_move_delay will be adjusted as invaders die
    base_move_delay: int = 30
    invader_initial_count: int = 0
    # bullet policy
    max_simultaneous_player_bullets: int = 5
    bullets_per_level_budget: int = 170
    bullets_used_this_level: int = 0

    def spawn_invader_grid(self, rows=4, cols=8, start_x=40, start_y=40, spacing_x=36, spacing_y=28):
        self.invaders = []
        for r in range(rows):
            for c in range(cols):
                self.invaders.append(Invader(start_x + c * spacing_x, start_y + r * spacing_y))
        # track initial count and reset move delay based on base
        self.invader_initial_count = len(self.invaders)
        self.invader_move_delay = self.base_move_delay

    def advance_level(self):
        """Advance to the next level, increase difficulty and spawn new invaders.

        Returns True if advanced, False if max levels reached.
        """
        if self.level >= self.max_levels:
            return False
        self.level += 1
        # increase difficulty: more rows/cols up to caps
        rows = min(6, 3 + self.level)
        cols = min(12, 6 + self.level)
        # speed up level by slightly reducing base move delay (min cap)
        self.base_move_delay = max(6, int(self.base_move_delay * 0.9))
        # spawn larger grid closer to top
        self.spawn_invader_grid(rows=rows, cols=cols, start_x=20, start_y=30, spacing_x=32, spacing_y=26)
        # clear bullets
        self.bullets = []
        self.bullets_used_this_level = 0
        self.invader_speed_timer = 0
        return True

    def reset(self):
        """Reset the game to initial state."""
        self.player = Player(self.width // 2 - 10, self.height - 40)
        self.score = 0
        self.level = 1
        self.invader_dx = 10
        self.invader_move_delay = 30
        self.bullets = []
        self.spawn_invader_grid()
        self.bullets_used_this_level = 0
        self.game_over = False
        self.invader_direction = 1
        self.invader_speed_timer = 0

    def player_shoot(self):
        # Allow up to max_simultaneous_player_bullets at a time and obey per-level budget
        if self.bullets_used_this_level >= self.bullets_per_level_budget:
            return None
        live_player_bullets = sum(1 for b in self.bullets if b.owner == 'player' and b.alive)
        if live_player_bullets >= self.max_simultaneous_player_bullets:
            return None
        b = Bullet(self.player.x + self.player.w // 2, self.player.y, dy=-8, owner='player')
        self.bullets.append(b)
        self.bullets_used_this_level += 1
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
        if self.invader_speed_timer >= self.invader_move_delay:
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

            # dynamic speed-up: as invaders are destroyed, reduce delay (min cap)
            alive = sum(1 for inv in self.invaders if inv.alive)
            if self.invader_initial_count > 0 and alive > 0:
                # Exponential scaling: as invaders are destroyed, delay decreases faster
                fraction = alive / float(self.invader_initial_count)
                # Use quadratic (exponent=2) scaling by default
                exponent = 2.0
                scaled = fraction ** exponent
                # target interpolates between base_move_delay (when fraction=1) and 6 (min) exponentially
                target = int(6 + (self.base_move_delay - 6) * scaled)
                self.invader_move_delay = max(6, target)

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
                    # increment score per invader
                    self.score += 10
                    break

        # check invaders reach player
        for inv in self.invaders:
            if inv.alive and inv.y + inv.h >= self.player.y:
                self.game_over = True

        # if all invaders cleared, do not auto-advance here; caller should call advance_level()
        # this avoids surprising mid-update spawn behavior during collision processing

    def is_level_cleared(self):
        return not any(inv.alive for inv in self.invaders)

    @staticmethod
    def _rect_collision(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw < bx or ax > bx + bw or ay + ah < by or ay > by + bh)
