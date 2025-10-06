import pytest
from space_invaders.core import GameState, Bullet, Invader


def test_spawn_and_counts():
    gs = GameState()
    gs.spawn_invader_grid(rows=2, cols=3, start_x=0, start_y=0, spacing_x=10, spacing_y=10)
    assert len(gs.invaders) == 6
    assert all(isinstance(i, Invader) for i in gs.invaders)


def test_player_shoot_only_one():
    gs = GameState()
    # allow up to 3 bullets
    b1 = gs.player_shoot()
    assert b1 is not None
    b2 = gs.player_shoot()
    assert b2 is not None
    b3 = gs.player_shoot()
    assert b3 is not None
    b4 = gs.player_shoot()
    assert b4 is None
    # simulate one bullet dead
    b1.alive = False
    b4 = gs.player_shoot()
    assert b4 is not None


def test_bullet_hits_invader_and_stops():
    gs = GameState(width=200, height=200)
    # ensure player is within screen for this small test area
    gs.player.y = 160
    # place single invader directly above player
    gs.invaders = [Invader(gs.player.x, gs.player.y - 50)]
    b = gs.player_shoot()
    assert b is not None
    # move bullet into invader
    for _ in range(10):
        gs.update()
    # bullet should be dead and invader dead
    assert not gs.invaders[0].alive
    assert not b.alive


def test_invaders_descend_and_game_over():
    gs = GameState(width=100, height=200)
    gs.player.y = 180
    # put invader close so that after a few moves it reaches player
    gs.invaders = [Invader(0, gs.player.y - 10)]
    # force movement to happen
    for _ in range(60):
        gs.update()
        if gs.game_over:
            break
    assert gs.game_over
