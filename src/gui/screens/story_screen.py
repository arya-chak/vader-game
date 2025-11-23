"""
Story screen - displays narrative, dialogue, and choices.
Clean layout focused on storytelling - no HUD clutter.
"""

import pygame
from ..utils import BLACK, WHITE, VADER_BLACK, normal_font, small_font
from ..components import TextBox, ChoiceButton


class StoryScreen:
    """
    Story/dialogue screen with scene text and choices.
    Status bars only appear in combat, not here.
    """
    
    def __init__(self, window, vader, suit):
        """
        Initialize story screen.
        
        Args:
            window: GameWindow instance
            vader: DarthVader character instance
            suit: SuitSystem instance
        """
        self.window = window
        self.width = window.width
        self.height = window.height
        
        # Game systems (keep reference but don't display constantly)
        self.vader = vader
        self.suit = suit
        
        # Scene/dialogue text box (centered, larger)
        text_box_width = 900
        text_box_height = 350
        text_box_x = (self.width - text_box_width) // 2
        text_box_y = self.height - text_box_height - 250
        
        self.dialogue_box = TextBox(text_box_x, text_box_y, text_box_width, text_box_height)
        
        # Current scene
        self.scene_title = ""
        self.current_choices = []
        
        # Callback for when choice is made
        self.on_choice_selected = None
    
    def set_scene(self, title: str, dialogue_text: str, speaker: str = None):
        """
        Set the current scene's dialogue.
        
        Args:
            title: Scene title
            dialogue_text: The dialogue/narration text
            speaker: Character speaking (e.g., "Vader", "Palpatine")
        """
        self.scene_title = title
        self.dialogue_box.set_text(dialogue_text, speaker)
    
    def set_choices(self, choices: list):
        """
        Set the available choices.
        
        Args:
            choices: List of dicts with 'text', 'id', and optional 'tag'
        """
        self.current_choices = []
        
        button_width = 800
        button_height = 60
        button_x = (self.width - button_width) // 2
        start_y = self.height - 180
        
        for i, choice_data in enumerate(choices):
            y = start_y + (i * 70)
            
            button = ChoiceButton(
                button_x, y,
                button_width, button_height,
                choice_data['text'],
                choice_data['id'],
                choice_data.get('tag')
            )
            self.current_choices.append(button)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        for button in self.current_choices:
            if button.handle_event(event):
                if self.on_choice_selected:
                    self.on_choice_selected(button.choice_id)
    
    def update(self):
        """Update game logic"""
        pass  # Nothing to update for story screen
    
    def render(self, surface: pygame.Surface):
        """Draw the story screen"""
        surface.fill(BLACK)
    
        # Scene title at top
        if self.scene_title:
            title_font = pygame.font.SysFont("arial", 28, bold=True)
            title_surface = title_font.render(self.scene_title, True, WHITE)
            title_rect = title_surface.get_rect(center=(self.width // 2, 50))
            surface.blit(title_surface, title_rect)
    
        # TODO: Scene image/background will go here (upper portion)
    
        # Dialogue box
        self.dialogue_box.render(surface)
    
        # Choice buttons OR "Press ENTER" prompt
        if self.current_choices:
            for button in self.current_choices:
                button.render(surface)
        else:
            # Show "Press ENTER to continue" at bottom
            prompt_font = small_font()
            prompt_text = prompt_font.render("Press ENTER to continue...", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(self.width // 2, self.height - 50))
            surface.blit(prompt_text, prompt_rect)