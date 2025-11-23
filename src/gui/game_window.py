"""
Main game window for Darth Vader RPG.
Handles the pygame window, event loop, and screen management.
"""

import pygame
import sys
from typing import Optional

from .utils import BLACK, WHITE, title_font


class GameWindow:
    """
    Main game window that manages the pygame display and game loop.
    """
    
    def __init__(self, width: int = 1280, height: int = 720, title: str = "Star Wars: Darth Vader"):
        """
        Initialize the game window.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
        """
        # Initialize pygame
        pygame.init()
        
        # Window settings
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Clock for controlling framerate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.running = True
        self.current_screen = None  # Will hold the active screen (menu, story, combat)
        
    def run(self):
        """
        Main game loop.
        Handles events, updates, and rendering.
        """
        while self.running:
            # Handle events
            self._handle_events()
            
            # Update game state
            self._update()
            
            # Render
            self._render()
            
            # Control framerate
            self.clock.tick(self.fps)
        
        # Cleanup
        self.quit()
    
    def _handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Pass events to current screen if it exists
            if self.current_screen:
                self.current_screen.handle_event(event)
    
    def _update(self):
        """Update game logic"""
        if self.current_screen:
            self.current_screen.update()
    
    def _render(self):
        """Render the current frame"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Render current screen if it exists
        if self.current_screen:
            self.current_screen.render(self.screen)
        else:
            # Placeholder if no screen is loaded
            self._render_placeholder()
        
        # Update display
        pygame.display.flip()
    
    def _render_placeholder(self):
        """Temporary placeholder screen"""
        font = title_font()
        text = font.render("STAR WARS: DARTH VADER", True, WHITE)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        
        # Small instruction text
        small_font = pygame.font.SysFont("arial", 20)
        instruction = small_font.render("GUI System Initialized - Screens loading...", True, WHITE)
        instruction_rect = instruction.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(instruction, instruction_rect)
    
    def set_screen(self, screen):
        """
        Switch to a different screen (menu, story, combat, etc.)
        
        Args:
            screen: Screen object to display
        """
        self.current_screen = screen
    
    def quit(self):
        """Clean shutdown"""
        pygame.quit()
        sys.exit()