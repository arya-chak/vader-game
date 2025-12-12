"""
Darth Vader Mask HUD Main Menu
A first-person view from inside Vader's mask with menu options displayed as HUD elements.
"""

import pygame
import math
from typing import Callable, Optional, List, Tuple


class RedLensEffect:
    """Draws a large glowing red ellipse lens."""
    
    def __init__(self, position: Tuple[int, int], width: int = 300, height: int = 350):
        self.position = position
        self.width = width
        self.height = height
        self.pulse_time = 0
        self.pulse_speed = 0.5
    
    def update(self, dt: float) -> None:
        """Update animation state."""
        self.pulse_time += dt * self.pulse_speed
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the glowing red ellipse lens."""
        # Create a temporary surface for the lens with alpha channel
        lens_surface = pygame.Surface(
            (self.width + 80, self.height + 80),
            pygame.SRCALPHA
        )
        center = (self.width // 2 + 40, self.height // 2 + 40)
        
        # Draw outer glow (darkest red, most transparent)
        pygame.draw.ellipse(
            lens_surface,
            (102, 0, 0, 80),
            (20, 20, self.width + 40, self.height + 40)
        )
        
        # Draw mid glow layers
        pygame.draw.ellipse(
            lens_surface,
            (153, 0, 0, 120),
            (30, 30, self.width + 20, self.height + 20)
        )
        pygame.draw.ellipse(
            lens_surface,
            (200, 30, 30, 150),
            (40, 40, self.width, self.height)
        )
        
        # Draw main lens body (bright red)
        pygame.draw.ellipse(
            lens_surface,
            (255, 51, 51, 220),
            (50, 50, self.width - 20, self.height - 20)
        )
        
        # Draw inner highlight
        pygame.draw.ellipse(
            lens_surface,
            (255, 100, 100, 200),
            (60, 60, self.width - 40, self.height - 40)
        )
        
        # Blit lens surface to main surface
        blit_position = (
            self.position[0] - self.width // 2 - 40,
            self.position[1] - self.height // 2 - 40
        )
        surface.blit(lens_surface, blit_position)
    
    def get_rect(self) -> pygame.Rect:
        """Get the bounding rect of the ellipse for text positioning."""
        return pygame.Rect(
            self.position[0] - self.width // 2,
            self.position[1] - self.height // 2,
            self.width,
            self.height
        )


class BreathingFog:
    """Manages subtle breathing fog effect that pulses over the lenses."""
    
    def __init__(self, lens_positions: List[Tuple[int, int]]):
        self.lens_positions = lens_positions
        self.animation_time = 0
        self.animation_speed = 0.3  # Controls breathing cycle speed
        self.max_opacity = 60  # Max alpha value for fog
    
    def update(self, dt: float) -> None:
        """Update fog animation."""
        self.animation_time += dt * self.animation_speed
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw breathing fog effect over lenses."""
        # Calculate opacity using sine wave (smooth breathing effect)
        opacity = int(self.max_opacity * (0.5 + 0.5 * math.sin(self.animation_time)))
        
        fog_width = 400
        fog_height = 250
        
        for pos in self.lens_positions:
            # Create fog surface
            fog_surface = pygame.Surface((fog_width, fog_height), pygame.SRCALPHA)
            
            # Draw semi-transparent fog wisps
            # Top wisp
            pygame.draw.ellipse(
                fog_surface,
                (255, 255, 255, opacity),
                (50, 20, 300, 80)
            )
            
            # Middle wisp
            pygame.draw.ellipse(
                fog_surface,
                (255, 255, 255, int(opacity * 0.7)),
                (30, 80, 340, 100)
            )
            
            # Bottom wisp
            pygame.draw.ellipse(
                fog_surface,
                (255, 255, 255, int(opacity * 0.5)),
                (60, 150, 280, 80)
            )
            
            # Blit fog to surface
            blit_pos = (pos[0] - fog_width // 2, pos[1] - fog_height // 2)
            surface.blit(fog_surface, blit_pos)


class MenuOption:
    """Represents a single menu option with glow effect."""
    
    def __init__(self, text: str, position: Tuple[int, int], 
                 font: pygame.font.Font, enabled: bool = True):
        self.text = text
        self.position = position
        self.font = font
        self.enabled = enabled
        self.is_hovered = False
        self.glow_intensity = 0
        self.target_glow = 0
    
    def set_hover(self, hovered: bool) -> None:
        """Set whether this option is hovered/selected."""
        self.is_hovered = hovered
        self.target_glow = 255 if hovered else 150
    
    def update(self, dt: float) -> None:
        """Smoothly animate glow intensity."""
        # Interpolate towards target glow
        diff = self.target_glow - self.glow_intensity
        self.glow_intensity += diff * 0.15  # Smooth animation
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the menu option with glow effect."""
        if not self.enabled:
            color = (102, 102, 102)  # Gray for disabled
            glow_alpha = 0
        else:
            color = (255, 165, 0)  # Orange/yellow color
            glow_alpha = int(self.glow_intensity * 0.7)
        
        # Render main text first to get rect (LEFT ALIGNED)
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(topleft=self.position)  # Changed from center to topleft
        
        # Draw glow ONLY when hovered/selected (glow_intensity > 0)
        if self.enabled and glow_alpha > 0 and self.is_hovered:
            for offset in [3, 2, 1]:
                glow_color = color
                glow_text = self.font.render(self.text, True, glow_color)
                glow_text.set_alpha(glow_alpha // (offset + 1))
                
                # Draw glow in 4 directions from top-left position
                for dx, dy in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
                    glow_rect = glow_text.get_rect(topleft=(self.position[0] + dx, self.position[1] + dy))
                    surface.blit(glow_text, glow_rect)
        
        # Draw main text on top
        surface.blit(text_surface, text_rect)
        
        # Store rect for hover detection
        self.rect = text_rect
    
    def collidepoint(self, point: Tuple[int, int]) -> bool:
        """Check if point collides with this option."""
        return hasattr(self, 'rect') and self.rect.collidepoint(point)


class MaskHUDMenu:
    """Main menu screen with Vader mask HUD effect."""
    
    def __init__(self, window_width: int = 1600, window_height: int = 900,
                 on_new_game: Optional[Callable] = None,
                 on_continue: Optional[Callable] = None,
                 on_settings: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None):
        
        self.width = window_width
        self.height = window_height
        
        # Callbacks for menu selections
        self.on_new_game = on_new_game
        self.on_continue = on_continue
        self.on_settings = on_settings
        self.on_quit = on_quit
        
        # Check if save exists for CONTINUE option
        self.has_save = self._check_save_exists()
        
        # Setup fonts
        # Using ImperialCode (Aurebesh-inspired) for menu and SF Distant Galaxy for title
        imperial_code_path = '../utils/fonts/ImperialCode-VGXpx.ttf'
        distant_galaxy_path = '../utils/fonts/SfDistantGalaxyAlternateItalic-3RDM.ttf'
        
        try:
            title_font = pygame.font.Font(distant_galaxy_path, 64)
            menu_font = pygame.font.Font(imperial_code_path, 32)  # Smaller menu font
        except FileNotFoundError as e:
            # Fallback to system font if file not found
            print(f"Warning: Font file not found: {e}")
            print("Falling back to Arial")
            title_font = pygame.font.SysFont('arial', 64, bold=True)
            menu_font = pygame.font.SysFont('arial', 32, bold=True)
        
        # Red lens positions (larger, centered on screen)
        lens_width = 600   # Much larger
        lens_height = 315  # Keep ratio
        lens_spacing = 250  # Larger gap between lenses
        
        left_lens_x = (self.width // 2) - (lens_width // 2) - (lens_spacing // 2)
        right_lens_x = (self.width // 2) + (lens_width // 2) + (lens_spacing // 2)
        lens_y = self.height // 2 - 50  # Slightly higher to leave room for bottom menu
        
        self.lens_positions = [
            (left_lens_x, lens_y),   # Left lens
            (right_lens_x, lens_y),  # Right lens
        ]
        
        # Create lens effects
        self.left_lens = RedLensEffect(self.lens_positions[0], width=lens_width, height=lens_height)
        self.right_lens = RedLensEffect(self.lens_positions[1], width=lens_width, height=lens_height)
        
        # Create breathing fog (disabled for now)
        # self.fog = BreathingFog(self.lens_positions)
        
        # Create menu options (positioned on left side of left lens, top to bottom)
        left_eye_left_edge = left_lens_x - (lens_width // 2)
        menu_x = left_eye_left_edge + 80  # Closer to left edge
        menu_start_y = lens_y - 85
        menu_spacing = 45
        
        self.menu_options = [
            MenuOption("NEW GAME", (menu_x, menu_start_y), menu_font, enabled=True),
            MenuOption("CONTINUE", (menu_x, menu_start_y + menu_spacing), menu_font, enabled=self.has_save),
            MenuOption("SETTINGS", (menu_x, menu_start_y + menu_spacing * 2), menu_font, enabled=True),
            MenuOption("QUIT", (menu_x, menu_start_y + menu_spacing * 3), menu_font, enabled=True),
        ]
        
        # Store credit text info for right eye
        self.credit_font = menu_font
        self.credit_text = ["Field", "Day", "Studios"]
        self.credit_color = (255, 165, 0)  # Same orange/yellow
        right_eye_right_edge = right_lens_x + (lens_width // 2)
        self.credit_x = right_eye_right_edge - 50  # Similar distance from edge as left menu
        self.credit_start_y = lens_y - 63.75
        
        self.selected_index = 0
        self.title_text = "MASK OF VADER"
        self.title_font = title_font
        
        # Colors
        self.background_color = (0, 0, 0)  # Pure black
        self.red_tint_color = (255, 0, 0)
        self.red_tint_alpha = 0  # No tint overlay for now
        
        # Update initial menu state
        self._update_menu_selection()
        
        # Audio (placeholder - will load if files exist)
        self.breathing_sound = None
        self.hum_sound = None
        self.click_sound = None
        self._load_audio()
        
        # Play background sounds
        self._play_background_sounds()
    
    def _check_save_exists(self) -> bool:
        """Check if a save file exists."""
        import os
        save_path = "save/vader_save.dat"
        return os.path.exists(save_path)
    
    def _load_audio(self) -> None:
        """Load audio files if they exist."""
        try:
            import os
            audio_dir = "gui/assets/sounds"
            
            if os.path.exists(f"{audio_dir}/breathing.wav"):
                self.breathing_sound = pygame.mixer.Sound(f"{audio_dir}/breathing.wav")
            
            if os.path.exists(f"{audio_dir}/hum.wav"):
                self.hum_sound = pygame.mixer.Sound(f"{audio_dir}/hum.wav")
            
            if os.path.exists(f"{audio_dir}/beep.wav"):
                self.click_sound = pygame.mixer.Sound(f"{audio_dir}/beep.wav")
        except Exception as e:
            print(f"Warning: Could not load audio files: {e}")
    
    def _play_background_sounds(self) -> None:
        """Play background breathing and hum sounds in loop."""
        if self.breathing_sound:
            self.breathing_sound.set_volume(0.4)
            self.breathing_sound.play(-1)  # Loop indefinitely
        
        if self.hum_sound:
            self.hum_sound.set_volume(0.2)
            self.hum_sound.play(-1)  # Loop indefinitely
    
    def _stop_background_sounds(self) -> None:
        """Stop background sounds."""
        if self.breathing_sound:
            self.breathing_sound.stop()
        if self.hum_sound:
            self.hum_sound.stop()
    
    def _update_menu_selection(self) -> None:
        """Update menu option hover states based on selection."""
        for i, option in enumerate(self.menu_options):
            option.set_hover(i == self.selected_index)
    
    def _play_click_sound(self) -> None:
        """Play click sound effect."""
        if self.click_sound:
            self.click_sound.set_volume(0.6)
            self.click_sound.play()
    
    def update(self, dt: float) -> None:
        """Update all components."""
        self.left_lens.update(dt)
        self.right_lens.update(dt)
        # self.fog.update(dt)
        
        for option in self.menu_options:
            option.update(dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entire menu screen."""
        # 1. Draw black background
        surface.fill(self.background_color)
        
        # 2. Draw red lenses
        self.left_lens.draw(surface)
        self.right_lens.draw(surface)
        
        # 3. Draw title at top
        title_surface = self.title_font.render(self.title_text, True, (0, 255, 255))
        title_rect = title_surface.get_rect(center=(self.width // 2, 100))
        surface.blit(title_surface, title_rect)
        
        # 4. Draw menu options (left eye)
        for option in self.menu_options:
            option.draw(surface)
        
        # 5. Draw credit text (right eye) - right aligned
        credit_y = self.credit_start_y
        for credit_line in self.credit_text:
            credit_surface = self.credit_font.render(credit_line, True, self.credit_color)
            credit_rect = credit_surface.get_rect(topright=(self.credit_x, credit_y))
            surface.blit(credit_surface, credit_rect)
            credit_y += 45  # Same spacing as menu
        
        # 6. Draw red tint overlay (final layer)
        tint_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        tint_surface.fill((self.red_tint_color[0], self.red_tint_color[1], 
                          self.red_tint_color[2], self.red_tint_alpha))
        surface.blit(tint_surface, (0, 0))
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard and mouse input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                self._update_menu_selection()
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                self._update_menu_selection()
            
            elif event.key == pygame.K_RETURN:
                self.select_option()
            
            elif event.key == pygame.K_ESCAPE:
                self.select_quit()
        
        elif event.type == pygame.MOUSEMOTION:
            # Update selection based on mouse position
            for i, option in enumerate(self.menu_options):
                if option.collidepoint(event.pos):
                    if self.selected_index != i:
                        self.selected_index = i
                        self._update_menu_selection()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.select_option()
    
    def select_option(self) -> None:
        """Handle selection of current menu option."""
        selected_option = self.menu_options[self.selected_index]
        
        if not selected_option.enabled:
            return
        
        self._play_click_sound()
        self._stop_background_sounds()
        
        if selected_option.text == "NEW GAME":
            if self.on_new_game:
                self.on_new_game()
        
        elif selected_option.text == "CONTINUE":
            if self.on_continue:
                self.on_continue()
        
        elif selected_option.text == "SETTINGS":
            if self.on_settings:
                self.on_settings()
        
        elif selected_option.text == "QUIT":
            self.select_quit()
    
    def select_quit(self) -> None:
        """Quit the game."""
        self._play_click_sound()
        self._stop_background_sounds()
        if self.on_quit:
            self.on_quit()
        else:
            pygame.quit()
            exit()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self._stop_background_sounds()


# Example usage / testing
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    
    # Create window
    screen = pygame.display.set_mode((1600, 900))
    pygame.display.set_caption("Darth Vader: Mask of Vader")
    clock = pygame.time.Clock()
    
    # Callbacks for menu
    def on_new_game():
        print("Starting new game...")
        return True
    
    def on_continue():
        print("Continuing saved game...")
        return True
    
    def on_settings():
        print("Opening settings...")
        return True
    
    def on_quit():
        print("Quitting game...")
    
    # Create menu
    menu = MaskHUDMenu(
        on_new_game=on_new_game,
        on_continue=on_continue,
        on_settings=on_settings,
        on_quit=on_quit
    )
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            menu.handle_input(event)
        
        menu.update(dt)
        menu.draw(screen)
        pygame.display.flip()
    
    menu.cleanup()
    pygame.quit()