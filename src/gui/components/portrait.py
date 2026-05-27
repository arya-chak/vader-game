"""
Portrait component for displaying character portrait images.
Handles image loading, positioning, and visual styling with borders and glows.
"""

import pygame
from typing import Tuple, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class Portrait:
    """
    A component for displaying character portrait images.
    Supports loading images, borders, glows, and positioning.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 image_path: Optional[str] = None,
                 border_color: Tuple[int, int, int] = (0, 255, 255),
                 border_width: int = 3,
                 show_border: bool = True,
                 glow_color: Tuple[int, int, int] = (0, 255, 255),
                 glow_width: int = 5):
        """
        Initialize the Portrait component.
        
        Args:
            x: X position of portrait
            y: Y position of portrait
            width: Width of portrait area
            height: Height of portrait area
            image_path: Path to portrait image (optional)
            border_color: RGB color for border (default cyan)
            border_width: Width of border in pixels (default 3)
            show_border: Whether to draw border (default True)
            glow_color: RGB color for glow effect (default cyan)
            glow_width: Width of glow effect (default 5)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Border and styling
        self.border_color = border_color
        self.border_width = border_width
        self.show_border = show_border
        self.glow_color = glow_color
        self.glow_width = glow_width
        
        # Image
        self.image = None
        self.original_image = None
        self.image_path = image_path
        
        # State
        self.is_speaking = False
        self.glow_active = False
        self.glow_intensity = 0.0
        self.glow_pulse_speed = 2.0  # For future animation
        
        # Rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Load image if provided
        if image_path:
            self.load_image(image_path)
    
    def load_image(self, image_path: str) -> bool:
        """
        Load a portrait image from file.
        
        Args:
            image_path: Path to image file
        
        Returns:
            True if image loaded successfully, False otherwise
        """
        try:
            # Try to load the image
            image = pygame.image.load(image_path)
            
            # Store original for reference
            self.original_image = image
            
            # Scale to fit portrait dimensions
            self.image = pygame.transform.scale(image, (self.width, self.height))
            self.image_path = image_path
            
            return True
        except pygame.error as e:
            print(f"Error loading portrait image '{image_path}': {e}")
            self.image = None
            self.original_image = None
            return False
        except FileNotFoundError:
            print(f"Portrait image not found: {image_path}")
            self.image = None
            self.original_image = None
            return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the portrait to the surface.
        
        Args:
            surface: Pygame surface to draw to
        """
        # Draw glow effect if active
        if self.glow_active:
            self._draw_glow(surface)
        
        # Draw the portrait image if loaded
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            # Draw placeholder if no image
            self._draw_placeholder(surface)
        
        # Draw border
        if self.show_border:
            self._draw_border(surface)
    
    def _draw_glow(self, surface: pygame.Surface) -> None:
        """
        Draw glow effect around the portrait.
        
        Args:
            surface: Pygame surface to draw to
        """
        # Create a glow surface with transparency
        glow_surface = pygame.Surface(
            (self.width + self.glow_width * 2, 
             self.height + self.glow_width * 2),
            pygame.SRCALPHA
        )
        
        # Draw glow rectangle with semi-transparent color
        glow_color_with_alpha = (*self.glow_color, int(100 * self.glow_intensity))
        pygame.draw.rect(
            glow_surface,
            glow_color_with_alpha,
            glow_surface.get_rect(),
            self.glow_width
        )
        
        # Blit glow surface to main surface
        glow_x = self.x - self.glow_width
        glow_y = self.y - self.glow_width
        surface.blit(glow_surface, (glow_x, glow_y))
    
    def _draw_border(self, surface: pygame.Surface) -> None:
        """
        Draw border around the portrait.
        
        Args:
            surface: Pygame surface to draw to
        """
        pygame.draw.rect(
            surface,
            self.border_color,
            self.rect,
            self.border_width
        )
    
    def _draw_placeholder(self, surface: pygame.Surface) -> None:
        """
        Draw a placeholder rectangle if no image is loaded.
        
        Args:
            surface: Pygame surface to draw to
        """
        # Draw a dark gray background
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        
        # Draw text "NO IMAGE"
        font = pygame.font.SysFont('arial', 14)
        text_surface = font.render("NO IMAGE", True, (150, 150, 150))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def set_speaking(self, is_speaking: bool) -> None:
        """
        Set whether this portrait is currently speaking.
        Shows glow effect when speaking.
        
        Args:
            is_speaking: True if this character is speaking
        """
        self.is_speaking = is_speaking
        self.glow_active = is_speaking
        self.glow_intensity = 1.0 if is_speaking else 0.0
    
    def set_glow(self, active: bool, intensity: float = 1.0) -> None:
        """
        Set glow effect state.
        
        Args:
            active: Whether glow is active
            intensity: Glow intensity (0.0 to 1.0)
        """
        self.glow_active = active
        self.glow_intensity = max(0.0, min(1.0, intensity))
    
    def set_position(self, x: int, y: int) -> None:
        """
        Set the position of the portrait.
        
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
        Set the dimensions of the portrait.
        Rescales image if loaded.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
        self.rect.width = width
        self.rect.height = height
        
        # Rescale image if loaded
        if self.original_image:
            self.image = pygame.transform.scale(self.original_image, 
                                               (self.width, self.height))
    
    def set_border_color(self, color: Tuple[int, int, int]) -> None:
        """
        Set the border color.
        
        Args:
            color: RGB color tuple
        """
        self.border_color = color
    
    def set_glow_color(self, color: Tuple[int, int, int]) -> None:
        """
        Set the glow color.
        
        Args:
            color: RGB color tuple
        """
        self.glow_color = color
    
    def set_border_visibility(self, visible: bool) -> None:
        """
        Set whether to draw the border.
        
        Args:
            visible: True to show border, False to hide
        """
        self.show_border = visible
    
    def collidepoint(self, pos: Tuple[int, int]) -> bool:
        """
        Check if a point collides with the portrait.
        
        Args:
            pos: (x, y) position tuple
        
        Returns:
            True if point is within portrait area
        """
        return self.rect.collidepoint(pos)
    
    def update(self, dt: float) -> None:
        """
        Update portrait state (for animations).
        
        Args:
            dt: Delta time in seconds
        """
        # For Phase 1, minimal update
        # In Phase 2, could add glow pulsing animation
        pass
    
    def has_image(self) -> bool:
        """
        Check if portrait has a loaded image.
        
        Returns:
            True if image is loaded
        """
        return self.image is not None
    
    def get_image_path(self) -> Optional[str]:
        """
        Get the path of the loaded image.
        
        Returns:
            Path to image or None if not loaded
        """
        return self.image_path
    
    def clear_image(self) -> None:
        """Clear the portrait image."""
        self.image = None
        self.original_image = None
        self.image_path = None
        self.is_speaking = False
        self.glow_active = False
    
    def get_rect(self) -> pygame.Rect:
        """
        Get the rectangle of the portrait.
        
        Returns:
            Pygame Rect object
        """
        return self.rect.copy()