"""
Main menu screen.
Shows title and menu options: New Game, Continue, Quit.
"""

import pygame
from ..utils import (
    BLACK, WHITE, SITH_RED, IMPERIAL_RED,
    title_font, header_font, normal_font
)
from ..components import ChoiceButton


class MainMenuScreen:
    """
    Main menu screen with title and menu buttons.
    """
    
    def __init__(self, window):
        """
        Initialize main menu.
        
        Args:
            window: GameWindow instance
        """
        self.window = window
        self.width = window.width
        self.height = window.height
        
        # Menu buttons
        button_width = 400
        button_height = 60
        button_x = (self.width - button_width) // 2
        start_y = self.height // 2 + 50
        
        self.buttons = [
            ChoiceButton(
                button_x, start_y,
                button_width, button_height,
                "New Game", "new_game"
            ),
            ChoiceButton(
                button_x, start_y + 80,
                button_width, button_height,
                "Continue", "continue"
            ),
            ChoiceButton(
                button_x, start_y + 160,
                button_width, button_height,
                "Quit", "quit"
            )
        ]
        
        # Callback for when button is clicked
        self.on_choice = None  # Will be set by game_window
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        for button in self.buttons:
            if button.handle_event(event):
                self._handle_choice(button.choice_id)
    
    def _handle_choice(self, choice_id: str):
        """Handle menu choice"""
        if choice_id == "new_game":
            print("New Game selected!")  # Placeholder
            # TODO: Start new game, switch to story screen
            if self.on_choice:
                self.on_choice("new_game")
        
        elif choice_id == "continue":
            print("Continue selected!")  # Placeholder
            # TODO: Load saved game
        
        elif choice_id == "quit":
            self.window.running = False
    
    def update(self):
        """Update menu logic (nothing to update for static menu)"""
        pass
    
    def render(self, surface: pygame.Surface):
        """Draw the main menu"""
        # Clear background
        surface.fill(BLACK)
        
        # Draw title
        font = title_font()
        title = font.render("STAR WARS", True, WHITE)
        title_rect = title.get_rect(center=(self.width // 2, 150))
        surface.blit(title, title_rect)
        
        # Draw subtitle
        subtitle_font = header_font()
        subtitle = subtitle_font.render("DARTH VADER", True, SITH_RED)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 220))
        surface.blit(subtitle, subtitle_rect)
        
        # Draw tagline
        tagline_font = normal_font()
        tagline = tagline_font.render("The Dark Times", True, IMPERIAL_RED)
        tagline_rect = tagline.get_rect(center=(self.width // 2, 270))
        surface.blit(tagline, tagline_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.render(surface)
        
        # Draw version/credits at bottom
        credits_font = pygame.font.SysFont("arial", 14)
        credits = credits_font.render("A Star Wars Fan Game | Educational Portfolio Project", True, WHITE)
        credits_rect = credits.get_rect(center=(self.width // 2, self.height - 30))
        surface.blit(credits, credits_rect)