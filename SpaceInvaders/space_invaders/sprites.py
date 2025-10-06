"""Runtime pixel-art sprite generator for Space Invaders."""
import pygame

def make_sprite(width, height, pixels, palette):
    """Create a pygame Surface sprite from a small pixel map.

    pixels: list of rows, each row is a list of palette indices (ints)
    palette: list of RGB tuples
    """
    surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    surf = surf.convert_alpha()
    for y, row in enumerate(pixels):
        for x, idx in enumerate(row):
            if idx is None:
                continue
            color = palette[idx]
            surf.set_at((x, y), color)
    return surf

def player_sprite():
    # simple 9x6 ship pixel art
    pixels = [
        [None,None,1,1,1,1,1, None,None],
        [None,1,1,1,1,1,1,1,None],
        [1,1,1,1,1,1,1,1,1],
        [None,None,1,1,1,1,1,None,None],
        [None,None,1,1,1,1,1,None,None],
        [None,1,1,0,0,0,1,1,None],
    ]
    palette = [(0,0,0,0),(0,200,0,255),(60,160,200,255)]
    return make_sprite(9,6,pixels,palette)

def invader_sprite():
    # simple 11x8 invader
    pixels = [
        [None,None,2,2,2,2,2,2,None,None,None],
        [None,2,2,2,2,2,2,2,2,None,None],
        [2,2,1,2,2,2,2,1,2,2,2],
        [2,2,2,2,2,2,2,2,2,2,2],
        [None,2,2,2,2,2,2,2,2,None,None],
        [None,None,2,2,2,2,2,2,None,None,None],
        [None,2,None,2,None,2,None,2,None,2,None],
        [2,None,None,None,2,None,None,None,2,None,2],
    ]
    palette = [(0,0,0,0),(20,160,20,255),(200,180,20,255)]
    return make_sprite(11,8,pixels,palette)
