# """
# Star Wars: Darth Vader RPG - Main Entry Point
# Launches the GUI version of the game.
# """

# from src.gui import GameWindow


# def main():
#     """
#     Main function - initializes and runs the game.
#     """
#     # Create the game window
#     window = GameWindow(
#         width=1280,
#         height=720,
#         title="Star Wars: Darth Vader - The Dark Times"
#     )
    
#     # Start the game loop
#     window.run()


# if __name__ == "__main__":
#     main()

"""
Star Wars: Darth Vader RPG - Main Entry Point
Terminal-based text adventure game with integrated combat.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from character.vader import DarthVader
from character.suit_system import SuitSystem
from character.force_powers import ForcePowerSystem
from story.story_system import StorySystem
from story.opening_scenes import create_opening_scenes
from story.mission_kyber import create_kyber_mission_scenes
from combat.combat_system import CombatSystem, create_enemy, EnemyType
from combat.boss_fight import BossFightSystem, create_infila_first_duel, create_infila_final_phase1, create_infila_final_phase2


class TerminalGame:
    """
    Terminal-based game runner for Darth Vader RPG.
    Manages the main game loop, user input, and scene progression.
    """
    
    def __init__(self):
        """Initialize the game systems"""
        self.vader = DarthVader()
        self.suit = SuitSystem()
        self.force_powers = ForcePowerSystem()
        self.story_system = StorySystem(self.vader, self.suit)
        self.combat_system = CombatSystem(self.vader, self.suit, self.force_powers)
        self.boss_system = BossFightSystem(self.vader, self.suit)
        
        self.current_scene_id = None
        self.running = True
        self._saved_boss_hp_percent = 60  # For multi-phase boss fights
    
    def load_all_scenes(self):
        """Load all story scenes into the system"""
        # Load opening scenes
        opening_scenes = create_opening_scenes()
        for scene_id, scene in opening_scenes.items():
            self.story_system.register_scene(scene)
        
        # Load Kyber mission scenes
        kyber_scenes = create_kyber_mission_scenes()
        for scene_id, scene in kyber_scenes.items():
            self.story_system.register_scene(scene)
        
        print(f"✓ Loaded {len(opening_scenes)} opening scenes")
        print(f"✓ Loaded {len(kyber_scenes)} Kyber mission scenes\n")
    
    def display_scene(self, scene_id: str):
        """Display a story scene and handle dialogue"""
        # Start the scene in the story system
        success, msg, scene = self.story_system.start_scene(scene_id)
        
        if not success:
            print(f"Error loading scene: {msg}")
            return False
        
        # Get dialogue for this scene
        dialogue_lines = self.story_system.get_dialogue_for_scene(scene_id)
        
        # Display dialogue
        print("\n" + "="*70)
        print(f"{scene.title.upper()}")
        print("="*70 + "\n")
        
        for line in dialogue_lines:
            if line.speaker != "Narrator":
                print(f"{line.speaker}: {line.text}")
            else:
                print(f"{line.text}")
            
            # Add internal thought if present
            if line.internal_thought:
                print(f"  💭 {line.internal_thought}")
        
        print()
        return True
    
    def show_choices(self, scene_id: str) -> str:
        """Display available choices and get user input"""
        choices = self.story_system.get_available_choices(scene_id)
        
        if not choices:
            return None
        
        # Display choices
        print("-"*70)
        choice_map = {}
        
        for i, choice in enumerate(choices, 1):
            choice_map[str(i)] = choice.id
            
            # Extract tag from choice text if present (e.g., [RAGE])
            text = choice.text
            if text.startswith('['):
                end_bracket = text.find(']')
                if end_bracket != -1:
                    display_text = text[end_bracket+1:].strip()
                else:
                    display_text = text
            else:
                display_text = text
            
            print(f"{i}. {display_text}")
        
        print("-"*70)
        
        # Get user input
        while True:
            user_input = input("\nChoose an option (enter number): ").strip()
            if user_input in choice_map:
                return choice_map[user_input]
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(choices)}")
    
    def handle_story_choice(self, scene_id: str, choice_id: str) -> str:
        """Process a story choice and return next scene ID"""
        success, msg, consequences = self.story_system.make_choice(scene_id, choice_id)
        
        if not success:
            print(f"Choice error: {msg}")
            return None
        
        # Get next scene from consequences
        next_scene = consequences.get('next_scene')
        return next_scene
    
    def print_combat_status(self):
        """Print current combat status"""
        print("\n" + "─"*70)
        print(f"TURN {self.combat_system.combat_state.turn_number}")
        print("─"*70)
        print(f"VADER: {self.vader.current_health}/{self.vader.max_health} HP | "
              f"{self.vader.current_force_points}/{self.vader.max_force_points} FP | "
              f"Suit: {self.suit.integrity}%")
        
        print("\nENEMIES:")
        alive_count = 0
        for i, enemy in enumerate(self.combat_system.combat_state.enemies, 1):
            if enemy.is_alive:
                alive_count += 1
                status = ""
                if enemy.is_helpless():
                    status = " [HELPLESS - Can Execute!]"
                print(f"  {i}. {enemy.name}: {enemy.current_hp}/{enemy.max_hp} HP{status}")
            else:
                print(f"  {i}. {enemy.name}: DEAD ☠️")
        
        print()
        return alive_count > 0
    
    def print_extended_status(self):
        """Print full extended status"""
        print("\n" + "─"*70)
        print(f"VADER STATUS:")
        print(f"  Health: {self.vader.current_health}/{self.vader.max_health}")
        print(f"  Force Points: {self.vader.current_force_points}/{self.vader.max_force_points}")
        print(f"  Suit Integrity: {self.suit.integrity}%")
        print(f"  Pain Level: {self.suit.current_pain_level}%")
        print(f"  Psychological State:")
        print(f"    - Darkness: {self.vader.psychological_state.darkness}")
        print(f"    - Control: {self.vader.psychological_state.control}")
        print(f"    - Rage: {self.vader.psychological_state.rage}")
        print(f"    - Suppression: {self.vader.psychological_state.suppression}")
        print("─"*70)
    
    def get_combat_action(self):
        """Get player combat action"""
        print("ACTIONS:")
        print("  1. Attack (lightsaber)")
        print("  2. Force Push (area attack)")
        print("  3. Force Choke (single target)")
        print("  4. Defend")
        if self.vader.current_force_points < self.vader.max_force_points * 0.5:
            print("  5. Meditate")
        print("  6. Attempt Retreat")
        print("  7. View Status")
        
        while True:
            choice = input("\nChoose action (1-7): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            print("Invalid choice.")
    
    def run_combat(self, combat_trigger: dict, scene=None):
        """Run a combat encounter in the terminal (regular or boss fight)"""
        # Check if this is a boss fight
        if combat_trigger.get('boss_fight'):
            self.run_boss_fight(combat_trigger, scene)
        else:
            self.run_regular_combat(combat_trigger, scene)
    
    def run_boss_fight(self, combat_trigger: dict, scene=None):
        """Run a boss fight encounter"""
        print("\n" + "="*70)
        print("👑 BOSS FIGHT!")
        print("="*70)
        
        boss_id = combat_trigger.get('boss_id')
        scripted_loss = combat_trigger.get('scripted_loss', False)
        hp_threshold_for_pause = combat_trigger.get('hp_threshold_for_pause')
        continue_from_phase1 = combat_trigger.get('continue_from_phase1', False)
        starting_hp_percent = combat_trigger.get('starting_hp_percent', 60)
        
        # Create the appropriate boss
        boss = None
        if boss_id == 'infila_first':
            boss = create_infila_first_duel()
        elif boss_id == 'infila_final_phase1':
            boss = create_infila_final_phase1()
        elif boss_id == 'infila_final_easy':
            boss = create_infila_final_phase2(
                water_tank_destroyed=True,
                starting_hp_percent=starting_hp_percent
            )
        elif boss_id == 'infila_final_hard':
            boss = create_infila_final_phase2(
                water_tank_destroyed=False,
                starting_hp_percent=starting_hp_percent
            )
        else:
            print(f"❌ Unknown boss_id: {boss_id}")
            return
        
        if not boss:
            print(f"❌ Failed to create boss: {boss_id}")
            return
        
        print(f"\nFacing: {boss.name} - {boss.title}\n")
        
        # Initialize boss fight
        self.boss_system.start_boss_fight(boss, scripted_loss=scripted_loss)
        
        # Boss fight loop
        while boss.current_hp > 0:
            # Show status
            self.print_boss_combat_status(boss)
            
            # Get player action
            action = self.get_combat_action()
            
            if action == '1':  # Attack
                damage = 40 + (self.vader.stats.strength * 2)
                result = self.boss_system.vader_attacks_boss(damage)
                print(f"\n⚔️  Dealt {result['damage']} damage!")
            
            elif action == '2':  # Force Push
                result = self.boss_system.vader_uses_force_on_boss("Force Push", 15)
                self.vader.spend_force_points(10)
                print(f"\n🌊 Force Push: {result['damage']} damage!")
            
            elif action == '3':  # Force Choke
                result = self.boss_system.vader_uses_force_on_boss("Force Choke", 35)
                self.vader.spend_force_points(20)
                print(f"\n🫱 Force Choke: {result['damage']} damage!")
            
            elif action == '4':  # Defend
                print("\n🛡️  Vader defends")
            
            elif action == '5':  # Meditate
                if self.vader.current_force_points < self.vader.max_force_points * 0.5:
                    self.vader.restore_force_points(30)
                    print(f"\n🧘 Restored 30 FP!")
                else:
                    print("FP is not low enough.")
                    continue
            
            elif action == '6':  # Retreat
                print("❌ Cannot retreat from boss fights!")
                continue
            
            elif action == '7':  # Status
                self.print_extended_status()
                continue
            
            # Check for scripted loss
            if scripted_loss and boss.current_hp <= boss.max_hp * 0.3:
                print("\n💀 Your leg gives out! You fall to one knee...")
                print("(This was scripted - recovering...)")
                self.vader.current_health = self.vader.max_health
                return
            
            # Boss turn
            boss_action = self.boss_system.boss_choose_action()
            if boss_action:
                result = self.boss_system.execute_boss_action(boss_action)
                print(f"\n🔥 {boss.name} uses {boss_action.name}!")
            
            # End turn
            self.boss_system.end_turn()
            
            # FP regeneration
            fp_regen = self.vader.regenerate_force_points(self.suit)
            if fp_regen > 0:
                print(f"🔵 +{fp_regen} FP")
            
            # Check if Vader is dead
            if self.vader.current_health <= 0:
                print("\n💀 Vader has been defeated!")
                return
        
        print("\n" + "="*70)
        print("🏆 BOSS DEFEATED!")
        print("="*70)
    
    def print_boss_combat_status(self, boss):
        """Print boss combat status"""
        print("\n" + "─"*70)
        print(f"VADER: {self.vader.current_health}/{self.vader.max_health} HP | "
              f"{self.vader.current_force_points}/{self.vader.max_force_points} FP")
        hp_percent = (boss.current_hp / boss.max_hp) * 100
        bar_length = 30
        filled = int(bar_length * (boss.current_hp / boss.max_hp))
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"{boss.name}: {bar} {hp_percent:.0f}%")
        print("─"*70)
        print()
    
    def run_regular_combat(self, combat_trigger: dict, scene=None):
        """Run a regular (non-boss) combat encounter in the terminal"""
        print("\n" + "="*70)
        print("⚔️  COMBAT START!")
        print("="*70)
        
        # CRITICAL: Reset combat system to avoid state carryover
        self.combat_system = CombatSystem(self.vader, self.suit, self.force_powers)
        
        # Create enemies from combat trigger
        enemies = self._create_enemies_from_trigger(combat_trigger)
        
        # Initialize combat
        self.combat_system.start_combat(enemies)
        
        print(f"\nEnemies: {', '.join([e.name for e in enemies])}\n")
        
        # Combat loop
        while self.combat_system.combat_state.combat_active:
            # Show status
            if not self.print_combat_status():
                break
            
            # Check for helpless enemies
            helpless = [e for e in enemies if e.is_alive and e.is_helpless()]
            if helpless:
                print(f"⚠️  {helpless[0].name} is HELPLESS!")
                print("   You can execute them or continue attacking.\n")
            
            # Get player action
            action = self.get_combat_action()
            
            if action == '1':  # Attack
                alive = [e for e in enemies if e.is_alive]
                if len(alive) > 1:
                    print("\nChoose target:")
                    for i, enemy in enumerate(alive, 1):
                        print(f"  {i}. {enemy.name}")
                    target_choice = input("Target (number): ").strip()
                    try:
                        target_idx = int(target_choice) - 1
                        if 0 <= target_idx < len(alive):
                            target = alive[target_idx]
                        else:
                            print("Invalid target!")
                            continue
                    except ValueError:
                        print("Invalid input!")
                        continue
                elif alive:
                    target = alive[0]
                else:
                    print("No enemies to attack!")
                    continue
                
                result = self.combat_system.vader_attack(target.id)
                if result.get('killed'):
                    print(f"\n⚔️  {target.name} eliminated!")
                else:
                    print(f"\n⚔️  Hit {target.name} for {result.get('damage', 0)} damage!")
            
            elif action == '2':  # Force Push
                result = self.combat_system.vader_use_force_power("force_push")
                if result.get('success'):
                    print(f"\n🌊 Force Push hits {len(result.get('targets_hit', []))} enemies!")
                    for kill in result.get('kills', []):
                        print(f"   💀 {kill} killed!")
                else:
                    print(f"\n❌ Force Push failed: {result.get('message')}")
            
            elif action == '3':  # Force Choke
                alive = [e for e in enemies if e.is_alive]
                if alive:
                    if len(alive) > 1:
                        print("\nChoose target:")
                        for i, enemy in enumerate(alive, 1):
                            print(f"  {i}. {enemy.name}")
                        target_choice = input("Target (number): ").strip()
                        try:
                            target_idx = int(target_choice) - 1
                            if 0 <= target_idx < len(alive):
                                target = alive[target_idx]
                            else:
                                print("Invalid target!")
                                continue
                        except ValueError:
                            print("Invalid input!")
                            continue
                    else:
                        target = alive[0]
                    
                    result = self.combat_system.vader_use_force_power("force_choke", target.id)
                    if result.get('success'):
                        print(f"\n🫱 Force Choke on {target.name}!")
                        if result.get('killed'):
                            print(f"   {target.name} choked to death!")
                    else:
                        print(f"\n❌ Force Choke failed: {result.get('message')}")
                else:
                    print("No enemies to choke!")
                    continue
            
            elif action == '4':  # Defend
                self.combat_system.vader_defend()
                print("\n🛡️  Vader assumes defensive stance.")
            
            elif action == '5':  # Meditate
                if self.vader.current_force_points < self.vader.max_force_points * 0.5:
                    result = self.combat_system.vader_meditate()
                    print(f"\n🧘 Vader meditates, restoring {result.get('fp_restored')} FP!")
                else:
                    print("Force Points are not low enough to meditate.")
                    continue
            
            elif action == '6':  # Retreat
                result = self.combat_system.vader_retreat()
                if result.get('success'):
                    print("\n💨 Successfully retreated from combat!")
                    return  # Exit combat
                else:
                    print("\n❌ Retreat blocked by enemies!")
                    continue
            
            elif action == '7':  # View Status
                self.print_extended_status()
                continue
            
            # Enemy turn
            self.combat_system.enemy_turn()
            
            # End turn
            self.combat_system.end_turn()
            
            # Check if Vader is dead
            if self.vader.current_health <= 0:
                print("\n💀 Vader has been defeated!")
                self.combat_system.combat_state.combat_active = False
                return
        
        # Combat summary
        print("\n" + "="*70)
        print("COMBAT COMPLETE")
        print("="*70)
        
        summary = self.combat_system.get_combat_summary()
        print(f"\nVictory Type: {summary['victory_type'].upper()}")
        print(f"Turns: {summary['turns']}")
        print(f"Enemies Killed: {summary['enemies_killed']}/{len(enemies)}")
        print(f"Damage Dealt: {summary['damage_dealt']}")
        print(f"Damage Taken: {summary['damage_taken']}")
        
        print(f"\nVader's Final Status:")
        print(f"  HP: {summary['vader_hp']}/{self.vader.max_health}")
        print(f"  FP: {summary['force_points_remaining']}/{self.vader.max_force_points}")
        print(f"  Suit Integrity: {summary['suit_integrity']}%")
        
        print()
        # Combat ends here - return to story
    
    def _create_enemies_from_trigger(self, trigger_info: dict) -> list:
        """Create enemy list from combat trigger data"""
        enemies = []
        enemy_types = trigger_info.get('enemy_types', ['stormtrooper'])
        
        for enemy_type_str in enemy_types:
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
    
    def run_story_scene(self, scene_id: str):
        """Run a complete story scene with choices"""
        # Display the scene
        if not self.display_scene(scene_id):
            return None
        
        # Get the scene object to check for combat triggers
        if scene_id not in self.story_system.scenes:
            return None
        
        scene = self.story_system.scenes[scene_id]
        
        # Check if THIS scene has a combat trigger
        # If so, run combat NOW, then auto-advance to next scene
        if hasattr(scene, 'trigger_combat') and scene.trigger_combat:
            input("\nPress ENTER to begin combat...")
            self.run_combat(scene.trigger_combat, scene)
            
            # After combat, auto-advance
            if scene.auto_next:
                return scene.auto_next
            else:
                return None
        
        # Check for available choices
        choices = self.story_system.get_available_choices(scene_id)
        
        if choices:
            # Let player choose
            choice_id = self.show_choices(scene_id)
            if choice_id:
                next_scene = self.handle_story_choice(scene_id, choice_id)
                return next_scene
        
        elif scene.auto_next:
            # Auto-advance to next scene (without combat)
            input("\nPress ENTER to continue...")
            return scene.auto_next
        
        else:
            # End of story branch
            input("\nPress ENTER to continue...")
            return None
    
    def main_loop(self):
        """Main game loop"""
        print("\n" + "="*70)
        print("STAR WARS: DARTH VADER - THE DARK TIMES")
        print("="*70 + "\n")
        
        # Load all scenes
        self.load_all_scenes()
        
        # Start game
        self.current_scene_id = "the_void"
        
        while self.running and self.current_scene_id:
            self.current_scene_id = self.run_story_scene(self.current_scene_id)
        
        print("\n" + "="*70)
        print("GAME OVER")
        print("="*70)


def main():
    """
    Main function - initializes and runs the terminal game.
    """
    game = TerminalGame()
    game.main_loop()


if __name__ == "__main__":
    main()