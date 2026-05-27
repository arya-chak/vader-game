"""
DialogueBox component for displaying dialogue text with speaker names.
Handles text rendering, positioning, and visual styling.
"""

import pygame
from typing import Tuple, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from gui.utils.text_utils import (
    wrap_text, split_into_lines, calculate_text_height, 
    get_line_height, render_wrapped_text
)


class DialogueBox:
    """
    A component for displaying dialogue text with speaker name.
    Renders wrapped text with proper spacing and formatting.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 dialogue_font: pygame.font.Font,
                 speaker_font: pygame.font.Font,
                 dialogue_color: Tuple[int, int, int] = (255, 255, 255),
                 speaker_color: Tuple[int, int, int] = (255, 170, 0),
                 line_spacing: float = 1.4,
                 padding: int = 20):
        """
        Initialize the DialogueBox.
        
        Args:
            x: X position of dialogue box
            y: Y position of dialogue box
            width: Width of dialogue box content area
            height: Height of dialogue box content area
            dialogue_font: Pygame font for dialogue text
            speaker_font: Pygame font for speaker name
            dialogue_color: RGB color for dialogue text (default white)
            speaker_color: RGB color for speaker name (default gold)
            line_spacing: Multiplier for space between lines (default 1.4)
            padding: Padding inside the box (default 20px)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = padding
        
        # Fonts and colors
        self.dialogue_font = dialogue_font
        self.speaker_font = speaker_font
        self.dialogue_color = dialogue_color
        self.speaker_color = speaker_color
        self.line_spacing = line_spacing
        
        # Content
        self.speaker_name = ""
        self.dialogue_text = ""
        self.wrapped_dialogue = ""
        self.lines = []
        
        # Animation state
        self.is_complete = False
        
        # Rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def set_dialogue(self, speaker: str, text: str) -> None:
        """
        Set the dialogue content.
        
        Args:
            speaker: Name of the speaking character
            text: The dialogue text
        """
        self.speaker_name = speaker.upper() if speaker else ""
        self.dialogue_text = text
        
        # Calculate available width for text (accounting for padding)
        text_width = self.width - (self.padding * 2)
        
        # Wrap the dialogue text
        self.wrapped_dialogue = wrap_text(self.dialogue_text, text_width, 
                                         self.dialogue_font)
        self.lines = self.wrapped_dialogue.split('\n')
        
        self.is_complete = True
    
    def get_dialogue_height(self) -> int:
        """
        Calculate the height needed to display current dialogue.
        
        Returns:
            Height in pixels
        """
        if not self.dialogue_text:
            return 0
        
        text_width = self.width - (self.padding * 2)
        line_height = get_line_height(self.dialogue_font, self.line_spacing)
        
        # Height = number of lines * line height
        num_lines = len(self.lines)
        dialogue_height = num_lines * line_height
        
        # Add space for speaker name if present
        if self.speaker_name:
            dialogue_height += line_height + self.padding
        
        return dialogue_height
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the dialogue box and its contents to the surface.
        
        Args:
            surface: Pygame surface to draw to
        """
        if not self.dialogue_text:
            return
        
        current_y = self.y + self.padding
        line_height = get_line_height(self.dialogue_font, self.line_spacing)
        text_x = self.x + self.padding
        
        # Draw dialogue lines
        for line in self.lines:
            text_surface = self.dialogue_font.render(line, True, self.dialogue_color)
            surface.blit(text_surface, (text_x, current_y))
            current_y += line_height
        
        # Draw speaker name below dialogue
        if self.speaker_name:
            current_y += self.padding
            speaker_surface = self.speaker_font.render(self.speaker_name, True, 
                                                       self.speaker_color)
            surface.blit(speaker_surface, (text_x, current_y))
    
    def clear(self) -> None:
        """Clear the dialogue box content."""
        self.speaker_name = ""
        self.dialogue_text = ""
        self.wrapped_dialogue = ""
        self.lines = []
        self.is_complete = False
    
    def collidepoint(self, pos: Tuple[int, int]) -> bool:
        """
        Check if a point collides with the dialogue box area.
        
        Args:
            pos: (x, y) position tuple
        
        Returns:
            True if point is within dialogue box
        """
        return self.rect.collidepoint(pos)
    
    def update(self, dt: float) -> None:
        """
        Update dialogue box state.
        
        Args:
            dt: Delta time in seconds
        """
        # For Phase 1, not much to update
        # In Phase 2, this will handle typing animation
        pass
    
    def get_text_content(self) -> Tuple[str, str]:
        """
        Get the current dialogue content.
        
        Returns:
            Tuple of (speaker_name, dialogue_text)
        """
        return self.speaker_name, self.dialogue_text
    
    def set_position(self, x: int, y: int) -> None:
        """
        Set the position of the dialogue box.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
    def set_dimensions(self, width: int, height: int) -> None:
        """
        Set the dimensions of the dialogue box.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
        self.rect.width = width
        self.rect.height = height
        
        # Re-wrap dialogue if it exists
        if self.dialogue_text:
            text_width = self.width - (self.padding * 2)
            self.wrapped_dialogue = wrap_text(self.dialogue_text, text_width,
                                             self.dialogue_font)
            self.lines = self.wrapped_dialogue.split('\n')
    
    def set_colors(self, dialogue_color: Tuple[int, int, int],
                   speaker_color: Tuple[int, int, int]) -> None:
        """
        Set the text colors.
        
        Args:
            dialogue_color: RGB tuple for dialogue text
            speaker_color: RGB tuple for speaker name
        """
        self.dialogue_color = dialogue_color
        self.speaker_color = speaker_color
    
    def is_empty(self) -> bool:
        """
        Check if the dialogue box is empty.
        
        Returns:
            True if no dialogue is set
        """
        return not self.dialogue_text
    
    def get_line_count(self) -> int:
        """
        Get the number of lines in the current dialogue.
        
        Returns:
            Number of lines
        """
        return len(self.lines)