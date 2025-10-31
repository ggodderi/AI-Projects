from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pygame


class AudioManager:
	def __init__(self, volume: float = 0.7) -> None:
		pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
		self.volume = max(0.0, min(1.0, volume))
		self.muted = False
		self.sounds: dict[str, Optional[pygame.mixer.Sound]] = {}
		self._load_sounds()
	
	def _load_sounds(self) -> None:
		"""Load sound effects. Creates silent placeholders if files don't exist."""
		sound_dir = Path("assets/sounds")
		sound_files = {
			"player_shot": "shot.wav",
			"invader_shot": "bomb.wav",
			"invader_hit": "invader_hit.wav",
			"player_death": "player_death.wav",
			"saucer_flyby": "saucer_flyby.wav",
			"saucer_hit": "saucer_hit.wav",
			"bunker_chip": "bunker_chip.wav",
		}
		
		for name, filename in sound_files.items():
			filepath = sound_dir / filename
			if filepath.exists():
				try:
					self.sounds[name] = pygame.mixer.Sound(str(filepath))
					self.sounds[name].set_volume(self.volume)
				except Exception:
					self.sounds[name] = None
			else:
				self.sounds[name] = None
	
	def play_sound(self, name: str) -> None:
		"""Play a sound effect by name."""
		if self.muted:
			return
		if name in self.sounds and self.sounds[name] is not None:
			try:
				self.sounds[name].play()
			except Exception:
				pass  # Ignore playback errors
	
	def set_volume(self, volume: float) -> None:
		"""Set volume (0.0 to 1.0)."""
		self.volume = max(0.0, min(1.0, volume))
		for sound in self.sounds.values():
			if sound is not None:
				sound.set_volume(self.volume)
	
	def mute(self) -> None:
		"""Toggle mute."""
		self.muted = not self.muted
	
	def is_muted(self) -> bool:
		"""Check if muted."""
		return self.muted

