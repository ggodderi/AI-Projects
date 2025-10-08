"""
Sound Manager for Space Invaders game.
Handles all game audio including shots, hits, and background music.
"""

import pygame
import os
import threading

class SoundManager:
    """Manages all game audio."""
    
    def __init__(self):
        """Initialize the sound manager."""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Create simple sound effects using pygame's built-in sound generation
        self.shot_sound = self.create_shot_sound()
        self.hit_sound = self.create_hit_sound()
        self.explosion_sound = self.create_explosion_sound()
        
        # Sound volume
        self.shot_sound.set_volume(0.3)
        self.hit_sound.set_volume(0.5)
        self.explosion_sound.set_volume(0.4)
    
    def create_shot_sound(self) -> pygame.mixer.Sound:
        """Create a laser shot sound effect."""
        # Generate a simple beep sound
        sample_rate = 22050
        duration = 0.1
        frames = int(duration * sample_rate)
        
        # Create a simple sine wave
        import math
        sound_array = []
        frequency = 800
        
        for i in range(frames):
            sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            sound_array.append([sample, sample])  # Stereo
        
        import numpy as np
        # Convert to proper stereo format
        stereo_array = np.array(sound_array, dtype=np.int16)
        sound = pygame.sndarray.make_sound(stereo_array)
        return sound
    
    def create_hit_sound(self) -> pygame.mixer.Sound:
        """Create a hit sound effect."""
        sample_rate = 22050
        duration = 0.2
        frames = int(duration * sample_rate)
        
        import math
        sound_array = []
        
        for i in range(frames):
            # Create a more complex sound with multiple frequencies
            freq1 = 400
            freq2 = 600
            sample1 = int(16383 * math.sin(2 * math.pi * freq1 * i / sample_rate))
            sample2 = int(16383 * math.sin(2 * math.pi * freq2 * i / sample_rate))
            sample = (sample1 + sample2) // 2
            sound_array.append([sample, sample])
        
        import numpy as np
        # Convert to proper stereo format
        stereo_array = np.array(sound_array, dtype=np.int16)
        sound = pygame.sndarray.make_sound(stereo_array)
        return sound
    
    def create_explosion_sound(self) -> pygame.mixer.Sound:
        """Create an explosion sound effect."""
        sample_rate = 22050
        duration = 0.3
        frames = int(duration * sample_rate)
        
        import math
        import random
        sound_array = []
        
        for i in range(frames):
            # Create noise-like explosion sound
            noise = random.randint(-16383, 16383)
            envelope = 1.0 - (i / frames)  # Fade out
            sample = int(noise * envelope)
            sound_array.append([sample, sample])
        
        import numpy as np
        # Convert to proper stereo format
        stereo_array = np.array(sound_array, dtype=np.int16)
        sound = pygame.sndarray.make_sound(stereo_array)
        return sound
    
    def play_shot_sound(self):
        """Play the shot sound effect."""
        def play_sound():
            self.shot_sound.play()
        
        # Play sound in a separate thread to avoid blocking
        sound_thread = threading.Thread(target=play_sound)
        sound_thread.daemon = True
        sound_thread.start()
    
    def play_hit_sound(self):
        """Play the hit sound effect."""
        def play_sound():
            self.hit_sound.play()
        
        sound_thread = threading.Thread(target=play_sound)
        sound_thread.daemon = True
        sound_thread.start()
    
    def play_explosion_sound(self):
        """Play the explosion sound effect."""
        def play_sound():
            self.explosion_sound.play()
        
        sound_thread = threading.Thread(target=play_sound)
        sound_thread.daemon = True
        sound_thread.start()
