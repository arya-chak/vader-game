"""
GUI utilities module.
Provides colors, fonts, and helper functions for the GUI.
"""

from .colors import *
from .fonts import get_font, title_font, header_font, normal_font, small_font

__all__ = [
    # Colors (all exported from colors.py)
    'BLACK', 'WHITE', 'DARK_GRAY', 'GRAY', 'LIGHT_GRAY',
    'IMPERIAL_RED', 'IMPERIAL_BLUE', 'VADER_BLACK',
    'FORCE_BLUE', 'SITH_RED', 'KYBER_CRIMSON',
    'HEALTH_GREEN', 'HEALTH_YELLOW', 'HEALTH_RED',
    'BUTTON_NORMAL', 'BUTTON_HOVER', 'BUTTON_PRESSED',
    'TEXT_BOX_BG', 'TEXT_BOX_BORDER',
    'CHOICE_RAGE', 'CHOICE_CONTROL', 'CHOICE_DARK', 'CHOICE_SUPPRESS',
    'TRANSPARENT', 'SEMI_TRANSPARENT_BLACK',
    
    # Fonts
    'get_font', 'title_font', 'header_font', 'normal_font', 'small_font'
]