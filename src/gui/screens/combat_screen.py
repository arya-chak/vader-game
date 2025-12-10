# """
# Combat screen - tactical turn-based combat display.
# Shows Vader status, enemies, and combat actions.
# """

# import pygame
# from ..utils import (
#     BLACK, WHITE, SITH_RED, IMPERIAL_RED, GRAY,
#     normal_font, small_font, header_font
# )
# from ..components import HealthBar, ChoiceButton


# class CombatScreen:
#     """
#     Combat screen with status bars, enemy display, and action buttons.
#     """
    
#     def __init__(self, window, vader, suit, force_powers):
#         """
#         Initialize combat screen.
        
#         Args:
#             window: GameWindow instance
#             vader: DarthVader instance
#             suit: SuitSystem instance
#             force_powers: ForcePowerSystem instance
#         """
#         self.window = window
#         self.width = window.width
#         self.height = window.height
        
#         # Game systems
#         self.vader = vader
#         self.suit = suit
#         self.force_powers = force_powers
        
#         # Combat state
#         self.enemies = []
#         self.boss = None
#         self.is_boss_fight = False
#         self.current_turn = 1
#         self.combat_log = []
        
#         # Create UI components
#         self._create_layout()
        
#         # Callback for actions
#         self.on_action_selected = None
    
#     def _create_layout(self):
#         """Create combat UI layout"""
#         # Vader status panel (left side)
#         status_x = 20
#         status_y = 20
        
#         # Status bars
#         bar_width = 220
#         bar_height = 30
        
#         self.hp_bar = HealthBar(status_x + 40, status_y + 80, bar_width, bar_height, "HP")
#         self.fp_bar = HealthBar(status_x + 40, status_y + 130, bar_width, bar_height, "FP")
#         self.suit_bar = HealthBar(status_x + 40, status_y + 180, bar_width, bar_height, "Suit")
        
#         # Combat action buttons (bottom)
#         self.action_buttons = []
#         button_width = 180
#         button_height = 50
#         button_y = self.height - 100
#         spacing = 200
#         start_x = 50
        
#         actions = [
#             {'text': '⚔️ Attack', 'id': 'attack'},
#             {'text': '🌊 Force Push', 'id': 'force_push'},
#             {'text': '🫱 Force Choke', 'id': 'force_choke'},
#             {'text': '🛡️ Defend', 'id': 'defend'},
#             {'text': '🧘 Meditate', 'id': 'meditate'},
#             {'text': '💨 Retreat', 'id': 'retreat'}
#         ]
        
#         for i, action in enumerate(actions):
#             x = start_x + (i * spacing)
#             button = ChoiceButton(x, button_y, button_width, button_height, action['text'], action['id'])
#             self.action_buttons.append(button)
    
#     def set_enemies(self, enemies: list):
#         """
#         Set the list of enemies to display.
        
#         Args:
#             enemies: List of Enemy objects from combat system
#         """
#         self.enemies = enemies
    
#     def add_to_log(self, message: str):
#         """Add message to combat log"""
#         self.combat_log.append(message)
#         # Keep only last 5 messages
#         if len(self.combat_log) > 5:
#             self.combat_log.pop(0)
    
#     def handle_event(self, event: pygame.event.Event):
#         """Handle input events"""
#         for button in self.action_buttons:
#             if button.handle_event(event):
#                 if self.on_action_selected:
#                     self.on_action_selected(button.choice_id)
    
#     def update(self):
#         """Update combat display"""
#         # Update Vader's status bars
#         self.hp_bar.set_value(self.vader.current_health, self.vader.max_health)
#         self.fp_bar.set_value(self.vader.current_force_points, self.vader.max_force_points)
#         self.suit_bar.set_value(self.suit.integrity, 100)
    
#     def render(self, surface: pygame.Surface):
#         """Draw the combat screen"""
#         surface.fill(BLACK)
        
#         # Turn number at top
#         turn_font = header_font()
#         turn_text = turn_font.render(f"TURN {self.current_turn}", True, SITH_RED)
#         turn_rect = turn_text.get_rect(center=(self.width // 2, 30))
#         surface.blit(turn_text, turn_rect)
        
#         # Vader status panel
#         self._render_vader_status(surface)
        
#         # Enemy panel
#         self._render_enemies(surface)
        
#         # Combat log
#         self._render_combat_log(surface)
        
#         # Action buttons
#         for button in self.action_buttons:
#             button.render(surface)
    
#     def _render_vader_status(self, surface: pygame.Surface):
#         """Render Vader's status panel"""
#         # Panel background
#         panel_rect = pygame.Rect(10, 10, 290, 250)
#         pygame.draw.rect(surface, (20, 20, 20), panel_rect)
#         pygame.draw.rect(surface, WHITE, panel_rect, 2)
        
#         # Title
#         font = normal_font()
#         title = font.render("DARTH VADER", True, SITH_RED)
#         surface.blit(title, (30, 30))
        
#         # Status bars
#         self.hp_bar.render(surface)
#         self.fp_bar.render(surface)
#         self.suit_bar.render(surface)
        
#         # Additional info
#         small = small_font()
#         info_y = 230
        
#         pain_text = small.render(f"Pain: {self.suit.current_pain_level}%", True, GRAY)
#         surface.blit(pain_text, (30, info_y))
        
#         rage_text = small.render(f"Rage: {self.vader.psychological_state.rage}", True, IMPERIAL_RED)
#         surface.blit(rage_text, (170, info_y))
    
#     def _render_enemies(self, surface: pygame.Surface):
#         """Render enemy list"""
#         # Panel background
#         enemy_x = self.width - 410
#         panel_rect = pygame.Rect(enemy_x, 10, 400, 400)
#         pygame.draw.rect(surface, (20, 20, 20), panel_rect)
#         pygame.draw.rect(surface, WHITE, panel_rect, 2)
    
#         # Title
#         font = normal_font()
#         if self.is_boss_fight and self.boss:
#             title = font.render(f"👑 BOSS: {self.boss.name}", True, SITH_RED)
#         else:
#             title = font.render("ENEMIES", True, IMPERIAL_RED)
#         surface.blit(title, (enemy_x + 20, 30))
    
#         # Enemy/Boss display
#         small = small_font()
#         y_offset = 70
    
#         if self.is_boss_fight and self.boss:
#             # Show boss info
#             name_text = small.render(self.boss.title, True, WHITE)
#             surface.blit(name_text, (enemy_x + 20, y_offset))
        
#             # HP bar
#             hp_text = small.render(f"HP: {self.boss.current_hp}/{self.boss.max_hp}", True, WHITE)
#             surface.blit(hp_text, (enemy_x + 20, y_offset + 25))
        
#             # Phase
#             phase_text = small.render(f"Phase: {self.boss.current_phase.name}", True, IMPERIAL_RED)
#             surface.blit(phase_text, (enemy_x + 20, y_offset + 50))
        
#         else:
#             # Regular enemies
#             for i, enemy in enumerate(self.enemies):
#                 if not enemy.is_alive:
#                     text = small.render(f"{i+1}. {enemy.name}: ☠️ DEAD", True, GRAY)
#                     surface.blit(text, (enemy_x + 20, y_offset))
#                 else:
#                     name_text = small.render(f"{i+1}. {enemy.name}", True, WHITE)
#                     surface.blit(name_text, (enemy_x + 20, y_offset))
                
#                     hp_text = small.render(f"HP: {enemy.current_hp}/{enemy.max_hp}", True, WHITE)
#                     surface.blit(hp_text, (enemy_x + 20, y_offset + 20))
                
#                     if hasattr(enemy, 'is_helpless') and enemy.is_helpless():
#                         status = small.render("[HELPLESS]", True, SITH_RED)
#                         surface.blit(status, (enemy_x + 250, y_offset + 20))
            
#                 y_offset += 60
    
#     def _render_combat_log(self, surface: pygame.Surface):
#         """Render combat log"""
#         log_x = 320
#         log_y = self.height - 300
#         log_width = self.width - 740
#         log_height = 180
        
#         # Background
#         log_rect = pygame.Rect(log_x, log_y, log_width, log_height)
#         pygame.draw.rect(surface, (20, 20, 20), log_rect)
#         pygame.draw.rect(surface, WHITE, log_rect, 2)
        
#         # Title
#         font = small_font()
#         title = font.render("COMBAT LOG", True, WHITE)
#         surface.blit(title, (log_x + 10, log_y + 10))
        
#         # Log messages
#         y_offset = log_y + 40
#         for message in self.combat_log:
#             msg_text = font.render(message, True, GRAY)
#             surface.blit(msg_text, (log_x + 10, y_offset))
#             y_offset += 25

#     def set_boss(self, boss):
#         """
#         Set the boss enemy to display.
    
#         Args:
#             boss: BossEnemy object from boss_fight system
#         """
#         self.boss = boss
#         self.is_boss_fight = True
#         # Convert boss to enemy-like object for display
#         self.enemies = [boss]  # Treat boss as single enemy for rendering