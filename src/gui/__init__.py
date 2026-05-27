"""
GUI Module for Darth Vader RPG
Handles all graphical interface components using Pygame.
"""

try:
    from .game_window import GameWindow
    __all__ = ['GameWindow']
except ImportError:
    pass