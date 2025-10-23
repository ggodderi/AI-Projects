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
            print("[Audio] Mixer initialized successfully.")
        except Exception as e:
            print(f"[Audio] Mixer initialization failed: {e}")
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
        # Generate a sine wave beep using numpy and play it
        if not self.initialized:
            print(f"[Audio] Mixer not initialized, cannot play beep {frequency}Hz.")
            return
        try:
            import numpy
            init = pygame.mixer.get_init()
            if not init:
                print("[Audio] Mixer not initialized (get_init is None).")
                return
            sample_rate, _, channels = init
            n_samples = int(sample_rate * duration_ms / 1000)
            t = numpy.linspace(0, duration_ms / 1000, n_samples, False)
            wave = (numpy.sin(2 * numpy.pi * frequency * t) * 32767 * 0.4).astype(numpy.int16)
            if channels >= 2:
                # Create stereo by duplicating mono signal across channels
                wave = numpy.column_stack((wave, wave)).copy(order="C")
            else:
                # Ensure shape is (n,)
                wave = wave.copy(order="C")
            sound = pygame.sndarray.make_sound(wave)
            print(f"[Audio] Playing beep {frequency}Hz for {duration_ms}ms.")
            sound.play(maxtime=duration_ms)
        except Exception as e:
            print(f"[Audio] Beep generation failed: {e}")

    def play_sfx(self, event: str) -> None:
        print(f"[Audio] SFX event triggered: {event}")
        if event == "fire":
            self.beep(880, 60)
        elif event == "alien_hit":
            self.beep(440, 80)
        elif event == "player_hit":
            self.beep(220, 120)
        elif event == "ufo":
            self.beep(1320, 100)
