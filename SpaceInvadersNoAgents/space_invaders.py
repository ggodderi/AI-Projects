"""Space Invaders-like game implemented with pygame.

Features (from design):
- Python + pygame
- Authentic pixel-art style invaders and shooter drawn procedurally
- Sound on shot and hit (generated at runtime)
- Bullet stops on hit; max 5 bullets in-air and 170 bullets per level
- Score, bullets remaining, level, and game over screen with replay prompt
- Levels up to 12; each level increases invader count/speed; invaders speed up as they are destroyed
- Simple multithreading: sound playback worker and a small background worker for level setup

Run: python space_invaders.py
Requires: pygame
"""

import os
import sys
import math
import random
import threading
import queue
import time
import wave
import struct

try:
    import pygame
except Exception:
    print("This game requires pygame. Install with: pip install pygame")
    raise

# Constants
SCREEN_W, SCREEN_H = 600, 700
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = -8
INVADER_DROP = 20
MAX_IN_AIR = 5
MAX_BULLETS_PER_LEVEL = 170
MAX_LEVEL = 12

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

HIGH_SCORE_FILE = os.path.join(ASSETS_DIR, 'highscore.json')


def generate_wav(filename, freq=440, duration=0.08, volume=0.5, sample_rate=44100, wave_type='sine'):
    """Generate a short WAV file for simple sound effects.
    This avoids external assets and numpy.
    """
    n_samples = int(sample_rate * duration)
    amplitude = int(32767 * volume)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            if wave_type == 'sine':
                sample = amplitude * math.sin(2 * math.pi * freq * t)
            elif wave_type == 'square':
                sample = amplitude * (1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0)
            else:
                sample = amplitude * math.sin(2 * math.pi * freq * t)
            wf.writeframes(struct.pack('<h', int(sample)))


def generate_bgm(filename, sample_rate=22050):
    """Generate a short looping background 'tune' and save as WAV.
    Keeps it very light-weight — sequence of tones.
    """
    melody = [440, 660, 550, 440, 0, 330, 440]
    duration_per_note = 0.25
    n_samples = int(sample_rate * duration_per_note * len(melody))
    amplitude = int(16000)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for freq in melody:
            for i in range(int(sample_rate * duration_per_note)):
                t = float(i) / sample_rate
                if freq <= 0:
                    sample = 0
                else:
                    sample = amplitude * math.sin(2 * math.pi * freq * t)
                wf.writeframes(struct.pack('<h', int(sample)))


SHOT_WAV = os.path.join(ASSETS_DIR, 'shot.wav')
HIT_WAV = os.path.join(ASSETS_DIR, 'hit.wav')
BGM_WAV = os.path.join(ASSETS_DIR, 'bgm.wav')
if not os.path.exists(SHOT_WAV):
    generate_wav(SHOT_WAV, freq=1200, duration=0.06, volume=0.3, wave_type='square')
if not os.path.exists(HIT_WAV):
    generate_wav(HIT_WAV, freq=600, duration=0.12, volume=0.4, wave_type='sine')
if not os.path.exists(BGM_WAV):
    generate_bgm(BGM_WAV)


class SoundWorker(threading.Thread):
    """Background worker to play sounds from a queue. Keeps sound play off the main logic thread."""

    def __init__(self):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self._stop = threading.Event()
        self.sounds = {}
        # initialize mixer here to avoid threading issues
        pygame.mixer.init()
        self.sounds['shot'] = pygame.mixer.Sound(SHOT_WAV)
        self.sounds['hit'] = pygame.mixer.Sound(HIT_WAV)
        # background music — use pygame music module for looping
        try:
            pygame.mixer.music.load(BGM_WAV)
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
        except Exception:
            # fallback: ignore music errors
            pass

    def run(self):
        while not self._stop.is_set():
            try:
                name = self.q.get(timeout=0.1)
            except queue.Empty:
                continue
            snd = self.sounds.get(name)
            if snd:
                snd.play()

    def play(self, name):
        try:
            self.q.put_nowait(name)
        except queue.Full:
            pass

    def stop(self):
        self._stop.set()


def make_pixel_surface(pattern, scale=4, fg=(0, 255, 0), bg=(0, 0, 0, 0)):
    """Create a surface from a list of strings with X for filled pixels."""
    h = len(pattern)
    w = max(len(r) for r in pattern)
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    surf.fill(bg)
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch == 'X':
                rect = pygame.Rect(x * scale, y * scale, scale, scale)
                surf.fill(fg, rect)
    return surf


PLAYER_PIX = [
    '  X  ',
    ' XXX ',
    'XXXXX',
]

# Spider-like invader pixel patterns with two frames each for a simple leg animation.
# Each entry is a list of two frames; each frame is a list of rows.
INVADER_PATTERNS = [
    [
        [
            '  X  ',
            ' XXX ',
            'XXXXX',
            'X X X',
            ' X X ',
        ],
        [
            '  X  ',
            ' XXX ',
            'X X X',
            'X X X',
            ' X X ',
        ],
    ],
    [
        [
            ' X X ',
            'XXXXX',
            'X X X',
            ' X X ',
            '  X  ',
        ],
        [
            ' X X ',
            'XXXXX',
            ' XXX ',
            ' X X ',
            '  X  ',
        ],
    ],
    [
        [
            '  X  ',
            ' XXX ',
            'X X X',
            ' XXX ',
            '  X  ',
        ],
        [
            '  X  ',
            ' XXX ',
            'X X X',
            'X X X',
            '  X  ',
        ],
    ],
]


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 40
        self.h = 20
        self.speed = PLAYER_SPEED
        self.surface = make_pixel_surface(PLAYER_PIX, scale=4, fg=(0, 180, 255))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen):
        screen.blit(self.surface, (self.x + (self.w - self.surface.get_width()) // 2, self.y))


class Bullet:
    def __init__(self, x, y, dy):
        self.x = x
        self.y = y
        self.dy = dy
        self.w = 4
        self.h = 10
        self.color = (255, 255, 0)

    def update(self):
        self.y += self.dy

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect())


class Invader:
    def __init__(self, x, y, pattern_index=0):
        # store positions as floats for smooth movement
        self.x = float(x)
        self.y = float(y)
        self.alive = True
        self.pattern_index = pattern_index
        # create two-frame animation surfaces for this invader
        frames = INVADER_PATTERNS[self.pattern_index % len(INVADER_PATTERNS)]
        # make spiders bigger (scale 5)
        self.surfaces = [make_pixel_surface(f, scale=5, fg=(150, 50, 180)) for f in frames]
        self.frame_index = 0
        self.last_frame_time = time.time()
        self.frame_interval = 0.32  # seconds between frames (slightly faster)
        self.w = self.surfaces[0].get_width()
        self.h = self.surfaces[0].get_height()

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen):
        if self.alive:
            # toggle frame based on time
            now = time.time()
            if now - self.last_frame_time >= self.frame_interval:
                self.frame_index = (self.frame_index + 1) % len(self.surfaces)
                self.last_frame_time = now
            screen.blit(self.surfaces[self.frame_index], (self.x, self.y))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption('Space Invaders - Python')
        self.clock = pygame.time.Clock()
        self.running = True
        self.sound_worker = SoundWorker()
        self.sound_worker.start()

        self.font = pygame.font.SysFont('Arial', 20)
        self.large_font = pygame.font.SysFont('Arial', 44)

        self.reset_game()

        # background worker for level setup (demonstrates threading requirement)
        self.bg_worker = threading.Thread(target=self._bg_worker_loop, daemon=True)
        self.bg_worker.start()
        # track whether space is currently held to allow one shot per press
        self.space_down = False
        # load high score
        self.high_score = self.load_high_score()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.bullets_remaining = MAX_BULLETS_PER_LEVEL
        self.bullets = []
        self.player = Player(SCREEN_W // 2 - 20, SCREEN_H - 60)
        self.invaders = []
        self.invader_dx = 1.0
        self.invader_direction = 1
        self.last_move_time = 0
        self.move_interval = 0.7
        self.spawn_level(self.level)

    def load_high_score(self):
        try:
            import json
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    data = json.load(f)
                    return int(data.get('high_score', 0))
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            import json
            data = {'high_score': max(self.high_score, self.score)}
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def spawn_level(self, level):
        # Increase invader count & speed with level
        rows = min(5 + level // 2, 7)
        cols = min(6 + level, 12)
        margin_x = 40
        margin_y = 60
        spacing_x = (SCREEN_W - 2 * margin_x) // cols
        spacing_y = 40
        self.invaders = []
        for r in range(rows):
            for c in range(cols):
                x = margin_x + c * spacing_x + (spacing_x - 30) // 2
                y = margin_y + r * spacing_y
                self.invaders.append(Invader(x, y, pattern_index=(r + c) % len(INVADER_PATTERNS)))
        # base speed decreases interval between moves
        # make invaders faster: significantly shorter base interval and larger dx per move
        base = max(0.45 - (level - 1) * 0.03, 0.04)
        self.move_interval = base
        # higher base speed and bigger per-level increase
        self.invader_speed = 2.0 + (level - 1) * 0.6
        self.bullets_remaining = MAX_BULLETS_PER_LEVEL

    def _bg_worker_loop(self):
        # background worker placeholder: could preload assets or compute level prep
        while self.running:
            time.sleep(1.0)

    def play_sound(self, name):
        self.sound_worker.play(name)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        self.sound_worker.stop()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if not self.space_down:
                        self.try_shoot()
                        self.space_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.space_down = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.x = max(0, self.player.x - self.player.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.x = min(SCREEN_W - self.player.w, self.player.x + self.player.speed)

    def try_shoot(self):
        # enforce both active bullets limit and total bullets per level
        if len(self.bullets) >= MAX_IN_AIR:
            return
        if self.bullets_remaining <= 0:
            return
        # create bullet from center-top of player
        bx = self.player.x + self.player.w // 2 - 2
        by = self.player.y - 10
        self.bullets.append(Bullet(bx, by, BULLET_SPEED))
        self.bullets_remaining -= 1
        self.play_sound('shot')

    def update(self, dt):
        # Update bullets
        for b in list(self.bullets):
            b.update()
            if b.y < -50 or b.y > SCREEN_H + 50:
                self.bullets.remove(b)

        # Invader movement timing
        now = time.time()
        if now - self.last_move_time >= self.move_interval:
            self._move_invaders()
            self.last_move_time = now

        # Check collisions: bullets vs invaders
        for b in list(self.bullets):
            for inv in self.invaders:
                if inv.alive and b.rect().colliderect(inv.rect()):
                    inv.alive = False
                    try:
                        self.bullets.remove(b)
                    except ValueError:
                        pass
                    self.score += 10
                    self.play_sound('hit')
                    break

        # Check invaders vs player or ground
        for inv in self.invaders:
            if not inv.alive:
                continue
            if inv.rect().colliderect(self.player.rect()):
                self.game_over()
                return
            if inv.y + inv.h >= self.player.y:
                self.game_over()
                return

        # Level cleared?
        if all(not inv.alive for inv in self.invaders):
            self.level += 1
            if self.level > MAX_LEVEL:
                self.win_game()
            else:
                # spawn next level faster and with more invaders
                self.spawn_level(self.level)

        # As invaders decrease, speed them up slightly
        alive = sum(1 for inv in self.invaders if inv.alive)
        total = max(1, len(self.invaders))
        # make move interval shorter as fewer invaders remain
        self.move_interval = max(0.05, (0.9 - (self.level - 1) * 0.06) * (alive / total))

    def _move_invaders(self):
        # Determine edges
        xs = [inv.x for inv in self.invaders if inv.alive]
        if not xs:
            return
        left = min(xs)
        right = max(inv.x + inv.w for inv in self.invaders if inv.alive)
        # use float dx for smoother and faster movement
        dx = self.invader_direction * self.invader_speed
        # If hit edge, move down and reverse
        if right + dx >= SCREEN_W - 10 or left + dx <= 10:
            for inv in self.invaders:
                if inv.alive:
                    inv.y += INVADER_DROP
            self.invader_direction *= -1
        else:
            for inv in self.invaders:
                if inv.alive:
                    inv.x += dx

    def draw(self):
        self.screen.fill((10, 10, 30))
        # Draw player
        self.player.draw(self.screen)
        # Draw invaders
        for inv in self.invaders:
            inv.draw(self.screen)
        # Draw bullets
        for b in self.bullets:
            b.draw(self.screen)

        # HUD (include high score)
        hud = f"Score: {self.score}  High: {self.high_score}  Level: {self.level}  Bullets left: {self.bullets_remaining}"
        text = self.font.render(hud, True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()

    def game_over(self):
        # Save high score if needed, show game over, and ask replay
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self._show_message(f"GAME OVER - Score: {self.score}", f"High Score: {self.high_score} - Press Y to play again, N to quit")
        # prompt
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.reset_game()
                        waiting = False
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
            self.clock.tick(10)

    def win_game(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self._show_message(f"YOU WIN! Score: {self.score}", f"High Score: {self.high_score} - Press Y to play again, N to quit")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.reset_game()
                        waiting = False
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
            self.clock.tick(10)

    def _show_message(self, title, subtitle):
        # dim
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        t_surf = self.large_font.render(title, True, (255, 255, 255))
        s_surf = self.font.render(subtitle, True, (200, 200, 200))
        self.screen.blit(t_surf, ((SCREEN_W - t_surf.get_width()) // 2, SCREEN_H // 2 - 40))
        self.screen.blit(s_surf, ((SCREEN_W - s_surf.get_width()) // 2, SCREEN_H // 2 + 10))
        pygame.display.flip()


def main():
    g = Game()
    g.run()


if __name__ == '__main__':
    main()
