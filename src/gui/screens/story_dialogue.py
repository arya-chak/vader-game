"""
StoryDialogueScreen - Main story and dialogue display screen.
Integrates DialogueBox, Portrait, and ChoiceButton components.
Manages scene display, dialogue flow, and choice selection.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Callable
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from gui.components.dialogue_box import DialogueBox
from gui.components.portrait import Portrait
from gui.components.choice_button import ChoiceButton


class StoryDialogueScreen:
    """
    Main screen for displaying story scenes and dialogue.
    Manages scene layout, character portraits, dialogue text, and choice selection.
    """
    
    def __init__(self, window_width: int = 1600, window_height: int = 900,
                 dialogue_font: pygame.font.Font = None,
                 speaker_font: pygame.font.Font = None,
                 title_font: pygame.font.Font = None,
                 choice_font: pygame.font.Font = None):
        """
        Initialize the StoryDialogueScreen.
        
        Args:
            window_width: Width of the screen (default 1600)
            window_height: Height of the screen (default 900)
            dialogue_font: Font for dialogue text (default Times New Roman 18)
            speaker_font: Font for speaker names (default Times New Roman 16 bold)
            title_font: Font for scene title (default SF Distant Galaxy 48)
            choice_font: Font for choices (default Times New Roman 16)
        """
        self.width = window_width
        self.height = window_height
        
        # Setup fonts with defaults
        if dialogue_font is None:
            dialogue_font = pygame.font.SysFont('times new roman', 18)
        if speaker_font is None:
            speaker_font = pygame.font.SysFont('times new roman', 16, bold=True)
        if title_font is None:
            title_font = pygame.font.SysFont('arial', 48, bold=True)
        if choice_font is None:
            choice_font = pygame.font.SysFont('times new roman', 16)
        
        self.dialogue_font = dialogue_font
        self.speaker_font = speaker_font
        self.title_font = title_font
        self.choice_font = choice_font
        
        # Colors
        self.bg_color = (10, 10, 10)  # Black
        self.title_color = (220, 100, 20)        # Reddish-orange
        self.dialogue_color = (255, 255, 255)    # White
        self.speaker_color = (255, 170, 0)       # Gold
        self.choice_color = (200, 80, 10)        # Reddish-orange
        self.choice_selected_color = (255, 180, 0)   # Bright gold when selected
        self.choice_hover_color = (240, 130, 30)     # Lighter orange on hover
        self.panel_border_color = (180, 60, 0)       # Dark red-orange for borders
        self.panel_border_inner = (120, 40, 0)       # Dimmer inner border
        
        # Layout dimensions
        self.scene_bg_height = 500
        self.title_bar_height = 60
        self.dialogue_section_start = self.scene_bg_height + self.title_bar_height
        self.dialogue_section_height = 240
        self.choices_section_start = self.dialogue_section_start + self.dialogue_section_height
        
        # Scene data
        self.current_scene_id = None
        self.scene_title = ""
        self.scene_background = None
        self.scene_background_color = (15, 8, 8)  # Near-black with slight red warmth
        
        # Components
        self.dialogue_box: Optional[DialogueBox] = None
        self.left_portrait: Optional[Portrait] = None
        self.right_portrait: Optional[Portrait] = None
        self.choice_buttons: List[ChoiceButton] = []
        
        # State
        self.current_dialogue_line = 0
        self.dialogue_lines: List[Dict] = []
        self.available_choices: List[Dict] = []
        self.selected_choice_index = 0
        self.is_displaying_choices = False
        self.is_complete = False
        
        # Callbacks
        self.on_choice_selected: Optional[Callable[[str], None]] = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize all UI components."""
        # Create left portrait
        left_portrait_x = 50
        left_portrait_y = self.dialogue_section_start
        left_portrait_width = 200
        left_portrait_height = 240
        
        self.left_portrait = Portrait(
            x=left_portrait_x,
            y=left_portrait_y,
            width=left_portrait_width,
            height=left_portrait_height,
            border_color=(220, 100, 20),
            glow_color=(220, 100, 20)
        )
        
        # Create right portrait
        right_portrait_x = self.width - 250
        right_portrait_y = self.dialogue_section_start
        right_portrait_width = 200
        right_portrait_height = 240
        
        self.right_portrait = Portrait(
            x=right_portrait_x,
            y=right_portrait_y,
            width=right_portrait_width,
            height=right_portrait_height,
            border_color=(220, 100, 20),
            glow_color=(220, 100, 20)
        )
        
        # Create dialogue box (centered between portraits)
        dialogue_box_x = left_portrait_x + left_portrait_width + 20
        dialogue_box_y = self.dialogue_section_start + 30
        dialogue_box_width = right_portrait_x - dialogue_box_x - 20
        dialogue_box_height = 150
        
        self.dialogue_box = DialogueBox(
            x=dialogue_box_x,
            y=dialogue_box_y,
            width=dialogue_box_width,
            height=dialogue_box_height,
            dialogue_font=self.dialogue_font,
            speaker_font=self.speaker_font,
            dialogue_color=self.dialogue_color,
            speaker_color=self.speaker_color
        )
    
    def set_scene(self, scene_data: Dict) -> None:
        """
        Set the current scene to display.
        
        Args:
            scene_data: Dictionary containing scene information:
                {
                    'id': scene_id,
                    'title': 'SCENE TITLE',
                    'background_image': 'path/to/image.png' (optional),
                    'lines': [
                        {
                            'speaker': 'CHARACTER_NAME',
                            'text': 'Dialogue text here',
                            'left_portrait': 'character_id' (optional),
                            'right_portrait': 'character_id' (optional),
                        },
                        ...
                    ],
                    'choices': [
                        {
                            'id': 'choice_id',
                            'text': 'Choice text',
                            'tags': [(tag_text, color), ...] (optional),
                        },
                        ...
                    ]
                }
        """
        # Clear previous state
        self.clear()
        
        # Set scene info
        self.current_scene_id = scene_data.get('id', '')
        self.scene_title = scene_data.get('title', '').upper()
        
        # Load background image if provided
        bg_image = scene_data.get('background_image')
        if bg_image:
            self._load_background_image(bg_image)
        
        # Load dialogue lines
        self.dialogue_lines = scene_data.get('lines', [])
        
        # Load choices
        self.available_choices = scene_data.get('choices', [])
        
        # Display first line
        self._display_next_line()
    
    def _load_background_image(self, image_path: str) -> bool:
        """
        Load a scene background image.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            True if loaded successfully
        """
        try:
            image = pygame.image.load(image_path)
            self.scene_background = pygame.transform.scale(image, 
                                                          (self.width, 
                                                           self.scene_bg_height))
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading background image: {e}")
            self.scene_background = None
            return False
    
    def _display_next_line(self) -> None:
        """Display the next dialogue line."""
        if self.current_dialogue_line >= len(self.dialogue_lines):
            # All lines displayed, show choices
            self._show_choices()
            return
        
        line_data = self.dialogue_lines[self.current_dialogue_line]
        
        # Get speaker and text
        speaker = line_data.get('speaker', 'Narrator')
        text = line_data.get('text', '')
        
        # Update dialogue box
        self.dialogue_box.set_dialogue(speaker, text)
        
        # Update portraits
        left_portrait_id = line_data.get('left_portrait')
        right_portrait_id = line_data.get('right_portrait')
        
        # Update portrait speaking states
        self.left_portrait.set_speaking(speaker != 'Narrator' and 
                                       left_portrait_id is not None)
        self.right_portrait.set_speaking(speaker != 'Narrator' and 
                                        right_portrait_id is not None)
        
        self.is_displaying_choices = False
        self.current_dialogue_line += 1
    
    def _show_choices(self) -> None:
        """Show available choices."""
        self.choice_buttons = []
        
        # Turn off portrait glows when showing choices
        self.left_portrait.set_speaking(False)
        self.right_portrait.set_speaking(False)
        
        if not self.available_choices:
            self.is_complete = True
            return
        
        # Create choice buttons
        choice_y = self.choices_section_start + 20
        choice_x = 100
        
        # Calculate spacing so all choices fit on screen
        available_height = self.height - choice_y
        spacing = min(45, max(30, (available_height - 50) // len(self.available_choices)))
        
        for i, choice_data in enumerate(self.available_choices):
            choice_button = ChoiceButton(
                x=choice_x,
                y=choice_y + (i * spacing),
                choice_id=choice_data.get('id', ''),
                text=choice_data.get('text', ''),
                font=self.choice_font,
                normal_color=self.choice_color,
                selected_color=self.choice_selected_color,
                hover_color=self.choice_hover_color
            )
            
            # Add tags if present
            tags = choice_data.get('tags', [])
            if tags:
                for tag_text in tags:
                    choice_button.add_tag(tag_text)
            
            self.choice_buttons.append(choice_button)
        
        # Select first choice by default
        if self.choice_buttons:
            self.choice_buttons[0].set_selected(True)
            self.selected_choice_index = 0
        
        self.is_displaying_choices = True
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the entire screen.
        
        Args:
            surface: Pygame surface to draw to
        """
        # Clear background
        surface.fill(self.bg_color)

        # Draw scene background
        self._draw_scene_background(surface)

        # Draw DS-style panel border framing the bottom section
        self._draw_panel_border(surface)

        # Draw title bar
        self._draw_title_bar(surface)
        
        # Draw portraits
        self.left_portrait.draw(surface)
        self.right_portrait.draw(surface)
        
        # Draw dialogue box
        self.dialogue_box.draw(surface)
        
        # Draw choices if visible
        if self.is_displaying_choices:
            self._draw_choices(surface)
    
    def _draw_scene_background(self, surface: pygame.Surface) -> None:
        """Draw the scene background."""
        if self.scene_background:
            surface.blit(self.scene_background, (0, 0))
        else:
            # Draw gradient-like background
            pygame.draw.rect(surface, self.scene_background_color,
                           (0, 0, self.width, self.scene_bg_height))
    
    def _draw_title_bar(self, surface: pygame.Surface) -> None:
        """Draw the title bar with scene name."""
        pygame.draw.line(surface, (50, 50, 50),
                        (0, self.scene_bg_height),
                        (self.width, self.scene_bg_height), 2)

        if self.scene_title:
            title_surface = self.title_font.render(self.scene_title, True,
                                                   self.title_color)
            title_x = 50
            title_y = self.scene_bg_height + 10
            surface.blit(title_surface, (title_x, title_y))

    def _draw_panel_border(self, surface: pygame.Surface) -> None:
        """Draw DS-style tech border framing the bottom panel (y=500 to y=900)."""
        bracket_color = (220, 100, 20)
        divider_color = (100, 35, 0)
        dot_color = (180, 60, 0)

        # Outer border
        pygame.draw.rect(surface, self.panel_border_color,
                         (0, 500, 1600, 400), 2)

        # Inner border (inset 6px)
        pygame.draw.rect(surface, self.panel_border_inner,
                         (6, 506, 1588, 388), 1)

        # Corner brackets — L-shaped, 20px long, 2px wide
        # Top-left
        pygame.draw.line(surface, bracket_color, (0, 500), (20, 500), 2)
        pygame.draw.line(surface, bracket_color, (0, 500), (0, 520), 2)
        # Top-right
        pygame.draw.line(surface, bracket_color, (1580, 500), (1600, 500), 2)
        pygame.draw.line(surface, bracket_color, (1599, 500), (1599, 520), 2)
        # Bottom-left
        pygame.draw.line(surface, bracket_color, (0, 899), (20, 899), 2)
        pygame.draw.line(surface, bracket_color, (0, 880), (0, 900), 2)
        # Bottom-right
        pygame.draw.line(surface, bracket_color, (1580, 899), (1600, 899), 2)
        pygame.draw.line(surface, bracket_color, (1599, 880), (1599, 900), 2)

        # Horizontal divider at y=560 (title / dialogue separator)
        pygame.draw.line(surface, divider_color, (0, 560), (1600, 560), 1)
        # Horizontal divider at y=800 (dialogue / choices separator)
        pygame.draw.line(surface, divider_color, (0, 800), (1600, 800), 1)

        # Decorative dots at midpoints of divider line ends
        for dot_pos in [(8, 560), (1592, 560), (8, 800), (1592, 800)]:
            pygame.draw.circle(surface, dot_color, dot_pos, 3)

    def _draw_choices(self, surface: pygame.Surface) -> None:
        """Draw all choice buttons."""
        for choice_button in self.choice_buttons:
            choice_button.draw(surface)
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """
        Handle user input.
        
        Args:
            event: Pygame event object
        """
        if not self.is_displaying_choices:
            # In dialogue mode - advance to next line
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._display_next_line()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._display_next_line()
        else:
            # In choice mode - navigate and select
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._select_previous_choice()
                elif event.key == pygame.K_DOWN:
                    self._select_next_choice()
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._confirm_choice()
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_hover(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
    
    def _select_previous_choice(self) -> None:
        """Select the previous choice."""
        if not self.choice_buttons:
            return
        
        # Deselect current
        self.choice_buttons[self.selected_choice_index].set_selected(False)
        
        # Select previous
        self.selected_choice_index = (self.selected_choice_index - 1) % len(self.choice_buttons)
        self.choice_buttons[self.selected_choice_index].set_selected(True)
    
    def _select_next_choice(self) -> None:
        """Select the next choice."""
        if not self.choice_buttons:
            return
        
        # Deselect current
        self.choice_buttons[self.selected_choice_index].set_selected(False)
        
        # Select next
        self.selected_choice_index = (self.selected_choice_index + 1) % len(self.choice_buttons)
        self.choice_buttons[self.selected_choice_index].set_selected(True)
    
    def _confirm_choice(self) -> None:
        """Confirm the currently selected choice."""
        if not self.choice_buttons or not self.is_displaying_choices:
            return
        
        selected_button = self.choice_buttons[self.selected_choice_index]
        choice_id = selected_button.get_choice_id()
        
        # Trigger callback
        if self.on_choice_selected:
            self.on_choice_selected(choice_id)
    
    def _handle_mouse_hover(self, pos: Tuple[int, int]) -> None:
        """Handle mouse hover over choices."""
        for i, choice_button in enumerate(self.choice_buttons):
            if choice_button.collidepoint(pos):
                # Deselect previous
                self.choice_buttons[self.selected_choice_index].set_selected(False)
                
                # Select new choice
                choice_button.set_selected(True)
                self.selected_choice_index = i
            else:
                choice_button.set_hovered(False)
    
    def _handle_mouse_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click on choices."""
        for choice_button in self.choice_buttons:
            if choice_button.collidepoint(pos):
                # Confirm this choice
                choice_id = choice_button.get_choice_id()
                if self.on_choice_selected:
                    self.on_choice_selected(choice_id)
                break
    
    def advance_to_next_line(self) -> None:
        """Manually advance to the next dialogue line."""
        if not self.is_displaying_choices:
            self._display_next_line()
    
    def set_choice_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set the callback function for when a choice is selected.
        
        Args:
            callback: Function that takes choice_id as parameter
        """
        self.on_choice_selected = callback
    
    def load_portrait(self, side: str, image_path: str) -> bool:
        """
        Load a portrait image for left or right side.
        
        Args:
            side: 'left' or 'right'
            image_path: Path to portrait image
        
        Returns:
            True if loaded successfully
        """
        if side.lower() == 'left':
            return self.left_portrait.load_image(image_path)
        elif side.lower() == 'right':
            return self.right_portrait.load_image(image_path)
        return False
    
    def clear(self) -> None:
        """Clear all scene data and reset state."""
        self.current_scene_id = None
        self.scene_title = ""
        self.scene_background = None
        self.current_dialogue_line = 0
        self.dialogue_lines = []
        self.available_choices = []
        self.selected_choice_index = 0
        self.choice_buttons = []
        self.is_displaying_choices = False
        self.is_complete = False
        
        if self.dialogue_box:
            self.dialogue_box.clear()
        if self.left_portrait:
            self.left_portrait.clear_image()
        if self.right_portrait:
            self.right_portrait.clear_image()
    
    def update(self, dt: float) -> None:
        """
        Update screen state.
        
        Args:
            dt: Delta time in seconds
        """
        # Update components
        if self.dialogue_box:
            self.dialogue_box.update(dt)
        if self.left_portrait:
            self.left_portrait.update(dt)
        if self.right_portrait:
            self.right_portrait.update(dt)
        
        for choice_button in self.choice_buttons:
            choice_button.update(dt)
    
    def get_current_scene_id(self) -> Optional[str]:
        """Get the current scene ID."""
        return self.current_scene_id
    
    def get_selected_choice_id(self) -> Optional[str]:
        """Get the currently selected choice ID."""
        if self.is_displaying_choices and self.choice_buttons:
            return self.choice_buttons[self.selected_choice_index].get_choice_id()
        return None
    
    def is_scene_complete(self) -> bool:
        """Check if scene is complete (all dialogue shown and choice made)."""
        return self.is_complete