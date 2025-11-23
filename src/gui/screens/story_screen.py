"""
Story screen - displays narrative, dialogue, and choices.
This is where the player experiences the story and makes decisions.
"""

import pygame
from ..utils import BLACK, WHITE, VADER_BLACK, normal_font, small_font
from ..components import TextBox, ChoiceButton, HealthBar


class StoryScreen:
    """
    Story/dialogue screen with Vader status, scene text, and choices.
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
        
        # Game systems
        self.vader = vader
        self.suit = suit
        
        # Layout sections
        self._create_layout()
        
        # Current scene data
        self.current_dialogue = []
        self.current_choices = []
        self.scene_title = ""
        
        # Callback for when choice is made
        self.on_choice_selected = None
    
    def _create_layout(self):
        """Create the layout components"""
        # Status panel (left side) - 20% of width
        status_width = 250
        status_x = 20
        status_y = 20
        
        # Health bars
        bar_width = 200
        bar_height = 25
        bar_x = status_x + 25
        
        self.hp_bar = HealthBar(bar_x, status_y + 80, bar_width, bar_height, "HP")
        self.fp_bar = HealthBar(bar_x, status_y + 120, bar_width, bar_height, "FP")
        self.suit_bar = HealthBar(bar_x, status_y + 160, bar_width, bar_height, "Suit")
        
        # Story panel (center/right) - remaining width
        story_x = status_width + 60
        story_width = self.width - story_x - 40
        
        # Scene/dialogue text box
        self.dialogue_box = TextBox(
            story_x, 20,
            story_width, 400
        )
        
        # Choice buttons area
        self.choice_y_start = 450
        self.choice_spacing = 70
    
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
                    Example: [{'text': 'Attack', 'id': 'attack', 'tag': 'RAGE'}]
        """
        self.current_choices = []
        
        button_width = self.width - 300 - 60
        button_height = 60
        button_x = 300
        
        for i, choice_data in enumerate(choices):
            y = self.choice_y_start + (i * self.choice_spacing)
            
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
        # Check choice buttons
        for button in self.current_choices:
            if button.handle_event(event):
                self._handle_choice(button.choice_id)
    
    def _handle_choice(self, choice_id: str):
        """Handle choice selection"""
        if self.on_choice_selected:
            self.on_choice_selected(choice_id)
    
    def update(self):
        """Update game logic"""
        # Update status bars with current Vader stats
        self.hp_bar.set_value(self.vader.current_health, self.vader.max_health)
        self.fp_bar.set_value(self.vader.current_force_points, self.vader.max_force_points)
        self.suit_bar.set_value(self.suit.integrity, 100)
    
    def render(self, surface: pygame.Surface):
        """Draw the story screen"""
        # Background
        surface.fill(BLACK)
        
        # Status panel background
        status_bg = pygame.Rect(10, 10, 260, 250)
        pygame.draw.rect(surface, VADER_BLACK, status_bg)
        pygame.draw.rect(surface, WHITE, status_bg, 2)
        
        # Status title
        font = normal_font()
        status_title = font.render("VADER", True, WHITE)
        surface.blit(status_title, (30, 30))
        
        # Health bars
        self.hp_bar.render(surface)
        self.fp_bar.render(surface)
        self.suit_bar.render(surface)
        
        # Psychological state (small text)
        small = small_font()
        y_offset = 220
        
        darkness_text = small.render(f"💀 Darkness: {self.vader.psychological_state.darkness}", True, WHITE)
        surface.blit(darkness_text, (30, y_offset))
        
        control_text = small.render(f"🧠 Control: {self.vader.psychological_state.control}", True, WHITE)
        surface.blit(control_text, (30, y_offset + 20))
        
        # Scene title
        if self.scene_title:
            title_font = pygame.font.SysFont("arial", 24, bold=True)
            title_surface = title_font.render(self.scene_title, True, WHITE)
            surface.blit(title_surface, (300, 30))
        
        # Dialogue box
        self.dialogue_box.render(surface)
        
        # Choice buttons
        for button in self.current_choices:
            button.render(surface)