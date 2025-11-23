"""
Font management for Darth Vader RPG GUI.
Handles font loading with fallbacks to system fonts.
"""

import pygame
import os

# Font paths (will add custom fonts to assets/fonts/ later)
FONTS_DIR = os.path.join("assets", "fonts")

# Font sizes
TITLE_SIZE = 48
HEADER_SIZE = 36
LARGE_SIZE = 28
NORMAL_SIZE = 20
SMALL_SIZE = 16

# Font cache (loaded once, reused)
_font_cache = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """
    Get a font of specified size.
    Uses custom Star Wars font if available, falls back to system font.
    
    Args:
        size: Font size in pixels
        bold: Whether to use bold variant
        
    Returns:
        pygame.font.Font object
    """
    cache_key = (size, bold)
    
    # Return cached font if already loaded
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    
    # Try to load custom font (we'll add these later)
    custom_font_path = os.path.join(FONTS_DIR, "StarWars.ttf")
    
    try:
        if os.path.exists(custom_font_path):
            font = pygame.font.Font(custom_font_path, size)
        else:
            # Fallback to system font
            font = pygame.font.SysFont("arial", size, bold=bold)
    except:
        # If all else fails, use pygame default
        font = pygame.font.Font(None, size)
    
    # Cache it
    _font_cache[cache_key] = font
    return font


# Convenience functions for common fonts
def title_font() -> pygame.font.Font:
    """Large title font"""
    return get_font(TITLE_SIZE, bold=True)


def header_font() -> pygame.font.Font:
    """Section header font"""
    return get_font(HEADER_SIZE, bold=True)


def normal_font() -> pygame.font.Font:
    """Standard body text font"""
    return get_font(NORMAL_SIZE)


def small_font() -> pygame.font.Font:
    """Small text (tooltips, hints)"""
    return get_font(SMALL_SIZE)