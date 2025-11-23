"""
Main game window for Darth Vader RPG.
Handles the pygame window, event loop, and screen management.
"""

import pygame
import sys
from typing import Optional

from .utils import BLACK, WHITE, title_font
from .screens import MainMenuScreen, StoryScreen


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
        self.current_screen = None
        
        # Game systems (will be initialized when starting new game)
        self.vader = None
        self.suit = None
        self.force_powers = None
        
        # Start at main menu
        self._show_main_menu()
    
    def _show_main_menu(self):
        """Switch to main menu"""
        menu = MainMenuScreen(self)
        menu.on_choice = self._handle_menu_choice
        self.current_screen = menu
    
    def _handle_menu_choice(self, choice: str):
        """Handle main menu choice"""
        if choice == "new_game":
            self._start_new_game()
    
    def _start_new_game(self):
        """Initialize new game and switch to story screen"""
        # Import here to avoid circular imports
        from src.character.vader import DarthVader
        from src.character.suit_system import SuitSystem
        from src.character.force_powers import ForcePowerSystem
        
        # Initialize game systems
        self.vader = DarthVader()
        self.suit = SuitSystem()
        self.force_powers = ForcePowerSystem()
        
        # Create story screen
        story_screen = StoryScreen(self, self.vader, self.suit)
        story_screen.on_choice_selected = self._handle_story_choice
        
        # Set a test scene
        story_screen.set_scene(
            "The Awakening",
            "You awaken on the operating table. The mechanical breathing fills your ears. Everything hurts. Through the pain, one thought burns: Where is Padmé?",
            "Narrator"
        )
        
        # Set test choices
        story_screen.set_choices([
            {'text': 'Demand to know where Padmé is', 'id': 'demand', 'tag': 'RAGE'},
            {'text': 'Ask about her condition calmly', 'id': 'ask', 'tag': 'CONTROL'},
            {'text': 'Focus on your situation', 'id': 'assess', 'tag': 'SUPPRESS'}
        ])
        
        self.current_screen = story_screen
    
    def _handle_story_choice(self, choice_id: str):
        """Handle story choice"""
        print(f"Story choice made: {choice_id}")
        # TODO: This will integrate with your story system
    
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
        
        # Render current screen
        if self.current_screen:
            self.current_screen.render(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def quit(self):
        """Clean shutdown"""
        pygame.quit()
        sys.exit()