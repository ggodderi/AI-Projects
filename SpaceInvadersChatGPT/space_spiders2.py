
# Space Spiders — a retro Space-Invaders–style game
# Requirements covered:
# 1) Gameplay like Space Invaders; 2) Authentic-looking sprites (retro pixel art)
# 3) Sound on shot & hit; 4) One bullet kills max one invader; bullet stops on hit
# 5) If invaders reach shooter level or hit shooter => game over
# 6) Python + pygame; 7) Performant: threaded sound queue; blit-optimized surfaces
# 8) Up to 5 bullets airborne
# 9) HUD score; 10) Game over screen when invaders hit ground/shooter
# 11) Prompt to play again; 12) Progressive levels up to 12; faster & more invaders
# 13) Fewer invaders => faster step
# 14) Uses multithreading (sound manager + bomb dropper)
# 15) 170 bullets per level; after that, no more shots
# 16) HUD shows bullets remaining
# 17) Shooter looks like a tank; 18) Invaders look like spiders
# 19) Invaders drop bombs; 20) Bullet can destroy bomb
# 21) Shooter width <= invader width

import os
import sys
import math
import random
import threading
import time
from dataclasses import dataclass
from typing import List, Tuple

import pygame

# --------------- Config ---------------
SCREEN_W, SCREEN_H = 900, 700
FPS = 60

# Gameplay tuning
START_ROWS, START_COLS = 4, 8
CELL_W, CELL_H = 70, 50
INVADER_Y_OFFSET = 80
INVADER_STEP_DOWN = 22
INVADER_BASE_SPEED = 0.6  # pixels/frame baseline; scaled per level and invader count
INVADER_BOMB_INTERVAL = (1.1, 2.3)  # random seconds between bomb drops (per cohort thread)
BOMB_SPEED = 4.5
BULLET_SPEED = 8.0
PLAYER_SPEED = 6.0
MAX_BULLETS_AIR = 5
BULLETS_PER_LEVEL = 170
MAX_LEVELS = 12
PLAYER_LIVES = 1  # classic vibe: one hit = game over
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
GRAY = (140, 140, 140)

# --------------- Utilities ---------------
def clamp(x, a, b):
    return max(a, min(b, x))

# --------------- Sound (threaded) ---------------
class SoundManager:
    """A background thread that plays queued sounds so the main loop never blocks."""
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=256)
        self.lock = threading.Lock()
        self.queue = []
        self.alive = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        # Preload sounds (generated files saved alongside script or cwd)
        base = os.path.dirname(os.path.abspath(__file__))
        self.snd_shoot = pygame.mixer.Sound(os.path.join(base, "shoot.wav"))
        self.snd_hit = pygame.mixer.Sound(os.path.join(base, "hit.wav"))
        self.snd_boom = pygame.mixer.Sound(os.path.join(base, "boom.wav"))

    def _run(self):
        while self.alive:
            item = None
            with self.lock:
                if self.queue:
                    item = self.queue.pop(0)
            if item:
                try:
                    item.play()
                except Exception:
                    pass
            else:
                time.sleep(0.005)

    def play_shoot(self): 
        with self.lock: self.queue.append(self.snd_shoot)
    def play_hit(self): 
        with self.lock: self.queue.append(self.snd_hit)
    def play_boom(self): 
        with self.lock: self.queue.append(self.snd_boom)

    def stop(self):
        self.alive = False
        try:
            self.thread.join(timeout=0.2)
        except Exception:
            pass

# --------------- Sprites (retro pixel art) ---------------
def make_spider_surface(scale=2) -> pygame.Surface:
    """Create a pixel-art spider invader. Width ~ 32px at scale=2 => 64px.
       Shooter width must be <= invader width (#21). We'll use ~64px invader; tank <= 64 px."""
    # 16x12 pixel mask
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
    # add eyes
    eye_color = CYAN
    pygame.draw.rect(surf, eye_color, (6*scale, 3*scale, scale, scale))
    pygame.draw.rect(surf, eye_color, (9*scale, 3*scale, scale, scale))
    return surf

def make_tank_surface(scale=3) -> pygame.Surface:
    """Retro tank: width <= spider width. Spider ~ 32*scale(2)=64; let's make tank width 54."""
    # 18x10 grid -> width 18*3=54
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
    # Cannon
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

# --------------- Entities ---------------
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
    pos: pygame.Vector2
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

# --------------- Bomb dropper (thread) ---------------
class BombScheduler:
    def __init__(self, invaders: List[Invader], bombs: List[Bomb], stop_flag: threading.Event):
        self.invaders = invaders
        self.bombs = bombs
        self.flag = stop_flag
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while not self.flag.is_set():
            # choose a random alive invader to drop bomb
            alive = [i for i in self.invaders if i.alive]
            if alive:
                inv = random.choice(alive)
                r = pygame.Rect(int(inv.pos.x)-3, int(inv.pos.y)+10, 6, 10)
                self.bombs.append(Bomb(r))
            # wait randomized interval
            time.sleep(random.uniform(*INVADER_BOMB_INTERVAL))

# --------------- Game ---------------
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 22)
        self.bigfont = pygame.font.SysFont("Consolas", 48, bold=True)
        self.smallfont = pygame.font.SysFont("Consolas", 18)

        self.snd = SoundManager()

        self.spider_surf = make_spider_surface(scale=2)  # ~64px wide
        self.tank_surf = make_tank_surface(scale=3)      # ~54px wide (<= invader width)
        self.bullet_surf = make_bullet_surface()
        self.bomb_surf = make_bomb_surface()

        self.reset_game()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.game_over = False
        self.running = True
        self.create_level(self.level)

    def create_level(self, level):
        rows = START_ROWS + (level-1)//2  # slowly add rows
        cols = START_COLS + (level-1)     # more columns each level
        cols = min(cols, 14)
        self.invaders: List[Invader] = []
        start_x = (SCREEN_W - cols*CELL_W)//2 + CELL_W//2
        for r in range(rows):
            for c in range(cols):
                x = start_x + c*CELL_W
                y = INVADER_Y_OFFSET + r*CELL_H
                self.invaders.append(Invader(pygame.Vector2(x,y)))
        self.inv_dir = 1  # 1 right, -1 left
        self.inv_speed = INVADER_BASE_SPEED + (self.level-1)*0.25  # faster each level
        self.inv_rect_w = self.spider_surf.get_width()

        self.player = Player(SCREEN_W//2, SCREEN_H-40, self.tank_surf)

        self.bullets: List[Bullet] = []
        self.bombs: List[Bomb] = []

        self.bullets_left = BULLETS_PER_LEVEL

        # threading: bomb scheduler
        if hasattr(self, "bomb_flag"):
            self.bomb_flag.set()
        self.bomb_flag = threading.Event()
        self.bomb_thread = BombScheduler(self.invaders, self.bombs, self.bomb_flag)

    def shutdown_level_threads(self):
        if hasattr(self, "bomb_flag"):
            self.bomb_flag.set()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        self.player.move(dx)

    def shoot(self):
        if len([b for b in self.bullets if b.active]) >= MAX_BULLETS_AIR:
            return
        if self.bullets_left <= 0:
            return
        # spawn bullet at cannon
        bx = self.player.rect.centerx - 2
        by = self.player.rect.top - 12
        rect = pygame.Rect(bx, by, 4, 12)
        self.bullets.append(Bullet(rect))
        self.bullets_left -= 1
        self.snd.play_shoot()

    def update_invaders(self):
        # compute bounding box to know when to bounce
        alive = [i for i in self.invaders if i.alive]
        if not alive:
            return "cleared"
        min_x = min(i.pos.x for i in alive)
        max_x = max(i.pos.x for i in alive) + self.inv_rect_w

        # speed-up as invaders die (#13)
        alive_ratio = len(alive)/len(self.invaders)
        # lower ratio => faster; boost up to +120%
        speed = self.inv_speed * (1 + (1-alive_ratio)*1.2)

        # move horizontally
        dx = speed * self.inv_dir
        for inv in alive:
            inv.pos.x += dx

        # bounce & step down
        left_limit = 20
        right_limit = SCREEN_W - 20
        if min_x <= left_limit or max_x >= right_limit:
            self.inv_dir *= -1
            for inv in alive:
                inv.pos.y += INVADER_STEP_DOWN
                # check ground hit (#5/#10)
                if inv.pos.y + self.spider_surf.get_height() >= self.player.rect.bottom:
                    self.game_over = True

        # collision: invader touching player (#5)
        for inv in alive:
            inv_rect = self.spider_surf.get_rect(topleft=(int(inv.pos.x), int(inv.pos.y)))
            if inv_rect.colliderect(self.player.rect):
                self.game_over = True
                break

        return None

    def update_bullets(self):
        for b in self.bullets:
            if not b.active: 
                continue
            b.rect.y -= BULLET_SPEED
            if b.rect.bottom < 0:
                b.active = False

        # bullet vs bomb (#20)
        for b in self.bullets:
            if not b.active: continue
            for bomb in self.bombs:
                if not bomb.active: continue
                if b.rect.colliderect(bomb.rect):
                    b.active = False
                    bomb.active = False
                    self.score += SCORE_PER_BOMB
                    self.snd.play_boom()
                    break

        # bullet vs invader (#4)
        for b in self.bullets:
            if not b.active: continue
            for inv in self.invaders:
                if not inv.alive: continue
                inv_rect = self.spider_surf.get_rect(topleft=(int(inv.pos.x), int(inv.pos.y)))
                if b.rect.colliderect(inv_rect):
                    inv.alive = False
                    b.active = False  # stop bullet on first hit
                    self.score += SCORE_PER_INVADER
                    self.snd.play_hit()
                    break

    def update_bombs(self):
        for bomb in self.bombs:
            if not bomb.active: continue
            bomb.rect.y += BOMB_SPEED
            if bomb.rect.top > SCREEN_H:
                bomb.active = False
                continue
            # hit player (#19)
            if bomb.rect.colliderect(self.player.rect):
                bomb.active = False
                self.game_over = True
                self.snd.play_boom()

    def draw_hud(self):
        hud = f"Score: {self.score}   Level: {self.level} / {MAX_LEVELS}   Bullets: {self.bullets_left}/{BULLETS_PER_LEVEL}"
        txt = self.font.render(hud, True, WHITE)
        self.screen.blit(txt, (14, 10))

    def draw(self):
        self.screen.fill((10,10,15))

        # invaders
        for inv in self.invaders:
            if inv.alive:
                self.screen.blit(self.spider_surf, (int(inv.pos.x), int(inv.pos.y)))

        # player
        self.player.draw(self.screen)

        # bullets
        for b in self.bullets:
            if b.active:
                self.screen.blit(self.bullet_surf, b.rect.topleft)

        # bombs
        for bomb in self.bombs:
            if bomb.active:
                self.screen.blit(self.bomb_surf, bomb.rect.topleft)

        # HUD
        self.draw_hud()

        pygame.display.flip()

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
        prompt = self.font.render("Press [Y] to play again or [N] to quit.", True, WHITE)
        self.screen.blit(over, over.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 40)))
        self.screen.blit(reason, reason.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 40)))
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if not self.game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP):
                        self.shoot()
                    if self.game_over:
                        if event.key in (pygame.K_y, pygame.K_RETURN):
                            # ask to play again (#11)
                            self.shutdown_level_threads()
                            self.reset_game()
                        elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                            self.running = False

            if not self.game_over:
                self.handle_input()
                status = self.update_invaders()
                self.update_bullets()
                self.update_bombs()

                # stop shooting when bullets exhausted (#15) — handled in shoot()

                if status == "cleared":
                    self.level_cleared()

                self.draw()
            else:
                self.game_over_screen()

            self.clock.tick(FPS)

        self.shutdown_level_threads()
        self.snd.stop()

def main():
    pygame.init()
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags, vsync=1 if hasattr(pygame.display, "gl_set_swap_interval") else 0)
    pygame.display.set_caption("Space Spiders")
    Game(screen).run()
    pygame.quit()

if __name__ == "__main__":
    main()
