"""
Text utilities for dialogue and UI text rendering.
Provides functions for text wrapping, sizing, and formatting.
"""

import pygame
from typing import List, Tuple


def wrap_text(text: str, max_width: int, font: pygame.font.Font) -> str:
    """
    Wrap text to fit within a maximum width.
    
    Args:
        text: The text to wrap
        max_width: Maximum width in pixels
        font: Pygame font object for measuring text
    
    Returns:
        Text with newlines inserted for proper wrapping
    """
    if not text:
        return text
    
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        # Test if adding this word would exceed max_width
        test_line = ' '.join(current_line + [word])
        text_width = font.size(test_line)[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            # Word doesn't fit, save current line and start new one
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add remaining line
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def split_into_lines(text: str, max_width: int, font: pygame.font.Font) -> List[str]:
    """
    Split text into lines that fit within max_width.
    
    Args:
        text: The text to split
        max_width: Maximum width in pixels
        font: Pygame font object for measuring text
    
    Returns:
        List of text lines
    """
    wrapped = wrap_text(text, max_width, font)
    return wrapped.split('\n')


def calculate_text_height(text: str, font: pygame.font.Font, 
                         max_width: int = None, line_spacing: float = 1.4) -> int:
    """
    Calculate the total height of rendered text.
    
    Args:
        text: The text to measure
        font: Pygame font object
        max_width: Maximum width for wrapping (None = single line)
        line_spacing: Multiplier for space between lines (default 1.4)
    
    Returns:
        Height in pixels
    """
    line_height = font.get_linesize()
    
    if max_width is None:
        # Single line
        return line_height
    
    # Multiple lines with wrapping
    lines = split_into_lines(text, max_width, font)
    total_height = int(line_height * len(lines) * line_spacing)
    
    return total_height


def calculate_text_width(text: str, font: pygame.font.Font) -> int:
    """
    Calculate the width of rendered text.
    
    Args:
        text: The text to measure
        font: Pygame font object
    
    Returns:
        Width in pixels
    """
    return font.size(text)[0]


def get_line_height(font: pygame.font.Font, line_spacing: float = 1.4) -> int:
    """
    Get the height of a single line of text with spacing.
    
    Args:
        font: Pygame font object
        line_spacing: Multiplier for space between lines
    
    Returns:
        Height in pixels
    """
    return int(font.get_linesize() * line_spacing)


def format_dialogue(speaker: str, text: str) -> str:
    """
    Format dialogue with speaker name.
    
    Args:
        speaker: Character name
        text: Dialogue text
    
    Returns:
        Formatted string (just returns the dialogue, speaker handled separately)
    """
    return text


def split_dialogue_into_pages(text: str, max_width: int, max_height: int,
                             font: pygame.font.Font, 
                             line_spacing: float = 1.4) -> List[str]:
    """
    Split long dialogue into multiple pages based on max dimensions.
    Useful for dialogue that's too long to fit on screen.
    
    Args:
        text: The dialogue text
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        font: Pygame font object
        line_spacing: Multiplier for space between lines
    
    Returns:
        List of text chunks, each fitting within max dimensions
    """
    lines = split_into_lines(text, max_width, font)
    line_height = get_line_height(font, line_spacing)
    
    # Calculate how many lines fit in max_height
    max_lines_per_page = max(1, max_height // line_height)
    
    pages = []
    current_page = []
    
    for line in lines:
        current_page.append(line)
        
        if len(current_page) >= max_lines_per_page:
            pages.append('\n'.join(current_page))
            current_page = []
    
    # Add remaining lines
    if current_page:
        pages.append('\n'.join(current_page))
    
    return pages


def center_text(text: str, x: int, y: int, font: pygame.font.Font,
               surface_width: int = None) -> Tuple[int, int]:
    """
    Calculate position to center text horizontally.
    
    Args:
        text: The text to center
        x: Reference x position (usually center of surface)
        y: Y position
        font: Pygame font object
        surface_width: Width of surface (optional, for bounds checking)
    
    Returns:
        Tuple of (adjusted_x, y) for rendering
    """
    text_width = calculate_text_width(text, font)
    adjusted_x = x - (text_width // 2)
    
    return adjusted_x, y


def truncate_text(text: str, max_width: int, font: pygame.font.Font,
                 suffix: str = "...") -> str:
    """
    Truncate text to fit within max_width, adding suffix if truncated.
    
    Args:
        text: The text to truncate
        max_width: Maximum width in pixels
        font: Pygame font object
        suffix: Text to add if truncated (default "...")
    
    Returns:
        Truncated text or original if it fits
    """
    if font.size(text)[0] <= max_width:
        return text
    
    # Find where to truncate
    for i in range(len(text), 0, -1):
        truncated = text[:i] + suffix
        if font.size(truncated)[0] <= max_width:
            return truncated
    
    return suffix


def render_wrapped_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                       color: Tuple[int, int, int], x: int, y: int,
                       max_width: int, line_spacing: float = 1.4) -> int:
    """
    Render wrapped text to a surface.
    
    Args:
        surface: Pygame surface to render to
        text: The text to render
        font: Pygame font object
        color: RGB color tuple
        x: X position
        y: Y position
        max_width: Maximum width for wrapping
        line_spacing: Multiplier for space between lines
    
    Returns:
        Total height of rendered text
    """
    lines = split_into_lines(text, max_width, font)
    line_height = get_line_height(font, line_spacing)
    
    current_y = y
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, current_y))
        current_y += line_height
    
    return current_y - y


def count_words(text: str) -> int:
    """
    Count the number of words in text.
    
    Args:
        text: The text to count
    
    Returns:
        Number of words
    """
    return len(text.split())


def estimate_reading_time(text: str, words_per_minute: int = 200) -> float:
    """
    Estimate how long it takes to read text (in seconds).
    
    Args:
        text: The text to measure
        words_per_minute: Average reading speed (default 200)
    
    Returns:
        Estimated reading time in seconds
    """
    word_count = count_words(text)
    return (word_count / words_per_minute) * 60