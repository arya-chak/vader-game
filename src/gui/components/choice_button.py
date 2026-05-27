"""
ChoiceButton component for displaying and handling story choice selection.
Handles rendering, mouse/keyboard interaction, and visual feedback.
"""

import pygame
from typing import Tuple, Optional, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from gui.utils.text_utils import calculate_text_width, truncate_text


class ChoiceButton:
    """
    A component for displaying interactive story choices.
    Handles selection, hover states, and rendering with proper styling.
    """
    
    def __init__(self, x: int, y: int, choice_id: str, text: str,
                 font: pygame.font.Font,
                 normal_color: Tuple[int, int, int] = (0, 255, 255),
                 selected_color: Tuple[int, int, int] = (0, 255, 0),
                 hover_color: Tuple[int, int, int] = (0, 200, 255),
                 disabled_color: Tuple[int, int, int] = (100, 100, 100),
                 chevron: str = "▸",
                 padding: int = 10,
                 max_width: Optional[int] = None):
        """
        Initialize the ChoiceButton.
        
        Args:
            x: X position of choice button
            y: Y position of choice button
            choice_id: Unique identifier for this choice
            text: Display text for the choice
            font: Pygame font for rendering text
            normal_color: RGB color when not selected (default cyan)
            selected_color: RGB color when selected (default green)
            hover_color: RGB color when hovered (default light cyan)
            disabled_color: RGB color when disabled (default gray)
            chevron: Character to show before text (default "▸")
            padding: Padding around text in pixels (default 10)
            max_width: Maximum width for text wrapping (optional)
        """
        self.x = x
        self.y = y
        self.choice_id = choice_id
        self.text = text
        self.font = font
        
        # Colors
        self.normal_color = normal_color
        self.selected_color = selected_color
        self.hover_color = hover_color
        self.disabled_color = disabled_color
        self.chevron = chevron
        
        # State
        self.is_selected = False
        self.is_hovered = False
        self.is_enabled = True
        self.is_focused = False
        
        # Layout
        self.padding = padding
        self.max_width = max_width
        
        # Tags for choice modifiers (e.g., [DARK SIDE], [+10 Darkness])
        self.tags: List[Tuple[str, Tuple[int, int, int]]] = []
        
        # Calculate dimensions
        self._update_dimensions()
    
    def _update_dimensions(self) -> None:
        """Calculate button dimensions based on text and chevron."""
        chevron_width = self.font.size(self.chevron + " ")[0]
        text_width = self.font.size(self.text)[0]
        
        self.width = chevron_width + text_width + (self.padding * 2)
        self.height = self.font.get_linesize() + (self.padding * 2)
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the choice button to the surface.
        
        Args:
            surface: Pygame surface to draw to
        """
        # Determine color based on state
        if not self.is_enabled:
            current_color = self.disabled_color
        elif self.is_selected:
            current_color = self.selected_color
        elif self.is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.normal_color
        
        # Draw selection indicator bar (3px wide, 20px tall) to left of chevron
        if self.is_selected and self.is_enabled:
            bar_x = self.x + self.padding - 6
            bar_y = self.y + (self.height // 2) - 10
            pygame.draw.rect(surface, (255, 180, 0), (bar_x, bar_y, 3, 20))

        # Draw text
        text_x = self.x + self.padding
        text_y = self.y + (self.height // 2) - (self.font.get_linesize() // 2)
        text_surface = self.font.render(self.text, True, current_color)
        surface.blit(text_surface, (text_x, text_y))
        
        # Draw glow/highlight if selected
        if self.is_selected and self.is_enabled:
            self._draw_selection_glow(surface, current_color)
        
        # Draw tags if present
        if self.tags:
            self._draw_tags(surface)
    
    def _draw_selection_glow(self, surface: pygame.Surface,
                            color: Tuple[int, int, int]) -> None:
        """
        Draw a glow effect around selected button.
        
        Args:
            surface: Pygame surface to draw to
            color: Color to use for glow
        """
        # Create subtle glow with offset lines
        glow_color = (*color, 100)
        glow_surface = pygame.Surface((self.width + 4, self.height + 4),
                                      pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), 2)
        
        surface.blit(glow_surface, (self.x - 2, self.y - 2))
    
    def _draw_tags(self, surface: pygame.Surface) -> None:
        """
        Draw choice modifier tags (e.g., [DARK SIDE]).
        
        Args:
            surface: Pygame surface to draw to
        """
        tag_font = pygame.font.SysFont('arial', 12)
        tag_y = self.y - 20  # Above the choice
        tag_x = self.x + self.padding
        
        for tag_text, tag_color in self.tags:
            tag_surface = tag_font.render(tag_text, True, tag_color)
            surface.blit(tag_surface, (tag_x, tag_y))
            tag_x += tag_surface.get_width() + 10
    
    def set_selected(self, selected: bool) -> None:
        """
        Set whether this button is selected.
        
        Args:
            selected: True if selected
        """
        self.is_selected = selected
    
    def set_hovered(self, hovered: bool) -> None:
        """
        Set whether this button is hovered (mouse over).
        
        Args:
            hovered: True if hovered
        """
        self.is_hovered = hovered
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Set whether this button is enabled/disabled.
        
        Args:
            enabled: True if enabled
        """
        self.is_enabled = enabled
    
    def set_focused(self, focused: bool) -> None:
        """
        Set keyboard focus state.
        
        Args:
            focused: True if focused
        """
        self.is_focused = focused
    
    def set_position(self, x: int, y: int) -> None:
        """
        Set the position of the button.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
    def set_text(self, text: str) -> None:
        """
        Set the button text.
        
        Args:
            text: New text
        """
        self.text = text
        self._update_dimensions()
    
    def add_tag(self, tag_text: str,
                tag_color: Tuple[int, int, int] = (255, 200, 0)) -> None:
        """
        Add a modifier tag to the choice (e.g., [DARK SIDE]).
        
        Args:
            tag_text: Tag text to display
            tag_color: RGB color for tag
        """
        self.tags.append((tag_text, tag_color))
    
    def clear_tags(self) -> None:
        """Remove all tags from this choice."""
        self.tags = []
    
    def set_tags(self, tags: List[Tuple[str, Tuple[int, int, int]]]) -> None:
        """
        Set tags for this choice.
        
        Args:
            tags: List of (tag_text, color) tuples
        """
        self.tags = tags
    
    def collidepoint(self, pos: Tuple[int, int]) -> bool:
        """
        Check if a point collides with the button.
        
        Args:
            pos: (x, y) position tuple
        
        Returns:
            True if point is within button area
        """
        return self.rect.collidepoint(pos)
    
    def get_rect(self) -> pygame.Rect:
        """
        Get the button's rectangle.
        
        Returns:
            Pygame Rect object
        """
        return self.rect.copy()
    
    def update(self, dt: float) -> None:
        """
        Update button state (for animations).
        
        Args:
            dt: Delta time in seconds
        """
        # For Phase 1, minimal update
        # In Phase 2+, could add glow pulsing or hover animations
        pass
    
    def get_choice_id(self) -> str:
        """
        Get the choice ID.
        
        Returns:
            The unique choice identifier
        """
        return self.choice_id
    
    def get_text(self) -> str:
        """
        Get the button text.
        
        Returns:
            The display text
        """
        return self.text
    
    def is_clickable(self) -> bool:
        """
        Check if button is clickable (enabled and not disabled).
        
        Returns:
            True if button can be clicked
        """
        return self.is_enabled
    
    def get_state(self) -> dict:
        """
        Get the complete state of the button.
        
        Returns:
            Dictionary with button state information
        """
        return {
            'id': self.choice_id,
            'text': self.text,
            'selected': self.is_selected,
            'hovered': self.is_hovered,
            'enabled': self.is_enabled,
            'tags': self.tags
        }
    
    def set_colors(self, normal: Tuple[int, int, int],
                   selected: Tuple[int, int, int],
                   hover: Tuple[int, int, int],
                   disabled: Tuple[int, int, int]) -> None:
        """
        Set all button colors at once.
        
        Args:
            normal: Color when normal
            selected: Color when selected
            hover: Color when hovered
            disabled: Color when disabled
        """
        self.normal_color = normal
        self.selected_color = selected
        self.hover_color = hover
        self.disabled_color = disabled