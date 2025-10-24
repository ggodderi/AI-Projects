
# Space Spiders — complete Space-Invaders–style game (pygame)
# Implements product requirements 1–23.
#
# Controls: Left/Right (A/D) to move, Space / Up / W to shoot.
# Game Over: Press Y/Enter to play again or N/Esc to quit.

import os
import sys
import math
import random
import threading
import time
from dataclasses import dataclass
from typing import List

import pygame

# ------------------ Config ------------------
SCREEN_W, SCREEN_H = 900, 700
FPS = 60

# Formation layout baseline
START_ROWS, START_COLS = 4, 8
CELL_W, CELL_H = 70, 50
INVADER_Y_OFFSET = 80
INVADER_STEP_DOWN = 22

# Speeds & pacing
INVADER_BASE_SPEED = 0.6          # pixels/frame baseline
BOMB_SPEED = 4.5
BULLET_SPEED = 8.0
PLAYER_SPEED = 6.0
INVADER_BOMB_INTERVAL = (1.1, 2.3)  # seconds between random bombs
WALL_INNER_TUCK = 6               # pixels tucked inside after a wall-hit
WALL_DROP_COOLDOWN_FRAMES = 8     # frames of immunity after dropping

# Gameplay limits
MAX_BULLETS_AIR = 5
BULLETS_PER_LEVEL = 170
MAX_LEVELS = 12
SCORE_PER_INVADER = 10
SCORE_PER_BOMB = 3

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (30, 210, 30)
RED = (220, 35, 35)
YELLOW = (240, 220, 40)
CYAN = (50, 200, 230)
MAGENTA = (230, 50, 180)

# ------------------ Helpers ------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ------------------ Pixel Art ------------------
def make_spider_surface(scale=2) -> pygame.Surface:
    # 16x12 mask -> ~32x24 at scale 2 (then drawn sharper)
    W, H = 16, 12
    mask = [
        "................",
        "...XXXX..XXXX...",
        "..XXXXXX.XXXX..",
        ".XXXXXXXXXXXX..",
        ".XXX.XXXX.XXX..",
        ".XXXXXXXXXXXX..",
        ".XX..XXXX..XX..",
        "...XX.XX.XX....",
        "...X..XX..X....",
        "..X..X..X..X...",
        ".X...X..X...X..",
        "X....X..X....X.",
    ]
    surf = pygame.Surface((W*scale, H*scale), pygame.SRCALPHA)
    for y,row in enumerate(mask):
        for x,ch in enumerate(row):
            if ch == "X":
                pygame.draw.rect(surf, MAGENTA, (x*scale, y*scale, scale, scale))
    # eyes
    pygame.draw.rect(surf, CYAN, (6*scale, 3*scale, scale, scale))
    pygame.draw.rect(surf, CYAN, (9*scale, 3*scale, scale, scale))
    return surf

def make_tank_surface(scale=3) -> pygame.Surface:
    # 18x10 mask -> 54x30 (≤ spider width ~64) to satisfy width rule
    W, H = 18, 10
    mask = [
        "..................",
        ".......XXXX.......",
        "......XXXXXX......",
        ".....XXXXXXXX.....",
        "XXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXX",
        "..XXXX......XXXX..",
        "..XXXX......XXXX..",
    ]
    surf = pygame.Surface((W*scale, H*scale), pygame.SRCALPHA)
    for y,row in enumerate(mask):
        for x,ch in enumerate(row):
            if ch == "X":
                pygame.draw.rect(surf, GREEN, (x*scale, y*scale, scale, scale))
    # cannon
    pygame.draw.rect(surf, GREEN, (9*scale, -3*scale, scale, 3*scale))
    return surf

def make_bullet_surface() -> pygame.Surface:
    s = pygame.Surface((4,12), pygame.SRCALPHA)
    pygame.draw.rect(s, YELLOW, (0,0,4,12))
    return s

def make_bomb_surface() -> pygame.Surface:
    s = pygame.Surface((6,10), pygame.SRCALPHA)
    pygame.draw.rect(s, RED, (0,0,6,10))
    return s

# ------------------ Entities ------------------
@dataclass
class Bullet:
    rect: pygame.Rect
    active: bool = True

@dataclass
class Bomb:
    rect: pygame.Rect
    active: bool = True

@dataclass
class Invader:
    x: float
    y: float
    alive: bool = True

class Player:
    def __init__(self, x, y, surf):
        self.surf = surf
        self.rect = surf.get_rect(midbottom=(x,y))
        self.speed = PLAYER_SPEED

    def move(self, dx):
        self.rect.x += dx*self.speed
        self.rect.x = clamp(self.rect.x, 0, SCREEN_W - self.rect.w)

    def draw(self, screen):
        screen.blit(self.surf, self.rect.topleft)

# ------------------ Sound Manager (threaded) ------------------
class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=256)
        except pygame.error:
            # Fallback without sound if device unavailable
            pass
        base = os.path.dirname(os.path.abspath(__file__))
        self.snd_shoot = self._load_sound(os.path.join(base, "shoot.wav"))
        self.snd_hit = self._load_sound(os.path.join(base, "hit.wav"))
        self.snd_boom = self._load_sound(os.path.join(base, "boom.wav"))
        self.lock = threading.Lock()
        self.queue = []
        self.alive = True
        self.thread = threading.Thread(target=self._runner, daemon=True)
        self.thread.start()

    def _load_sound(self, path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            class Null:
                def play(self_inner): pass
            return Null()

    def _runner(self):
        while self.alive:
            item = None
            with self.lock:
                if self.queue:
                    item = self.queue.pop(0)
            if item:
                try: item.play()
                except Exception: pass
            else:
                time.sleep(0.004)

    def play_shoot(self):
        with self.lock: self.queue.append(self.snd_shoot)
    def play_hit(self):
        with self.lock: self.queue.append(self.snd_hit)
    def play_boom(self):
        with self.lock: self.queue.append(self.snd_boom)

    def stop(self):
        self.alive = False
        try: self.thread.join(timeout=0.2)
        except Exception: pass

# ------------------ Bomb Scheduler (threaded) ------------------
class BombScheduler:
    def __init__(self, invaders: List[Invader], bombs: List[Bomb], stop_flag: threading.Event, spider_w: int):
        self.invaders = invaders
        self.bombs = bombs
        self.flag = stop_flag
        self.spider_w = spider_w
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while not self.flag.is_set():
            alive = [i for i in self.invaders if i.alive]
            if alive:
                inv = random.choice(alive)
                r = pygame.Rect(int(inv.x)+self.spider_w//2-3, int(inv.y)+10, 6, 10)
                self.bombs.append(Bomb(r))
            time.sleep(random.uniform(*INVADER_BOMB_INTERVAL))

# ------------------ Game ------------------
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 22)
        self.bigfont = pygame.font.SysFont("Consolas", 48, bold=True)
        self.smallfont = pygame.font.SysFont("Consolas", 18)

        # High score
        base = os.path.dirname(os.path.abspath(__file__))
        self.hs_path = os.path.join(base, "highscore.txt")
        self.high_score = 0
        self._load_high_score()
        self.high_beaten = False
        self.congrats_timer = 0

        self.snd = SoundManager()

        # Sprites
        self.spider_surf = make_spider_surface(scale=2)   # ~64 px wide
        self.tank_surf = make_tank_surface(scale=3)       # ~54 px wide (<= spider width)
        self.bullet_surf = make_bullet_surface()
        self.bomb_surf = make_bomb_surface()

        # Master loop flag
        self.running = True

        # Initialize game state
        self.reset_whole_game()

    # ---------- High score ----------
    def _load_high_score(self):
        try:
            with open(self.hs_path, "r") as f:
                self.high_score = int(f.read().strip() or "0")
        except Exception:
            self.high_score = 0

    def _save_high_score(self):
        try:
            with open(self.hs_path, "w") as f:
                f.write(str(int(self.high_score)))
        except Exception:
            pass

    # ---------- Game State ----------
    def reset_whole_game(self):
        self.level = 1
        self.score = 0
        self.game_over = False
        self.create_level(self.level)

    def create_level(self, level):
        self.game_over = False
        rows = START_ROWS + (level-1)//2
        cols = START_COLS + (level-1)
        cols = min(cols, 14)

        self.invaders: List[Invader] = []
        start_x = (SCREEN_W - cols*CELL_W)//2 + CELL_W//2
        for r in range(rows):
            for c in range(cols):
                x = start_x + c*CELL_W
                y = INVADER_Y_OFFSET + r*CELL_H
                self.invaders.append(Invader(x=float(x), y=float(y)))

        self.inv_dir = 1  # 1 right, -1 left
        self.inv_speed_base = INVADER_BASE_SPEED + (self.level-1)*0.25
        self.inv_rect_w = self.spider_surf.get_width()
        self.drop_cooldown = 0  # frames after a wall-drop to prevent chain drops

        # Player & ordnance
        self.player = Player(SCREEN_W//2, SCREEN_H-40, self.tank_surf)
        self.bullets: List[Bullet] = []
        self.bombs: List[Bomb] = []
        self.bullets_left = BULLETS_PER_LEVEL

        # Threading: bombs
        if hasattr(self, "bomb_flag"):
            self.bomb_flag.set()
        self.bomb_flag = threading.Event()
        self.bomb_thread = BombScheduler(self.invaders, self.bombs, self.bomb_flag, self.spider_surf.get_width())

    def shutdown_level_threads(self):
        if hasattr(self, "bomb_flag"):
            self.bomb_flag.set()

    # ---------- Input ----------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        self.player.move(dx)

    def shoot(self):
        if self.bullets_left <= 0: return
        if len([b for b in self.bullets if b.active]) >= MAX_BULLETS_AIR:
            return
        bx = self.player.rect.centerx - 2
        by = self.player.rect.top - 12
        rect = pygame.Rect(bx, by, 4, 12)
        self.bullets.append(Bullet(rect))
        self.bullets_left -= 1
        self.snd.play_shoot()

    # ---------- Updates ----------
    def current_invader_speed(self, alive_count_ratio: float) -> float:
        # Speed increases as invaders die (rule 13)
        return self.inv_speed_base * (1 + (1 - alive_count_ratio) * 1.2)

    def update_invaders(self):
        alive = [i for i in self.invaders if i.alive]
        if not alive:
            return "cleared"

        min_x = min(i.x for i in alive)
        max_x = max(i.x for i in alive) + self.inv_rect_w
        alive_ratio = len(alive)/len(self.invaders)
        speed = self.current_invader_speed(alive_ratio)

        left_limit = 20
        right_limit = SCREEN_W - 20

        if self.drop_cooldown > 0:
            self.drop_cooldown -= 1

        dx = speed * self.inv_dir
        will_hit_left = (min_x + dx) <= left_limit
        will_hit_right = (max_x + dx) >= right_limit
        hit_wall_now = (will_hit_left or will_hit_right) and (self.drop_cooldown == 0)

        if hit_wall_now:
            # Drop exactly one row
            for inv in alive:
                inv.y += INVADER_STEP_DOWN

            # Tuck inside to avoid immediate re-trigger
            if will_hit_left:
                shift = (left_limit - min_x) + WALL_INNER_TUCK
            else:
                shift = (right_limit - max_x) - WALL_INNER_TUCK  # negative value
            for inv in alive:
                inv.x += shift

            # Reverse and start cooldown
            self.inv_dir *= -1
            self.drop_cooldown = WALL_DROP_COOLDOWN_FRAMES

            # Ground check after drop
            for inv in alive:
                if inv.y + self.spider_surf.get_height() >= self.player.rect.bottom:
                    self.game_over = True
                    break
        else:
            # Normal horizontal advance
            for inv in alive:
                inv.x += dx

        # Collision with player (game over)
        if not self.game_over:
            for inv in alive:
                inv_rect = self.spider_surf.get_rect(topleft=(int(inv.x), int(inv.y)))
                if inv_rect.colliderect(self.player.rect):
                    self.game_over = True
                    break

        return None

    def update_bullets(self):
        # Move bullets up & cull
        for b in self.bullets:
            if not b.active: continue
            b.rect.y -= BULLET_SPEED
            if b.rect.bottom < 0:
                b.active = False

        # Bullet vs bomb
        for b in self.bullets:
            if not b.active: continue
            for bomb in self.bombs:
                if not bomb.active: continue
                if b.rect.colliderect(bomb.rect):
                    b.active = False
                    bomb.active = False
                    self.score += SCORE_PER_BOMB
                    if self.score > self.high_score:
                        if not self.high_beaten:
                            self.congrats_timer = int(4*FPS)
                        self.high_beaten = True
                        self.high_score = self.score
                        self._save_high_score()
                    self.snd.play_boom()
                    break

        # Bullet vs invader
        for b in self.bullets:
            if not b.active: continue
            for inv in self.invaders:
                if not inv.alive: continue
                inv_rect = self.spider_surf.get_rect(topleft=(int(inv.x), int(inv.y)))
                if b.rect.colliderect(inv_rect):
                    inv.alive = False
                    b.active = False
                    self.score += SCORE_PER_INVADER
                    if self.score > self.high_score:
                        if not self.high_beaten:
                            self.congrats_timer = int(4*FPS)
                        self.high_beaten = True
                        self.high_score = self.score
                        self._save_high_score()
                    self.snd.play_hit()
                    break

    def update_bombs(self):
        for bomb in self.bombs:
            if not bomb.active: continue
            bomb.rect.y += BOMB_SPEED
            if bomb.rect.top > SCREEN_H:
                bomb.active = False
                continue
            if bomb.rect.colliderect(self.player.rect):
                bomb.active = False
                self.game_over = True
                self.snd.play_boom()

    # ---------- Drawing ----------
    def draw_hud(self):
        hud = f"Score: {self.score}   High: {self.high_score}   Level: {self.level} / {MAX_LEVELS}   Bullets: {self.bullets_left}/{BULLETS_PER_LEVEL}"
        txt = self.font.render(hud, True, WHITE)
        self.screen.blit(txt, (14, 10))

    def draw(self):
        self.screen.fill((10,10,15))

        # Invaders
        for inv in self.invaders:
            if inv.alive:
                self.screen.blit(self.spider_surf, (int(inv.x), int(inv.y)))

        # Player
        self.player.draw(self.screen)

        # Bullets
        for b in self.bullets:
            if b.active:
                self.screen.blit(self.bullet_surf, b.rect.topleft)

        # Bombs
        for bomb in self.bombs:
            if bomb.active:
                self.screen.blit(self.bomb_surf, bomb.rect.topleft)

        # HUD
        self.draw_hud()

        # Congratulate if new high score
        if self.congrats_timer > 0:
            banner = self.bigfont.render("NEW HIGH SCORE!", True, YELLOW)
            self.screen.blit(banner, banner.get_rect(center=(SCREEN_W//2, 80)))
            self.congrats_timer -= 1

        pygame.display.flip()

    # ---------- Level / Game transitions ----------
    def level_cleared(self):
        self.shutdown_level_threads()
        self.level += 1
        if self.level > MAX_LEVELS:
            self.game_over = True
            return
        self.create_level(self.level)

    def game_over_screen(self):
        over = self.bigfont.render("GAME OVER", True, RED)
        reason = self.smallfont.render("Invaders reached you or a bomb hit you.", True, WHITE)
        if self.high_beaten:
            hsline = self.font.render(f"NEW HIGH SCORE: {self.high_score}", True, CYAN)
        else:
            hsline = self.font.render(f"High Score: {self.high_score}", True, CYAN)
        prompt = self.font.render("Press [Y] to play again or [N] to quit.", True, WHITE)
        self.screen.blit(over, over.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 60)))
        self.screen.blit(reason, reason.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 20)))
        self.screen.blit(hsline, hsline.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 20)))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 60)))
        pygame.display.flip()

    # ---------- Main loop ----------
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if not self.game_over and (event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP)):
                        self.shoot()
                    if self.game_over:
                        if event.key in (pygame.K_y, pygame.K_RETURN):
                            # Replay
                            self.shutdown_level_threads()
                            self.reset_whole_game()
                        elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                            self.running = False

            if not self.game_over:
                self.handle_input()
                status = self.update_invaders()
                self.update_bullets()
                self.update_bombs()
                if status == "cleared":
                    self.level_cleared()
                self.draw()
            else:
                self.game_over_screen()

            self.clock.tick(FPS)

        self.shutdown_level_threads()
        self._save_high_score()
        self.snd.stop()

# ------------------ Entrypoint ------------------
def main():
    pygame.init()
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
    pygame.display.set_caption("Space Spiders")
    Game(screen).run()
    pygame.quit()

if __name__ == "__main__":
    main()
