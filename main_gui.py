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
from src.character.vader import DarthVader
from src.character.suit_system import SuitSystem
from src.story.story_system import StorySystem, Scene
from src.story.opening_scenes import create_opening_scenes
from src.story.mission_kyber import create_kyber_mission_scenes
from src.gui.utils.story_adapter import scene_to_gui
from src.core.game_session import GameSession
from src.core.save_system import SaveSystem


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
            {"slot": 1, "name": "Slot 1", "description": "EMPTY", "used": False},
            {"slot": 2, "name": "Slot 2", "description": "EMPTY", "used": False},
            {"slot": 3, "name": "Slot 3", "description": "EMPTY", "used": False},
        ]
        self.slot_data = [None, None, None]

        # Overwrite confirmation state
        self.overwrite_slot: Optional[int] = None   # slot number (1-3) being confirmed
        self.confirm_yes: bool = True                # True = YES highlighted

        # Setup fonts
        try:
            distant_galaxy_path = os.path.join(script_dir, 'gui/utils/fonts/SfDistantGalaxyAlternateItalic-3RDM.ttf')
            imperial_code_path = os.path.join(script_dir, 'gui/utils/fonts/ImperialCode-VGXpx.ttf')
            self.title_font = pygame.font.Font(distant_galaxy_path, 64)
            self.slot_font = pygame.font.Font(imperial_code_path, 40)
            self.desc_font = pygame.font.Font(imperial_code_path, 24)
            self.confirm_font = pygame.font.Font(imperial_code_path, 32)
        except:
            self.title_font = pygame.font.SysFont('arial', 64, bold=True)
            self.slot_font = pygame.font.SysFont('arial', 40, bold=True)
            self.desc_font = pygame.font.SysFont('arial', 24)
            self.confirm_font = pygame.font.SysFont('arial', 32, bold=True)

        # Colors
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 165, 0)
        self.selected_color = (0, 255, 255)
        self.used_color = (220, 100, 20)
        self.slot_rects = []

    def refresh_slots(self) -> None:
        """Read live save metadata and update slot display data."""
        self.slot_data = SaveSystem.get_all_slots()
        for i, data in enumerate(self.slot_data):
            if data is None:
                self.slots[i]["description"] = "EMPTY"
                self.slots[i]["used"] = False
            else:
                meta = data.get("metadata", {})
                title = meta.get("scene_title", "Unknown")
                darkness = meta.get("darkness", 0)
                self.slots[i]["description"] = f"{title}  |  Dark: {darkness}"
                self.slots[i]["used"] = True

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the save slot selection screen."""
        surface.fill(self.bg_color)

        # Title
        title = self.title_font.render("SELECT SAVE SLOT", True, self.selected_color)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        surface.blit(title, title_rect)

        # Slots
        self.slot_rects = []
        slot_width = 320
        slot_height = 220
        gap = 60
        total_width = (slot_width * 3) + (gap * 2)
        start_x = (self.width - total_width) // 2
        start_y = 280

        for i, slot in enumerate(self.slots):
            x = start_x + (i * (slot_width + gap))
            y = start_y
            slot_rect = pygame.Rect(x, y, slot_width, slot_height)
            self.slot_rects.append(slot_rect)

            if i == self.selected_slot:
                color = self.selected_color
                pygame.draw.rect(surface, color, slot_rect, 3)
            elif slot["used"]:
                color = self.used_color
                pygame.draw.rect(surface, color, slot_rect, 2)
            else:
                color = self.text_color
                pygame.draw.rect(surface, color, slot_rect, 2)

            slot_text = self.slot_font.render(f"SLOT {slot['slot']}", True, color)
            slot_text_rect = slot_text.get_rect(center=(x + slot_width // 2, y + 55))
            surface.blit(slot_text, slot_text_rect)

            desc_text = self.desc_font.render(slot["description"], True, color)
            desc_text_rect = desc_text.get_rect(center=(x + slot_width // 2, y + 130))
            surface.blit(desc_text, desc_text_rect)

            # Timestamp line for used slots
            if slot["used"] and self.slot_data[i]:
                ts = self.slot_data[i].get("timestamp", "")[:16].replace("T", "  ")
                ts_surf = self.desc_font.render(ts, True, color)
                ts_rect = ts_surf.get_rect(center=(x + slot_width // 2, y + 175))
                surface.blit(ts_surf, ts_rect)

        # Overwrite confirmation overlay
        if self.overwrite_slot is not None:
            self._draw_overwrite_prompt(surface)

    def _draw_overwrite_prompt(self, surface: pygame.Surface) -> None:
        box_w, box_h = 500, 200
        box_x = (self.width - box_w) // 2
        box_y = (self.height - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        # Semi-transparent backdrop
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (0, 0, 0), box_rect)
        pygame.draw.rect(surface, (220, 100, 20), box_rect, 2)

        prompt = self.confirm_font.render(
            f"OVERWRITE SLOT {self.overwrite_slot}?", True, (255, 200, 0)
        )
        surface.blit(prompt, prompt.get_rect(center=(self.width // 2, box_y + 55)))

        yes_color = (255, 215, 0) if self.confirm_yes else (150, 100, 0)
        no_color = (255, 215, 0) if not self.confirm_yes else (150, 100, 0)

        yes_surf = self.confirm_font.render("YES", True, yes_color)
        no_surf = self.confirm_font.render("NO", True, no_color)
        surface.blit(yes_surf, yes_surf.get_rect(center=(self.width // 2 - 80, box_y + 135)))
        surface.blit(no_surf, no_surf.get_rect(center=(self.width // 2 + 80, box_y + 135)))

    def handle_input(self, event: pygame.event.Event) -> Optional[int]:
        """
        Returns the selected slot number (1-3) when confirmed, -1 for back, None otherwise.
        """
        if self.overwrite_slot is not None:
            return self._handle_overwrite_input(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_slot = (self.selected_slot - 1) % len(self.slots)
            elif event.key == pygame.K_RIGHT:
                self.selected_slot = (self.selected_slot + 1) % len(self.slots)
            elif event.key == pygame.K_RETURN:
                return self._select_slot(self.selected_slot)
            elif event.key == pygame.K_ESCAPE:
                return -1

        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(event.pos):
                    self.selected_slot = i

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(self.slot_rects):
                    if rect.collidepoint(event.pos):
                        return self._select_slot(i)

        return None

    def _select_slot(self, index: int) -> Optional[int]:
        """Select a slot by zero-based index. Prompts for overwrite if occupied."""
        slot_num = self.slots[index]["slot"]
        if self.slots[index]["used"]:
            self.overwrite_slot = slot_num
            self.confirm_yes = True
            return None
        return slot_num

    def _handle_overwrite_input(self, event: pygame.event.Event) -> Optional[int]:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.confirm_yes = not self.confirm_yes
            elif event.key == pygame.K_RETURN:
                slot = self.overwrite_slot
                self.overwrite_slot = None
                return slot if self.confirm_yes else None
            elif event.key == pygame.K_ESCAPE:
                self.overwrite_slot = None
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

        # Active session — None until start_new_game() or load_game() fires
        self.session: Optional[GameSession] = None

        # Legacy references kept for backward compat with _start_scene / _load_scene_gui
        self.vader = None
        self.suit = None
        self.story = None
        
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
        self.save_slot_screen.refresh_slots()
        self.current_state = GameState.SAVE_SLOT_SELECT

    def on_continue(self) -> None:
        """Handle continue button press — loads most recent save."""
        slot = SaveSystem.get_most_recent_slot()
        if slot is not None:
            self.load_game(slot)
    
    def on_settings(self) -> None:
        """Handle settings button press"""
        self.current_state = GameState.SETTINGS
        print("Settings feature coming soon")
    
    def on_quit(self) -> None:
        """Handle quit button press"""
        self.running = False
    
    def on_story_choice_selected(self, choice_id: str) -> None:
        """Handle story choice selection — advance story or auto-continue."""
        if not self.session:
            return

        # Auto-next scenes synthesise a __continue__ choice; handle it directly
        if choice_id == "__continue__":
            scene = self.session.get_current_scene()
            next_id = scene.auto_next if scene else None
            if next_id:
                advanced = self.session.advance_to_scene(next_id)
                if advanced:
                    self._load_scene_into_gui(advanced)
                else:
                    self.return_to_menu()
            else:
                self.return_to_menu()
            return

        consequences = self.session.make_choice(choice_id)
        next_scene_id = consequences.get("next_scene")
        if next_scene_id:
            # make_choice already called start_scene internally — fetch without re-starting
            scene = self.session.story_system.scenes.get(next_scene_id)
            if scene and scene.trigger_combat:
                print(f"Combat trigger: {scene.trigger_combat}")
            elif scene:
                self._load_scene_into_gui(scene)
            else:
                self.return_to_menu()
        else:
            self.return_to_menu()
        SaveSystem.save(self.session)

    def _load_scene_into_gui(self, scene: Scene) -> None:
        """Push a Scene object into the dialogue screen."""
        choices = self.session.story_system.get_available_choices(scene.id)
        self.story_screen.set_scene(scene_to_gui(scene, choices))

    def _start_scene(self, scene_id: str) -> bool:
        """Legacy helper — start a scene via self.story and push to GUI."""
        if not self.story:
            return False
        success, _msg, _scene = self.story.start_scene(scene_id)
        if not success:
            self.return_to_menu()
            return False
        self._load_scene_gui(scene_id)
        return True

    def _load_scene_gui(self, scene_id: str) -> None:
        """Legacy helper — push an already-started scene into the dialogue screen."""
        if not self.story:
            return
        scene = self.story.scenes.get(scene_id)
        if not scene:
            self.return_to_menu()
            return
        choices = self.story.get_available_choices(scene_id)
        self.story_screen.set_scene(scene_to_gui(scene, choices))

    def start_new_game(self, slot: int) -> None:
        """Create a new GameSession, save immediately, and begin at the_void."""
        self.session = GameSession.new_game(slot)
        self.selected_slot = slot
        SaveSystem.save(self.session)
        scene = self.session.get_current_scene()
        if scene:
            self._load_scene_into_gui(scene)
        self.current_state = GameState.STORY_PLAYING

    def load_game(self, slot: int) -> None:
        """Load a saved GameSession and resume from the saved scene."""
        self.session = SaveSystem.load(slot)
        if self.session is None:
            return  # Stay on menu — load failed
        self.selected_slot = slot
        scene = self.session.get_current_scene()
        if scene:
            self._load_scene_into_gui(scene)
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
            if self.session:
                self.session.tick(dt)
    
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