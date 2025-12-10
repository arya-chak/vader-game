# """
# Health/status bar component.
# Displays HP, Force Points, Suit Integrity, etc. with color-coded bars.
# """

# import pygame
# from ..utils import (
#     HEALTH_GREEN, HEALTH_YELLOW, HEALTH_RED,
#     FORCE_BLUE, SITH_RED,
#     BLACK, WHITE, GRAY, TEXT_BOX_BORDER,
#     small_font
# )


# class HealthBar:
#     """
#     A status bar that shows current/max values with color coding.
#     Used for HP, FP, Suit Integrity, etc.
#     """
    
#     def __init__(self, x: int, y: int, width: int, height: int, label: str, bar_color=HEALTH_GREEN):
#         """
#         Initialize a health/status bar.
        
#         Args:
#             x, y: Position
#             width, height: Size of the bar
#             label: Text label (e.g., "HP", "FP", "Suit")
#             bar_color: Default bar color (can change based on percentage)
#         """
#         self.rect = pygame.Rect(x, y, width, height)
#         self.label = label
#         self.default_color = bar_color
        
#         # Values
#         self.current = 100
#         self.maximum = 100
        
#     def set_value(self, current: int, maximum: int):
#         """Update the bar's current and maximum values"""
#         self.current = max(0, current)
#         self.maximum = max(1, maximum)  # Avoid division by zero
    
#     def get_percentage(self) -> float:
#         """Get current value as percentage (0.0 to 1.0)"""
#         return self.current / self.maximum
    
#     def get_bar_color(self) -> tuple:
#         """
#         Get bar color based on percentage.
#         For HP: Green > 50%, Yellow 25-50%, Red < 25%
#         For other bars: Use default color
#         """
#         if self.label == "HP":
#             percentage = self.get_percentage()
#             if percentage > 0.5:
#                 return HEALTH_GREEN
#             elif percentage > 0.25:
#                 return HEALTH_YELLOW
#             else:
#                 return HEALTH_RED
#         elif self.label == "FP":
#             return FORCE_BLUE
#         elif self.label == "Suit":
#             return GRAY
#         else:
#             return self.default_color
    
#     def render(self, surface: pygame.Surface):
#         """Draw the status bar"""
#         # Draw label
#         font = small_font()
#         label_text = font.render(self.label, True, WHITE)
#         label_rect = label_text.get_rect(midright=(self.rect.x - 5, self.rect.centery))
#         surface.blit(label_text, label_rect)
        
#         # Draw bar background (empty bar)
#         pygame.draw.rect(surface, BLACK, self.rect)
#         pygame.draw.rect(surface, TEXT_BOX_BORDER, self.rect, 1)  # Border
        
#         # Draw filled portion
#         fill_width = int(self.rect.width * self.get_percentage())
#         if fill_width > 0:
#             fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
#             pygame.draw.rect(surface, self.get_bar_color(), fill_rect)
        
#         # Draw text showing values (e.g., "150/200")
#         value_text = font.render(f"{self.current}/{self.maximum}", True, WHITE)
#         value_rect = value_text.get_rect(center=self.rect.center)
#         surface.blit(value_text, value_rect)