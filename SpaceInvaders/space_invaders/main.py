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
import threading
import queue
try:
    from .sprites import player_sprite, invader_sprite
except Exception:
    from sprites import player_sprite, invader_sprite  # type: ignore

SCREEN_W = 400
SCREEN_H = 600

def make_sound(frequency=440, duration_ms=120, volume=0.2, sample_rate=44100):
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
    tone = np.sin(frequency * 2 * np.pi * t)
    mono = (tone * (2**15 - 1) * volume).astype(np.int16)
    # pygame mixer often expects a 2D array for stereo. Make stereo by duplicating channels.
    stereo = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)


def draw_player(surf, player, sprite):
    # sprite is expected pre-scaled to player size
    surf.blit(sprite, (player.x, player.y))

def draw_invader(surf, inv, sprite):
    # sprite is expected pre-scaled to invader size
    surf.blit(sprite, (inv.x, inv.y))

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
    # create sprites (base sprites)
    p_sprite = player_sprite()
    i_sprite = invader_sprite()
    # pre-scale sprites to current sizes to avoid per-frame scaling
    scaled_player = pygame.transform.scale(p_sprite, (gs.player.w, gs.player.h))
    # determine invader size from first invader or defaults
    if gs.invaders:
        inv_w, inv_h = gs.invaders[0].w, gs.invaders[0].h
    else:
        inv_w, inv_h = 16, 12
    scaled_invader = pygame.transform.scale(i_sprite, (inv_w, inv_h))

    # sound queue and worker
    sound_q = queue.Queue()
    def sound_worker(q):
        while True:
            item = q.get()
            if item is None:
                break
            snd = item
            try:
                snd.play()
            except Exception:
                pass
        # drain
        while not q.empty():
            q.get()

    worker = threading.Thread(target=sound_worker, args=(sound_q,), daemon=True)
    worker.start()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    b = gs.player_shoot()
                    if b:
                        # enqueue sound for background playback
                        sound_q.put(shot_sound)
                    # handle restart/quit on game over
                    if gs.game_over:
                        if e.key == pygame.K_r:
                            gs.reset()
                        if e.key == pygame.K_q:
                            running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            gs.player.x = max(0, gs.player.x - 6)
        if keys[pygame.K_RIGHT]:
            gs.player.x = min(gs.width - gs.player.w, gs.player.x + 6)

        prev_alive = sum(1 for i in gs.invaders if i.alive)
        gs.update()
        post_alive = sum(1 for i in gs.invaders if i.alive)
        if post_alive < prev_alive:
            sound_q.put(hit_sound)

        screen.fill((0, 0, 0))
        # draw player (pre-scaled)
        draw_player(screen, gs.player, scaled_player)
        # draw invaders using pre-scaled sprite
        for inv in gs.invaders:
            if inv.alive:
                draw_invader(screen, inv, scaled_invader)
        # draw bullets
        for b in gs.bullets:
            if b.alive:
                draw_bullet(screen, b)

        # HUD: score, level, bullets
        font = pygame.font.SysFont(None, 24)
        live_bullets = sum(1 for b in gs.bullets if b.owner=="player" and b.alive)
        bullets_left = max(0, gs.bullets_per_level_budget - gs.bullets_used_this_level)
        hud = font.render(
            f'Score: {gs.score}   Level: {gs.level}   Bullets: {bullets_left}/{gs.bullets_per_level_budget} ({live_bullets} in flight)',
            True,
            (255,255,255),
        )
        screen.blit(hud, (8,8))

        if gs.game_over:
            font_big = pygame.font.SysFont(None, 48)
            surf = font_big.render('GAME OVER', True, (255, 0, 0))
            screen.blit(surf, (SCREEN_W//2 - surf.get_width()//2, SCREEN_H//2 - 40))
            score_surf = font.render(f'Final Score: {gs.score}   Level Reached: {gs.level}', True, (255,255,255))
            screen.blit(score_surf, (SCREEN_W//2 - score_surf.get_width()//2, SCREEN_H//2 + 10))
            prompt = font.render('Press R to play again or Q to quit', True, (200,200,200))
            screen.blit(prompt, (SCREEN_W//2 - prompt.get_width()//2, SCREEN_H//2 + 40))

        # if level cleared, automatically advance after a short pause and update scaled sprites
        if not gs.game_over and gs.is_level_cleared():
            # brief pause to show cleared screen
            level_msg = font.render(f'Level {gs.level} Cleared!', True, (200,200,50))
            screen.blit(level_msg, (SCREEN_W//2 - level_msg.get_width()//2, SCREEN_H//2 - 10))
            pygame.display.flip()
            pygame.time.delay(700)
            advanced = gs.advance_level()
            if advanced:
                # recompute scaled invader sprite for new invader size
                if gs.invaders:
                    inv_w, inv_h = gs.invaders[0].w, gs.invaders[0].h
                else:
                    inv_w, inv_h = inv_w, inv_h
                scaled_invader = pygame.transform.scale(i_sprite, (inv_w, inv_h))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    run()
