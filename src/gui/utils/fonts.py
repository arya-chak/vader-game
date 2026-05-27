"""
Font definitions for Darth Vader RPG GUI.
Centralized font management for consistent typography across all screens.
"""

import pygame
import os
from typing import Optional

# Get the path to the fonts directory
FONTS_DIR = os.path.join(os.path.dirname(__file__), 'fonts')

# Font file paths
SF_DISTANT_GALAXY_PATH = os.path.join(FONTS_DIR, 'SfDistantGalaxyAlternateItalic-3RDM.ttf')
IMPERIAL_CODE_PATH = os.path.join(FONTS_DIR, 'ImperialCode-VGXpx.ttf')

# Font size constants
SIZE_SMALL = 12
SIZE_REGULAR = 16
SIZE_MEDIUM = 18
SIZE_LARGE = 24
SIZE_TITLE = 48
SIZE_HUGE = 64

# System fonts (always available)
ARIAL_BOLD = 'arial bold'
TIMES_NEW_ROMAN = 'times new roman'
COURIER_NEW = 'courier new'

# Font instances - These are created on demand to avoid initialization issues
_font_cache = {}


def get_font(font_name: str, size: int) -> pygame.font.Font:
    """
    Get a font instance, using cache to avoid recreating fonts.
    
    Args:
        font_name: Name of font (e.g., 'times new roman', 'arial')
        size: Font size in pixels
    
    Returns:
        Pygame font object
    """
    cache_key = (font_name, size)
    
    if cache_key not in _font_cache:
        _font_cache[cache_key] = pygame.font.SysFont(font_name, size)
    
    return _font_cache[cache_key]


def get_title_font(size: int = SIZE_TITLE) -> pygame.font.Font:
    """
    Get SF Distant Galaxy font (Star Wars style).
    Falls back to Arial Bold if file not found.
    
    Args:
        size: Font size in pixels
    
    Returns:
        Pygame font object
    """
    cache_key = ('title', size)
    
    if cache_key not in _font_cache:
        try:
            _font_cache[cache_key] = pygame.font.Font(SF_DISTANT_GALAXY_PATH, size)
        except (pygame.error, FileNotFoundError):
            # Fallback to system font
            _font_cache[cache_key] = pygame.font.SysFont(ARIAL_BOLD, size, bold=True)
    
    return _font_cache[cache_key]


def get_dialogue_font(size: int = SIZE_MEDIUM) -> pygame.font.Font:
    """
    Get Times New Roman font for dialogue text.
    Uses system font for consistent availability.
    
    Args:
        size: Font size in pixels (default 18)
    
    Returns:
        Pygame font object
    """
    return get_font(TIMES_NEW_ROMAN, size)


def get_speaker_font(size: int = SIZE_REGULAR) -> pygame.font.Font:
    """
    Get Times New Roman bold font for speaker names.
    
    Args:
        size: Font size in pixels (default 16)
    
    Returns:
        Pygame font object (bold)
    """
    cache_key = ('speaker', size)
    
    if cache_key not in _font_cache:
        _font_cache[cache_key] = pygame.font.SysFont(TIMES_NEW_ROMAN, size, bold=True)
    
    return _font_cache[cache_key]


def get_choice_font(size: int = SIZE_REGULAR) -> pygame.font.Font:
    """
    Get Times New Roman font for choice text.
    
    Args:
        size: Font size in pixels (default 16)
    
    Returns:
        Pygame font object
    """
    return get_font(TIMES_NEW_ROMAN, size)


def get_imperial_code_font(size: int = SIZE_MEDIUM) -> pygame.font.Font:
    """
    Get ImperialCode font (Aurebesh-inspired).
    Falls back to Arial if file not found.
    
    Args:
        size: Font size in pixels
    
    Returns:
        Pygame font object
    """
    cache_key = ('imperial', size)
    
    if cache_key not in _font_cache:
        try:
            _font_cache[cache_key] = pygame.font.Font(IMPERIAL_CODE_PATH, size)
        except (pygame.error, FileNotFoundError):
            # Fallback to Arial
            _font_cache[cache_key] = pygame.font.SysFont('arial', size)
    
    return _font_cache[cache_key]


def get_menu_title_font(size: int = SIZE_HUGE) -> pygame.font.Font:
    """
    Get font for main menu titles.
    Uses SF Distant Galaxy with fallback.
    
    Args:
        size: Font size in pixels (default 64)
    
    Returns:
        Pygame font object
    """
    return get_title_font(size)


def get_menu_option_font(size: int = SIZE_MEDIUM) -> pygame.font.Font:
    """
    Get font for main menu options.
    Uses ImperialCode with fallback.
    
    Args:
        size: Font size in pixels (default 18)
    
    Returns:
        Pygame font object
    """
    return get_imperial_code_font(size)


def clear_font_cache() -> None:
    """Clear the font cache. Use if you need to reload fonts."""
    global _font_cache
    _font_cache.clear()


# Pre-load commonly used fonts for performance
# These will be created on first get_* call, not at module import
def preload_common_fonts() -> None:
    """
    Preload commonly used font sizes to improve performance.
    Call this during game initialization.
    """
    get_dialogue_font(SIZE_MEDIUM)  # 18px dialogue
    get_speaker_font(SIZE_REGULAR)  # 16px speaker
    get_choice_font(SIZE_REGULAR)   # 16px choices
    get_title_font(SIZE_TITLE)      # 48px titles
    get_title_font(SIZE_HUGE)       # 64px huge titles