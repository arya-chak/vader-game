"""
Star Wars: Darth Vader RPG - GUI Main Entry Point
Pygame-based GUI with Mask HUD main menu and integrated game flow.
"""

import pygame
import sys
import os
from typing import Optional

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import the mask HUD menu and story dialogue screen
from src.gui.screens.mask_hud import MaskHUDMenu
from src.gui.screens.story_dialogue import StoryDialogueScreen


class GameState:
    """Enum-like class for game states"""
    MAIN_MENU = "main_menu"
    SAVE_SLOT_SELECT = "save_slot_select"
    LOADING_GAME = "loading_game"
    STORY_PLAYING = "story_playing"
    PLAYING = "playing"
    SETTINGS = "settings"
    QUIT = "quit"


class SaveSlotScreen:
    """Screen to select which save slot to start a new game in"""
    
    def __init__(self, window_width: int = 1600, window_height: int = 900):
        self.width = window_width
        self.height = window_height
        self.selected_slot = 0
        self.slots = [
            {"slot": 1, "name": "Slot 1", "description": "Empty", "used": False},
            {"slot": 2, "name": "Slot 2", "description": "Empty", "used": False},
            {"slot": 3, "name": "Slot 3", "description": "Empty", "used": False},
        ]
        
        # Setup fonts
        try:
            distant_galaxy_path = os.path.join(script_dir, 'gui/utils/fonts/SfDistantGalaxyAlternateItalic-3RDM.ttf')
            imperial_code_path = os.path.join(script_dir, 'gui/utils/fonts/ImperialCode-VGXpx.ttf')
            self.title_font = pygame.font.Font(distant_galaxy_path, 64)
            self.slot_font = pygame.font.Font(imperial_code_path, 40)
            self.desc_font = pygame.font.Font(imperial_code_path, 24)
        except:
            self.title_font = pygame.font.SysFont('arial', 64, bold=True)
            self.slot_font = pygame.font.SysFont('arial', 40, bold=True)
            self.desc_font = pygame.font.SysFont('arial', 24)
        
        # Colors
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 165, 0)
        self.selected_color = (0, 255, 255)
        self.slot_rects = []
    
    def update(self, dt: float) -> None:
        """Update save slot screen"""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the save slot selection screen"""
        surface.fill(self.bg_color)
        
        # Draw title
        title = self.title_font.render("SELECT SAVE SLOT", True, self.selected_color)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        surface.blit(title, title_rect)
        
        # Draw save slots
        self.slot_rects = []
        slot_width = 300
        slot_height = 200
        gap = 50
        
        total_width = (slot_width * 3) + (gap * 2)
        start_x = (self.width - total_width) // 2
        start_y = 300
        
        for i, slot in enumerate(self.slots):
            x = start_x + (i * (slot_width + gap))
            y = start_y
            
            slot_rect = pygame.Rect(x, y, slot_width, slot_height)
            self.slot_rects.append(slot_rect)
            
            # Draw slot background
            if i == self.selected_slot:
                pygame.draw.rect(surface, self.selected_color, slot_rect, 3)
                color = self.selected_color
            else:
                pygame.draw.rect(surface, self.text_color, slot_rect, 2)
                color = self.text_color
            
            # Draw slot content
            slot_text = self.slot_font.render(f"SLOT {slot['slot']}", True, color)
            slot_text_rect = slot_text.get_rect(center=(x + slot_width // 2, y + 50))
            surface.blit(slot_text, slot_text_rect)
            
            desc_text = self.desc_font.render(slot['description'], True, color)
            desc_text_rect = desc_text.get_rect(center=(x + slot_width // 2, y + 130))
            surface.blit(desc_text, desc_text_rect)
    
    def handle_input(self, event: pygame.event.Event) -> Optional[int]:
        """
        Handle input for save slot selection.
        Returns the selected slot number (1-3) or None if not selected.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_slot = (self.selected_slot - 1) % len(self.slots)
            elif event.key == pygame.K_RIGHT:
                self.selected_slot = (self.selected_slot + 1) % len(self.slots)
            elif event.key == pygame.K_RETURN:
                return self.slots[self.selected_slot]['slot']
            elif event.key == pygame.K_ESCAPE:
                return -1  # Return to main menu
        
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(event.pos):
                    self.selected_slot = i
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for i, rect in enumerate(self.slot_rects):
                    if rect.collidepoint(event.pos):
                        return self.slots[i]['slot']
        
        return None


class GUIGame:
    """Main game controller with GUI"""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.width = 1600
        self.height = 900
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h - 130
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Darth Vader: Mask of Vader")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.current_state = GameState.MAIN_MENU
        self.selected_slot = None
        
        # Setup fonts for dialogue screen
        try:
            import os
            distant_galaxy_path = os.path.join(script_dir, 'src/gui/utils/fonts/SfDistantGalaxyAlternateItalic-3RDM.ttf')
            self.dialogue_font = pygame.font.SysFont('times new roman', 18)
            self.speaker_font = pygame.font.SysFont('times new roman', 16, bold=True)
            self.title_font = pygame.font.Font(distant_galaxy_path, 48)
            self.choice_font = pygame.font.SysFont('times new roman', 16)
        except:
            self.dialogue_font = pygame.font.SysFont('times new roman', 18)
            self.speaker_font = pygame.font.SysFont('times new roman', 16, bold=True)
            self.title_font = pygame.font.SysFont('arial', 48, bold=True)
            self.choice_font = pygame.font.SysFont('times new roman', 16)
        
        # Initialize screens
        self.main_menu = MaskHUDMenu(
            window_width=self.width,
            window_height=self.height,
            on_new_game=self.on_new_game,
            on_continue=self.on_continue,
            on_settings=self.on_settings,
            on_quit=self.on_quit
        )
        self.save_slot_screen = SaveSlotScreen(self.width, self.height)
        
        # Initialize story dialogue screen
        self.story_screen = StoryDialogueScreen(
            window_width=self.width,
            window_height=self.height,
            dialogue_font=self.dialogue_font,
            speaker_font=self.speaker_font,
            title_font=self.title_font,
            choice_font=self.choice_font
        )
        self.story_screen.set_choice_callback(self.on_story_choice_selected)
    
    def on_new_game(self) -> None:
        """Handle new game button press"""
        self.current_state = GameState.SAVE_SLOT_SELECT
    
    def on_continue(self) -> None:
        """Handle continue button press"""
        # TODO: Load most recent save
        print("Continue feature coming soon")
    
    def on_settings(self) -> None:
        """Handle settings button press"""
        self.current_state = GameState.SETTINGS
        print("Settings feature coming soon")
    
    def on_quit(self) -> None:
        """Handle quit button press"""
        self.running = False
    
    def on_story_choice_selected(self, choice_id: str) -> None:
        """Handle story choice selection"""
        print(f"Story choice selected: {choice_id}")
        # TODO: Process choice in game logic and load next scene
        # For now, just advance to show how it works
        # This will be replaced with actual game logic integration
    
    def start_new_game(self, slot: int) -> None:
        """Start a new game in the selected slot"""
        print(f"Starting new game in slot {slot}")
        self.selected_slot = slot
        
        # Create a test scene to demonstrate the story screen
        test_scene = {
            'id': 'the_void',
            'title': 'THE VOID',
            'background_image': None,
            'lines': [
                {
                    'speaker': 'Narrator',
                    'text': 'Darkness. Cold. An endless void stretches before you.',
                    'left_portrait': None,
                    'right_portrait': None,
                },
                {
                    'speaker': 'Vader',
                    'text': 'I sense a disturbance in the Force.',
                    'left_portrait': 'vader_mask',
                    'right_portrait': None,
                },
                {
                    'speaker': 'Officer',
                    'text': 'Lord Vader, the rebels have been spotted near the Kyber Temple.',
                    'left_portrait': 'vader_mask',
                    'right_portrait': 'imperial_officer',
                },
            ],
            'choices': [
                {
                    'id': 'hunt_rebels',
                    'text': 'Hunt them down. Leave none alive.',
                    'tags': ['[DARK SIDE]'],
                },
                {
                    'id': 'interrogate',
                    'text': 'Capture them for interrogation.',
                    'tags': [],
                },
                {
                    'id': 'investigate',
                    'text': 'Investigate the Kyber Temple personally.',
                    'tags': [],
                },
            ]
        }
        
        # Load test scene into story screen
        self.story_screen.set_scene(test_scene)
        
        # Transition directly to story screen (no loading delay)
        self.current_state = GameState.STORY_PLAYING
    
    def return_to_menu(self) -> None:
        """Return to main menu"""
        self.current_state = GameState.MAIN_MENU
    
    def handle_input(self) -> None:
        """Handle all input based on current state"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif self.current_state == GameState.MAIN_MENU:
                self.main_menu.handle_input(event)
            
            elif self.current_state == GameState.SAVE_SLOT_SELECT:
                result = self.save_slot_screen.handle_input(event)
                if result is not None:
                    if result == -1:
                        self.return_to_menu()
                    else:
                        self.start_new_game(result)
            
            elif self.current_state == GameState.STORY_PLAYING:
                self.story_screen.handle_input(event)
    
    def update(self, dt: float) -> None:
        """Update game state"""
        if self.current_state == GameState.MAIN_MENU:
            self.main_menu.update(dt)
        elif self.current_state == GameState.SAVE_SLOT_SELECT:
            self.save_slot_screen.update(dt)
        elif self.current_state == GameState.STORY_PLAYING:
            self.story_screen.update(dt)
    
    def draw(self) -> None:
        """Draw current screen"""
        if self.current_state == GameState.MAIN_MENU:
            self.main_menu.draw(self.screen)
        elif self.current_state == GameState.SAVE_SLOT_SELECT:
            self.save_slot_screen.draw(self.screen)
        elif self.current_state == GameState.LOADING_GAME:
            # Draw loading screen
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            text = font.render(f"Starting game in Slot {self.selected_slot}...", True, (255, 165, 0))
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text, text_rect)
        elif self.current_state == GameState.STORY_PLAYING:
            self.story_screen.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            
            self.handle_input()
            self.update(dt)
            self.draw()
        
        self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.main_menu.cleanup()
        pygame.quit()


if __name__ == "__main__":
    game = GUIGame()
    game.run()