from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

import pygame

# Try to import numpy, fallback to math if not available
try:
	import numpy as np
	HAS_NUMPY = True
except ImportError:
	HAS_NUMPY = False
	np = None


class AudioManager:
	def __init__(self, volume: float = 0.7) -> None:
		# Initialize mixer - use real audio device if available
		# Only fallback to dummy if explicitly needed (for headless testing)
		try:
			# Don't set dummy driver - use real audio
			pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
			# Verify mixer is actually initialized
			if not pygame.mixer.get_init():
				raise RuntimeError("Mixer not initialized")
		except Exception:
			# Only use dummy as absolute last resort
			try:
				import os
				# Only set dummy if not already set
				if "SDL_AUDIODRIVER" not in os.environ:
					os.environ["SDL_AUDIODRIVER"] = "dummy"
				pygame.mixer.quit()
				pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
			except Exception:
				pass  # Audio not available
		
		self.volume = max(0.0, min(1.0, volume))
		self.muted = False
		self.sounds: dict[str, Optional[pygame.mixer.Sound]] = {}
		self._load_sounds()
		self._generate_default_sounds()
	
	def _generate_tone(self, frequency: float, duration: float, sample_rate: int = 22050, wave_type: str = "sine") -> pygame.mixer.Sound:
		"""Generate a tone sound effect."""
		if not HAS_NUMPY:
			# Fallback: generate simple tone using math
			return self._generate_tone_fallback(frequency, duration, sample_rate, wave_type)
		
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
	
	def _generate_tone_fallback(self, frequency: float, duration: float, sample_rate: int, wave_type: str) -> pygame.mixer.Sound:
		"""Fallback tone generator without numpy."""
		samples = int(duration * sample_rate)
		# Create byte array for stereo 16-bit sound
		import array
		arr = array.array('h', [0] * (samples * 2))
		
		for i in range(samples):
			t = i / sample_rate
			if wave_type == "sine":
				val = math.sin(2 * math.pi * frequency * t)
			elif wave_type == "square":
				val = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
			else:
				val = math.sin(2 * math.pi * frequency * t)
			
			# Simple envelope
			fade_samples = min(int(0.01 * sample_rate), samples // 10)
			if i < fade_samples:
				val *= i / fade_samples if fade_samples > 0 else 1.0
			elif i >= samples - fade_samples:
				val *= (samples - i) / fade_samples if fade_samples > 0 else 1.0
			
			sample_val = int(val * 32767 * self.volume)
			# Stereo: left and right channels
			arr[i * 2] = sample_val
			arr[i * 2 + 1] = sample_val
		
		try:
			sound = pygame.sndarray.make_sound(arr)
			return sound
		except Exception:
			# Create a minimal silent sound as last resort
			silent = array.array('h', [0] * (samples * 2))
			return pygame.sndarray.make_sound(silent)
	
	def _generate_player_shot(self) -> pygame.mixer.Sound:
		"""Generate player shot sound (high-pitched beep)."""
		return self._generate_tone(800, 0.1, wave_type="square")
	
	def _generate_invader_shot(self) -> pygame.mixer.Sound:
		"""Generate invader bomb sound (lower pitch)."""
		return self._generate_tone(300, 0.15, wave_type="sawtooth")
	
	def _generate_invader_hit(self) -> pygame.mixer.Sound:
		"""Generate invader hit sound (explosion-like)."""
		if not HAS_NUMPY:
			return self._generate_tone_fallback(200, 0.2, 22050, "sine")
		
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
		if not HAS_NUMPY:
			return self._generate_tone_fallback(300, 0.5, 22050, "sine")
		
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
		if not HAS_NUMPY:
			return self._generate_tone_fallback(600, 0.5, 22050, "sine")
		
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
					sound = generator()
					if sound is not None:
						sound.set_volume(self.volume)
						self.sounds[name] = sound
					else:
						self.sounds[name] = None
				except Exception as e:
					# Try to generate a simple fallback sound
					try:
						self.sounds[name] = self._generate_tone_fallback(440, 0.1, 22050, "sine")
						if self.sounds[name]:
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
				# Check if mixer is initialized
				if not pygame.mixer.get_init():
					pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
				self.sounds[name].play()
			except Exception:
				# Try to reinitialize and play
				try:
					pygame.mixer.quit()
					pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
					if name in self.sounds and self.sounds[name] is not None:
						self.sounds[name].play()
				except Exception:
					pass  # Audio not available
	
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

