# """
# Text box component for displaying dialogue and story text.
# Handles word wrapping, character names, and scrolling text.
# """

# import pygame
# from ..utils import TEXT_BOX_BG, TEXT_BOX_BORDER, WHITE, GRAY, normal_font, small_font


# class TextBox:
#     """
#     A box for displaying story text, dialogue, and narration.
#     Supports word wrapping and character names.
#     """
    
#     def __init__(self, x: int, y: int, width: int, height: int):
#         """
#         Initialize text box.
        
#         Args:
#             x, y: Position
#             width, height: Size
#         """
#         self.rect = pygame.Rect(x, y, width, height)
#         self.padding = 15  # Inner padding
        
#         # Text content
#         self.lines = []  # List of rendered text surfaces
#         self.speaker = None  # Character name (e.g., "Vader", "Palpatine")
        
#     def set_text(self, text: str, speaker: str = None):
#         """
#         Set the text to display with word wrapping.
        
#         Args:
#             text: The text to display
#             speaker: Optional character name
#         """
#         self.speaker = speaker
#         self.lines = []
        
#         font = normal_font()
#         words = text.split(' ')
        
#         # Word wrapping
#         current_line = ""
#         max_width = self.rect.width - (self.padding * 2)
        
#         for word in words:
#             test_line = current_line + word + " "
#             test_surface = font.render(test_line, True, WHITE)
            
#             if test_surface.get_width() <= max_width:
#                 current_line = test_line
#             else:
#                 # Line is full, save it and start new line
#                 if current_line:
#                     self.lines.append(font.render(current_line.strip(), True, WHITE))
#                 current_line = word + " "
        
#         # Add last line
#         if current_line:
#             self.lines.append(font.render(current_line.strip(), True, WHITE))
    
#     def render(self, surface: pygame.Surface):
#         """Draw the text box"""
#         # Draw background
#         pygame.draw.rect(surface, TEXT_BOX_BG, self.rect)
#         pygame.draw.rect(surface, TEXT_BOX_BORDER, self.rect, 2)  # Border
        
#         # Draw speaker name if present
#         y_offset = self.rect.y + self.padding
        
#         if self.speaker:
#             speaker_font = small_font()
#             speaker_text = speaker_font.render(f"{self.speaker}:", True, GRAY)
#             surface.blit(speaker_text, (self.rect.x + self.padding, y_offset))
#             y_offset += speaker_text.get_height() + 10  # Space after name
        
#         # Draw text lines
#         for line_surface in self.lines:
#             if y_offset + line_surface.get_height() > self.rect.bottom - self.padding:
#                 break  # Don't draw beyond box
            
#             surface.blit(line_surface, (self.rect.x + self.padding, y_offset))
#             y_offset += line_surface.get_height() + 5  # Line spacing