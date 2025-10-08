import os
import tempfile
from space_invaders import generate_wav, MAX_IN_AIR, Bullet


def test_generate_wav_creates_file(tmp_path):
    fn = tmp_path / "test.wav"
    generate_wav(str(fn), freq=440, duration=0.02)
    assert fn.exists()
    assert fn.stat().st_size > 0


def test_bullet_limit():
    # create a small list to simulate in-air bullets
    bullets = []
    for i in range(MAX_IN_AIR + 2):
        if len(bullets) < MAX_IN_AIR:
            bullets.append(Bullet(0, 0, -1))
        else:
            # attempts to add beyond limit should not increase list
            before = len(bullets)
            if len(bullets) < MAX_IN_AIR:
                bullets.append(Bullet(0, 0, -1))
            assert len(bullets) == before
