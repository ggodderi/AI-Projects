from typing import Optional

import pygame

from settings import MASTER_VOLUME, SFX_VOLUME


class Audio:
    def __init__(self) -> None:
        self.initialized = False
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(MASTER_VOLUME)
            self.initialized = True
        except Exception:
            # Audio might fail on some systems; continue silently
            self.initialized = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}

    def load_sound(self, key: str, path: Optional[str] = None) -> None:
        if not self.initialized or not path:
            return
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(SFX_VOLUME)
            self.sounds[key] = snd
        except Exception:
            pass

    def play(self, key: str) -> None:
        if not self.initialized:
            return
        snd = self.sounds.get(key)
        if snd is not None:
            try:
                snd.play()
            except Exception:
                pass

    def beep(self, frequency: int = 880, duration_ms: int = 60) -> None:
        # Minimal fallback: try to play a short tone using Sound object if mixer is initialized.
        # If not available, do nothing.
        # Note: Generating tones requires numpy; we avoid that dependency here.
        pass
