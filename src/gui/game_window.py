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
        from src.story.mission_kyber import create_kyber_mission_scenes
        
        # Initialize game systems
        self.vader = DarthVader()
        self.suit = SuitSystem()
        self.force_powers = ForcePowerSystem()
        self.story_system = StorySystem(self.vader, self.suit)
        
        # Load opening scenes
        opening_scenes = create_opening_scenes()
        for scene_id, scene in opening_scenes.items():
            self.story_system.register_scene(scene)

        # Load Kyber mission scenes
        kyber_scenes = create_kyber_mission_scenes()
        for scene_id, scene in kyber_scenes.items():
            self.story_system.register_scene(scene)
        
        print(f"✓ Loaded {len(opening_scenes)} opening scenes")
        print(f"✓ Loaded {len(kyber_scenes)} Kyber mission scenes")

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

        # CHECK FOR COMBAT TRIGGER BEFORE SHOWING STORY
        if hasattr(scene, 'trigger_combat') and scene.trigger_combat:
            print(f"🗡️ Combat triggered in scene: {scene_id}")
            self._start_combat(scene.trigger_combat, scene.auto_next)
            return  # Don't show story screen, go straight to combat

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

    def _start_combat(self, combat_trigger: dict, next_scene_after_combat: str):
        """
        Start a combat encounter (regular or boss fight).
    
        Args:
            combat_trigger: Dict with combat parameters from scene
            next_scene_after_combat: Scene to go to after combat ends
        """
        from src.combat.combat_system import CombatSystem, create_enemy, EnemyType
    
        # Check if this is a boss fight
        if combat_trigger.get('boss_fight'):
            self._start_boss_fight(combat_trigger, next_scene_after_combat)
            return
    
        # Regular combat
        # Initialize combat system if not already done
        if not hasattr(self, 'combat_system'):
            self.combat_system = CombatSystem(self.vader, self.suit, self.force_powers)
    
        # Create enemies based on trigger
        enemies = self._create_enemies_from_trigger(combat_trigger)
    
        # Start combat in the combat system
        self.combat_system.start_combat(enemies)
    
        # Store where to go after combat
        self._scene_after_combat = next_scene_after_combat
    
        # Switch to combat screen
        combat_screen = CombatScreen(self, self.vader, self.suit, self.force_powers)
        combat_screen.set_enemies(enemies)
        combat_screen.on_action_selected = self._handle_combat_action
        combat_screen.current_turn = self.combat_system.combat_state.turn_number
        self.current_screen = combat_screen
    
        print(f"⚔️ Combat started with {len(enemies)} enemies")

    def _create_enemies_from_trigger(self, trigger_info: dict) -> list:
        """Create enemy list from combat trigger data"""
        from src.combat.combat_system import create_enemy, EnemyType
    
        enemies = []
        enemy_types = trigger_info.get('enemy_types', ['stormtrooper'])
    
        for enemy_type_str in enemy_types:
            # Map string to EnemyType enum
            if enemy_type_str == "pirate_thug":
                enemy = create_enemy(EnemyType.REBEL_SOLDIER)
                enemy.name = "Pirate Thug"
            elif enemy_type_str == "pirate_leader":
                enemy = create_enemy(EnemyType.REBEL_VETERAN)
                enemy.name = "Pirate Leader"
                enemy.max_hp = 50
                enemy.current_hp = 50
            elif enemy_type_str == "clone_trooper":
                enemy = create_enemy(EnemyType.STORMTROOPER)
                enemy.name = "Clone Trooper"
                enemy.max_hp = 40
                enemy.current_hp = 40
            else:
                # Default to stormtrooper
                enemy = create_enemy(EnemyType.STORMTROOPER)
        
            enemies.append(enemy)
    
        return enemies

    def _handle_combat_action(self, action_id: str):
        """Handle combat action selection"""
        print(f"Combat action: {action_id}")
    
        result = None
    
        if action_id == "attack":
            # Find first alive enemy
            alive = [e for e in self.combat_system.combat_state.enemies if e.is_alive]
            if alive:
                result = self.combat_system.vader_attack(alive[0].id)
                self.current_screen.add_to_log(f"⚔️ Attacked {result['target']} for {result['damage']} damage")
    
        elif action_id == "force_push":
            result = self.combat_system.vader_use_force_power("force_push")
            if result.get('success'):
                targets = len(result.get('targets_hit', []))
                self.current_screen.add_to_log(f"🌊 Force Push hit {targets} enemies")
    
        elif action_id == "force_choke":
            alive = [e for e in self.combat_system.combat_state.enemies if e.is_alive]
            if alive:
                result = self.combat_system.vader_use_force_power("force_choke", alive[0].id)
                if result.get('success'):
                    self.current_screen.add_to_log(f"🫱 Force Choke activated!")
    
        elif action_id == "defend":
            self.combat_system.vader_defend()
            self.current_screen.add_to_log("🛡️ Vader defends")
    
        elif action_id == "meditate":
            result = self.combat_system.vader_meditate()
            self.current_screen.add_to_log(f"🧘 Restored {result['fp_restored']} FP")
    
        elif action_id == "retreat":
            result = self.combat_system.vader_retreat()
            if result.get('success'):
                self._end_combat(victory=False, fled=True)
                return
    
        # Enemy turn
        self.combat_system.enemy_turn()
    
        # Add enemy actions to log
        for log in self.combat_system.combat_log[-3:]:
            if "enemy" in log.lower() or "attacks" in log.lower():
                self.current_screen.add_to_log(log)
    
        # End turn
        self.combat_system.end_turn()
        self.current_screen.current_turn = self.combat_system.combat_state.turn_number
    
        # Check if combat ended
        if not self.combat_system.combat_state.combat_active:
            victory = self.combat_system.combat_state.victory_type in ["total_victory", "intimidation_victory"]
            self._end_combat(victory=victory, fled=False)

    def _end_combat(self, victory: bool, fled: bool):
        """Handle end of combat"""
        if victory:
            print("🏆 Combat Victory!")
            # Return to story at next scene
            if hasattr(self, '_scene_after_combat') and self._scene_after_combat:
                self.current_scene_id = self._scene_after_combat
                self._show_story_scene(self._scene_after_combat)
        elif fled:
            print("💨 Fled from combat")
            # Could handle retreat differently
            if hasattr(self, '_scene_after_combat') and self._scene_after_combat:
                self._show_story_scene(self._scene_after_combat)
        else:
            print("💀 Combat Defeat")
            # Game over screen or respawn
            self._show_main_menu()

    def _start_boss_fight(self, combat_trigger: dict, next_scene_after_combat: str):
        """
        Start a boss fight encounter.
    
        Args:
            combat_trigger: Dict with boss fight parameters
            next_scene_after_combat: Scene to go to after boss is defeated
        """
        from src.combat.boss_fight import (
            BossFightSystem,
            create_infila_first_duel,
            create_infila_final_phase1,
            create_infila_final_phase2
        )
    
        # Initialize boss fight system if not already done
        if not hasattr(self, 'boss_system'):
            self.boss_system = BossFightSystem(self.vader, self.suit)
    
        boss_id = combat_trigger.get('boss_id')
        scripted_loss = combat_trigger.get('scripted_loss', False)
        hp_threshold_for_pause = combat_trigger.get('hp_threshold_for_pause')
    
        # Create the boss
        boss = None
        if boss_id == 'infila_first':
            boss = create_infila_first_duel()
        elif boss_id == 'infila_final_phase1':
            boss = create_infila_final_phase1()
        elif boss_id == 'infila_final_easy':
            # Get saved HP from water tank choice
            saved_hp = getattr(self, '_saved_boss_hp_percent', 60)
            boss = create_infila_final_phase2(
                water_tank_destroyed=True,
                starting_hp_percent=saved_hp
            )
        elif boss_id == 'infila_final_hard':
            saved_hp = getattr(self, '_saved_boss_hp_percent', 60)
            boss = create_infila_final_phase2(
                water_tank_destroyed=False,
                starting_hp_percent=saved_hp
            )
    
        if not boss:
            print(f"❌ Unknown boss_id: {boss_id}")
            return
    
        # Start boss fight
        self.boss_system.start_boss_fight(boss, scripted_loss=scripted_loss)
    
        # Store combat info
        self._scene_after_combat = next_scene_after_combat
        self._boss_fight_active = True
        self._boss_scripted_loss = scripted_loss
        self._boss_hp_pause_threshold = hp_threshold_for_pause
    
        # Switch to combat screen with boss
        combat_screen = CombatScreen(self, self.vader, self.suit, self.force_powers)
        combat_screen.set_boss(boss)  # We'll add this method
        combat_screen.on_action_selected = self._handle_boss_action
        combat_screen.current_turn = self.boss_system.turn_number
        combat_screen.is_boss_fight = True
        self.current_screen = combat_screen
    
        print(f"👑 Boss fight started: {boss.name}")

    def _handle_boss_action(self, action_id: str):
        """Handle boss fight action selection"""
        print(f"Boss combat action: {action_id}")
    
        # Check for HP pause threshold BEFORE action
        if self._boss_hp_pause_threshold:
            hp_percent = (self.boss_system.current_boss.current_hp / 
                         self.boss_system.current_boss.max_hp) * 100
        
            if hp_percent <= self._boss_hp_pause_threshold:
                # PAUSE for story choice!
                self._saved_boss_hp_percent = hp_percent
                self._boss_hp_pause_threshold = None  # Don't trigger again
                print(f"⏸️ Combat paused at {hp_percent:.0f}% HP for story choice")
            
                # Return to story for the choice
                if hasattr(self, '_scene_after_combat'):
                    self._show_story_scene(self._scene_after_combat)
                return
    
        result = None
    
        if action_id == "attack":
            damage = 40 + (self.vader.stats.strength * 2)
            result = self.boss_system.vader_attacks_boss(damage)
            self.current_screen.add_to_log(f"⚔️ Dealt {result['damage']} damage to boss")
    
        elif action_id == "force_push":
            result = self.boss_system.vader_uses_force_on_boss("Force Push", 15)
            self.vader.spend_force_points(10)
            self.current_screen.add_to_log(f"🌊 Force Push: {result['damage']} damage")
    
        elif action_id == "force_choke":
            result = self.boss_system.vader_uses_force_on_boss("Force Choke", 35)
            self.vader.spend_force_points(20)
            self.current_screen.add_to_log(f"🫱 Force Choke: {result['damage']} damage")
    
        elif action_id == "defend":
            self.current_screen.add_to_log("🛡️ Vader defends")
    
        elif action_id == "meditate":
            self.vader.restore_force_points(30)
            self.current_screen.add_to_log(f"🧘 Restored 30 FP")
    
        elif action_id == "retreat":
            # Can't retreat from boss fights
            self.current_screen.add_to_log("❌ Cannot retreat from this fight!")
            return
    
        # Check for scripted loss BEFORE boss turn
        if self._boss_scripted_loss and self.boss_system.check_scripted_loss():
            print("💀 Scripted loss triggered!")
            self.current_screen.add_to_log("Your leg gives out! You fall...")
            # Wait a moment then return to story
            pygame.time.wait(2000)
            self._boss_fight_active = False
            if hasattr(self, '_scene_after_combat'):
                self._show_story_scene(self._scene_after_combat)
            return
    
        # Boss's turn
        boss_action = self.boss_system.boss_choose_action()
        if boss_action:
            result = self.boss_system.execute_boss_action(boss_action)
            self.current_screen.add_to_log(f"🔥 {self.boss_system.current_boss.name} uses {boss_action.name}!")
        
            if result.get('vader_defeated'):
                self._end_combat(victory=False, fled=False)
                return
        else:
            # Basic boss attack
            damage = self.boss_system.current_boss.base_damage
            self.vader.take_damage(damage)
            self.current_screen.add_to_log(f"⚔️ Boss attacks for {damage} damage")
    
        # End turn
        self.boss_system.end_turn()
        self.current_screen.current_turn = self.boss_system.turn_number
    
        # FP regeneration
        fp_regen = self.vader.regenerate_force_points(self.suit)
        if fp_regen > 0:
            self.current_screen.add_to_log(f"🔵 +{fp_regen} FP")

        # Check if boss defeated
        if self.boss_system.current_boss.current_hp <= 0:
            print("🏆 Boss Defeated!")
            self._boss_fight_active = False
            # Return to story
            if hasattr(self, '_scene_after_combat'):
                self._show_story_scene(self._scene_after_combat)