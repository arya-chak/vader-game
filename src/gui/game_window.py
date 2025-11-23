"""
Main game window for Darth Vader RPG.
Handles the pygame window, event loop, and screen management.
"""

import pygame
import sys
from typing import Optional

from .utils import BLACK, WHITE, title_font
from .screens import MainMenuScreen, StoryScreen, CombatScreen


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
    
        # Game systems (initialized when starting new game)
        self.vader = None
        self.suit = None
        self.force_powers = None
        self.story_system = None
        self.current_scene_id = None
    
        # Story flow control
        self._waiting_for_enter = False  # ADD THIS LINE
        self._pending_scene = None       # ADD THIS LINE
    
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
        # Import game systems
        from src.character.vader import DarthVader
        from src.character.suit_system import SuitSystem
        from src.character.force_powers import ForcePowerSystem
        from src.story.story_system import StorySystem
        from src.story.opening_scenes import create_opening_scenes
        
        # Initialize game systems
        self.vader = DarthVader()
        self.suit = SuitSystem()
        self.force_powers = ForcePowerSystem()
        self.story_system = StorySystem(self.vader, self.suit)
        
        # Load opening scenes
        opening_scenes = create_opening_scenes()
        for scene_id, scene in opening_scenes.items():
            self.story_system.register_scene(scene)
        
        # Start at the first scene
        self.current_scene_id = "the_void"
        self._show_story_scene(self.current_scene_id)
    
    def _show_story_scene(self, scene_id: str):
        """Display a story scene"""
        # Start the scene in the story system
        success, msg, scene = self.story_system.start_scene(scene_id)
    
        if not success:
            print(f"Error loading scene: {msg}")
            return
    
        # Create/update story screen
        if not isinstance(self.current_screen, StoryScreen):
            story_screen = StoryScreen(self, self.vader, self.suit)
            story_screen.on_choice_selected = self._handle_story_choice
            self.current_screen = story_screen
    
        # Get dialogue for this scene
        dialogue_lines = self.story_system.get_dialogue_for_scene(scene_id)
    
        # Combine dialogue into one text block for display
        dialogue_text = ""
        speaker = None
    
        for line in dialogue_lines:
            if line.speaker != "Narrator":
                speaker = line.speaker
                dialogue_text += f"{line.text}\n\n"
            else:
                dialogue_text += f"{line.text}\n\n"
        
            # Add internal thought if present
            if line.internal_thought:
                dialogue_text += f"💭 {line.internal_thought}\n\n"
    
        # Set the scene
        self.current_screen.set_scene(scene.title, dialogue_text.strip(), speaker)
    
        # Get available choices
        choices = self.story_system.get_available_choices(scene_id)
    
        if choices:
            # Has choices - show them
            choice_data = []
            for choice in choices:
                # Extract tag from choice text if present (e.g., [RAGE])
                tag = None
                if choice.text.startswith('['):
                    end_bracket = choice.text.find(']')
                    if end_bracket != -1:
                        tag = choice.text[1:end_bracket]
                        display_text = choice.text[end_bracket+1:].strip()
                    else:
                        display_text = choice.text
                else:
                    display_text = choice.text
            
                choice_data.append({
                    'text': display_text,
                    'id': choice.id,
                    'tag': tag
                })
        
            self.current_screen.set_choices(choice_data)
            self._waiting_for_enter = False
    
        elif scene.auto_next:
            # No choices, auto-advance - show "Press ENTER to continue"
            self.current_screen.set_choices([])
            self._waiting_for_enter = True
            self._pending_scene = scene.auto_next
        else:
            # No choices and no auto_next
            self.current_screen.set_choices([])
            self._waiting_for_enter = False

    def _handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
            elif event.type == pygame.KEYDOWN:
                # Handle ENTER key for auto-advance scenes
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if self._waiting_for_enter and self._pending_scene:
                        next_scene = self._pending_scene
                        self._pending_scene = None
                        self._waiting_for_enter = False
                        self.current_scene_id = next_scene
                        self._show_story_scene(next_scene)
        
            # Pass events to current screen if it exists
            if self.current_screen:
                self.current_screen.handle_event(event)
    
    def _handle_story_choice(self, choice_id: str):
        """Handle story choice selection"""
        # Make the choice in the story system
        success, msg, consequences = self.story_system.make_choice(
            self.current_scene_id, 
            choice_id
        )
        
        if not success:
            print(f"Choice error: {msg}")
            return
        
        # Get next scene from consequences
        next_scene = consequences.get('next_scene')
        
        if next_scene:
            self.current_scene_id = next_scene
            self._show_story_scene(next_scene)
        else:
            # No next scene - story ended or needs different handling
            print("Story sequence complete or requires special handling")
    
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