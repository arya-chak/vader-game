"""
Choice button component for story decisions.
Displays choices with hover effects and tags like [RAGE], [CONTROL], etc.
"""

import pygame
from ..utils import (
    BUTTON_NORMAL, BUTTON_HOVER, BUTTON_PRESSED, WHITE, TEXT_BOX_BORDER,
    CHOICE_RAGE, CHOICE_CONTROL, CHOICE_DARK, CHOICE_SUPPRESS,
    normal_font, small_font
)


class ChoiceButton:
    """
    A clickable button for story choices.
    Shows hover effects and choice tags.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, choice_id: str, tag: str = None):
        """
        Initialize a choice button.
        
        Args:
            x, y: Position
            width, height: Size
            text: Button text (the actual choice)
            choice_id: Unique identifier for this choice
            tag: Optional tag like "RAGE", "CONTROL", "DARK SIDE", "SUPPRESS"
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.choice_id = choice_id
        self.tag = tag
        
        # State
        self.hovered = False
        self.pressed = False
        
        # Colors based on tag
        self.tag_color = self._get_tag_color(tag)
        
    def _get_tag_color(self, tag: str):
        """Get color based on choice tag"""
        if not tag:
            return WHITE
        
        tag_upper = tag.upper()
        if "RAGE" in tag_upper:
            return CHOICE_RAGE
        elif "CONTROL" in tag_upper:
            return CHOICE_CONTROL
        elif "DARK" in tag_upper:
            return CHOICE_DARK
        elif "SUPPRESS" in tag_upper:
            return CHOICE_SUPPRESS
        else:
            return WHITE
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events.
        
        Returns:
            True if button was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.pressed = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.hovered:
                self.pressed = False
                return True  # Button was clicked!
            self.pressed = False
        
        return False
    
    def render(self, surface: pygame.Surface):
        """Draw the button"""
        # Choose color based on state
        if self.pressed:
            bg_color = BUTTON_PRESSED
        elif self.hovered:
            bg_color = BUTTON_HOVER
        else:
            bg_color = BUTTON_NORMAL
        
        # Draw background
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, TEXT_BOX_BORDER, self.rect, 2)  # Border
        
        # Draw tag if present (e.g., [RAGE])
        if self.tag:
            tag_font = small_font()
            tag_text = tag_font.render(f"[{self.tag.upper()}]", True, self.tag_color)
            tag_rect = tag_text.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
            surface.blit(tag_text, tag_rect)
            
            # Main text offset after tag
            text_x = tag_rect.right + 10
        else:
            text_x = self.rect.x + 10
        
        # Draw main text
        font = normal_font()
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(midleft=(text_x, self.rect.centery))
        surface.blit(text_surface, text_rect)