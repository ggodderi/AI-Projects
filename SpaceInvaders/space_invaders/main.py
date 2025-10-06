"""Run the Space Invaders game using pygame."""
import sys
import pygame
try:
    # when run as package: python -m space_invaders.main
    from .core import GameState
except Exception:
    # when run directly: python space_invaders/main.py
    from core import GameState  # type: ignore
import numpy as np

SCREEN_W = 400
SCREEN_H = 600

def make_sound(frequency=440, duration_ms=120, volume=0.2, sample_rate=44100):
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
    tone = np.sin(frequency * 2 * np.pi * t)
    mono = (tone * (2**15 - 1) * volume).astype(np.int16)
    # pygame mixer often expects a 2D array for stereo. Make stereo by duplicating channels.
    stereo = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)

def draw_player(surf, player):
    pygame.draw.polygon(surf, (0, 255, 0), [(player.x, player.y + player.h), (player.x + player.w//2, player.y), (player.x + player.w, player.y + player.h)])

def draw_invader(surf, inv):
    pygame.draw.rect(surf, (255, 255, 0), inv.rect())

def draw_bullet(surf, b):
    if b.owner == 'player':
        color = (0, 255, 255)
    else:
        color = (255, 0, 0)
    pygame.draw.rect(surf, color, (b.x, b.y, 2, 6))

def run():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    gs = GameState(width=SCREEN_W, height=SCREEN_H)
    gs.spawn_invader_grid()

    shot_sound = make_sound(880, 80, 0.08)
    hit_sound = make_sound(220, 160, 0.12)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    b = gs.player_shoot()
                    if b:
                        shot_sound.play()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            gs.player.x = max(0, gs.player.x - 6)
        if keys[pygame.K_RIGHT]:
            gs.player.x = min(gs.width - gs.player.w, gs.player.x + 6)

        prev_alive = sum(1 for i in gs.invaders if i.alive)
        gs.update()
        post_alive = sum(1 for i in gs.invaders if i.alive)
        if post_alive < prev_alive:
            hit_sound.play()

        screen.fill((0, 0, 0))
        draw_player(screen, gs.player)
        for inv in gs.invaders:
            if inv.alive:
                draw_invader(screen, inv)
        for b in gs.bullets:
            if b.alive:
                draw_bullet(screen, b)

        if gs.game_over:
            font = pygame.font.SysFont(None, 48)
            surf = font.render('GAME OVER', True, (255, 0, 0))
            screen.blit(surf, (100, 280))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    run()
