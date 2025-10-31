from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pygame


class AudioManager:
	def __init__(self, volume: float = 0.7) -> None:
		pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
		self.volume = max(0.0, min(1.0, volume))
		self.muted = False
		self.sounds: dict[str, Optional[pygame.mixer.Sound]] = {}
		self._load_sounds()
		self._generate_default_sounds()
	
	def _generate_tone(self, frequency: float, duration: float, sample_rate: int = 22050, wave_type: str = "sine") -> pygame.mixer.Sound:
		"""Generate a tone sound effect."""
		samples = int(duration * sample_rate)
		time_array = np.linspace(0, duration, samples)
		
		if wave_type == "sine":
			wave = np.sin(2 * np.pi * frequency * time_array)
		elif wave_type == "square":
			wave = np.sign(np.sin(2 * np.pi * frequency * time_array))
		elif wave_type == "sawtooth":
			wave = 2 * (time_array * frequency - np.floor(time_array * frequency + 0.5))
		else:
			wave = np.sin(2 * np.pi * frequency * time_array)
		
		# Apply envelope (fade in/out)
		envelope = np.ones(samples)
		fade_samples = min(int(0.01 * sample_rate), samples // 10)
		envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
		envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
		wave *= envelope
		
		# Convert to int16
		wave = (wave * 32767 * self.volume).astype(np.int16)
		# Make stereo
		stereo_wave = np.zeros((samples, 2), dtype=np.int16)
		stereo_wave[:, 0] = wave
		stereo_wave[:, 1] = wave
		
		sound = pygame.sndarray.make_sound(stereo_wave)
		return sound
	
	def _generate_player_shot(self) -> pygame.mixer.Sound:
		"""Generate player shot sound (high-pitched beep)."""
		return self._generate_tone(800, 0.1, wave_type="square")
	
	def _generate_invader_shot(self) -> pygame.mixer.Sound:
		"""Generate invader bomb sound (lower pitch)."""
		return self._generate_tone(300, 0.15, wave_type="sawtooth")
	
	def _generate_invader_hit(self) -> pygame.mixer.Sound:
		"""Generate invader hit sound (explosion-like)."""
		sample_rate = 22050
		duration = 0.2
		samples = int(duration * sample_rate)
		time_array = np.linspace(0, duration, samples)
		
		# Mix multiple frequencies for explosion effect
		wave = (np.sin(2 * np.pi * 200 * time_array) * 0.5 +
		        np.sin(2 * np.pi * 150 * time_array) * 0.3 +
		        np.sin(2 * np.pi * 100 * time_array) * 0.2)
		
		# Exponential decay
		envelope = np.exp(-time_array * 15)
		wave *= envelope
		
		wave = (wave * 32767 * self.volume).astype(np.int16)
		stereo_wave = np.zeros((samples, 2), dtype=np.int16)
		stereo_wave[:, 0] = wave
		stereo_wave[:, 1] = wave
		return pygame.sndarray.make_sound(stereo_wave)
	
	def _generate_player_death(self) -> pygame.mixer.Sound:
		"""Generate player death sound (longer explosion)."""
		sample_rate = 22050
		duration = 0.5
		samples = int(duration * sample_rate)
		time_array = np.linspace(0, duration, samples)
		
		# Descending frequencies
		freq = 400 - (time_array / duration) * 350
		wave = np.sin(2 * np.pi * freq * time_array)
		envelope = np.exp(-time_array * 5)
		wave *= envelope
		
		wave = (wave * 32767 * self.volume).astype(np.int16)
		stereo_wave = np.zeros((samples, 2), dtype=np.int16)
		stereo_wave[:, 0] = wave
		stereo_wave[:, 1] = wave
		return pygame.sndarray.make_sound(stereo_wave)
	
	def _generate_saucer_flyby(self) -> pygame.mixer.Sound:
		"""Generate saucer flyby sound (alternating tones)."""
		sample_rate = 22050
		duration = 2.0
		samples = int(duration * sample_rate)
		time_array = np.linspace(0, duration, samples)
		
		# Alternating frequencies
		freq = 600 + 100 * np.sin(2 * np.pi * 2 * time_array)
		wave = np.sin(2 * np.pi * freq * time_array)
		
		# Fade in/out
		envelope = np.ones(samples)
		fade = int(0.1 * sample_rate)
		envelope[:fade] = np.linspace(0, 1, fade)
		envelope[-fade:] = np.linspace(1, 0, fade)
		wave *= envelope
		
		wave = (wave * 32767 * self.volume * 0.6).astype(np.int16)
		stereo_wave = np.zeros((samples, 2), dtype=np.int16)
		stereo_wave[:, 0] = wave
		stereo_wave[:, 1] = wave
		return pygame.sndarray.make_sound(stereo_wave)
	
	def _generate_saucer_hit(self) -> pygame.mixer.Sound:
		"""Generate saucer hit sound."""
		return self._generate_invader_hit()
	
	def _generate_bunker_chip(self) -> pygame.mixer.Sound:
		"""Generate bunker chip sound (short click)."""
		return self._generate_tone(1000, 0.05, wave_type="square")
	
	def _generate_default_sounds(self) -> None:
		"""Generate default procedural sounds."""
		sound_generators = {
			"player_shot": self._generate_player_shot,
			"invader_shot": self._generate_invader_shot,
			"invader_hit": self._generate_invader_hit,
			"player_death": self._generate_player_death,
			"saucer_flyby": self._generate_saucer_flyby,
			"saucer_hit": self._generate_saucer_hit,
			"bunker_chip": self._generate_bunker_chip,
		}
		
		for name, generator in sound_generators.items():
			if name not in self.sounds or self.sounds[name] is None:
				try:
					self.sounds[name] = generator()
					self.sounds[name].set_volume(self.volume)
				except Exception:
					self.sounds[name] = None
	
	def _load_sounds(self) -> None:
		"""Load sound effects from files if they exist."""
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
					pass  # Will use generated sound instead
	
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

