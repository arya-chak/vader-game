"""
Story System Demo - WITH COMBAT INTEGRATION
Play through the opening sequence and the Kyber Crystal mission with ACTUAL COMBAT.
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
from combat.combat_system import CombatSystem, CombatAction, create_enemy, EnemyType
from combat.boss_fight import (
    BossFightSystem, 
    create_infila_first_duel, 
    create_infila_final_duel,
    create_infila_final_phase1,  # NEW - Phase 1 boss
    create_infila_final_phase2   # NEW - Phase 2 with resume
)


# ============================================================
# GLOBAL COMBAT SYSTEMS
# ============================================================

combat_system = None
boss_system = None

# Save boss state for mid-combat story choices
saved_boss_hp_percent = 60  # Default if somehow missed


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_separator(char="═", length=60):
    """Print a separator line"""
    print(char * length)


def print_dialogue_line(line):
    """Print a dialogue line with formatting"""
    emotion_marker = f" [{line.emotion}]" if line.emotion else ""
    print(f"\n{line.speaker}{emotion_marker}:")
    print(f'  "{line.text}"')
    
    if line.internal_thought:
        print(f"\n  💭 {line.internal_thought}")


def print_scene_header(scene):
    """Print scene header with title and description"""
    print("\n")
    print_separator()
    print(f"  {scene.title.upper()}")
    print_separator()
    
    if scene.location:
        print(f"📍 Location: {scene.location}")
    
    print(f"\n{scene.description}\n")


def print_vader_status(vader, suit):
    """Print Vader's current psychological state"""
    print("\n" + "─" * 60)
    print("VADER'S STATE:")
    print(f"  💀 Darkness: {vader.psychological_state.darkness}/100")
    print(f"  🧠 Control: {vader.psychological_state.control}/100")
    print(f"  🔒 Suppression: {vader.psychological_state.suppression}/100")
    print(f"  😡 Rage: {vader.psychological_state.rage}/100")
    print(f"  ⚡ Health: {vader.current_health}/{vader.max_health}")
    print(f"  🔵 Force: {vader.current_force_points}/{vader.max_force_points}")
    print(f"  🛡️  Suit Integrity: {suit.integrity}%")
    print("─" * 60)


def print_choice(index, choice):
    """Print a choice with formatting"""
    print(f"  {index}. {choice.text}")


# ============================================================
# COMBAT HELPERS
# ============================================================

def create_hp_bar(current, maximum, length=20):
    """Create a visual HP bar"""
    filled = int((current / maximum) * length)
    bar = "█" * filled + "░" * (length - filled)
    return bar


def print_combat_status(vader, suit, enemies, boss=None, turn=1):
    """Print current combat status with visual bars"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print(f"║  {'TURN ' + str(turn):^56}  ║")
    print("╚" + "═" * 58 + "╝")
    
    # Vader status
    hp_bar = create_hp_bar(vader.current_health, vader.max_health)
    fp_bar = create_hp_bar(vader.current_force_points, vader.max_force_points)
    
    print(f"\n⚔️  VADER:")
    print(f"    HP:  {hp_bar}  {vader.current_health}/{vader.max_health}")
    print(f"    FP:  {fp_bar}  {vader.current_force_points}/{vader.max_force_points}")
    print(f"    Suit: {suit.integrity}%  |  Pain: {suit.current_pain_level}%")
    
    # Enemy/Boss status
    if boss:
        hp_bar = create_hp_bar(boss.current_hp, boss.max_hp)
        phase_marker = f"[{boss.current_phase.name}]" if hasattr(boss, 'current_phase') else ""
        print(f"\n🎯 {boss.name.upper()} {phase_marker}")
        print(f"    HP:  {hp_bar}  {boss.current_hp}/{boss.max_hp}")
    else:
        print(f"\n👥 ENEMIES:")
        for i, enemy in enumerate(enemies, 1):
            if enemy.is_alive:
                hp_bar = create_hp_bar(enemy.current_hp, enemy.max_hp, length=15)
                status = ""
                if enemy.is_helpless():
                    status = " [HELPLESS]"
                print(f"    {i}. {enemy.name}: {hp_bar} {enemy.current_hp}/{enemy.max_hp}{status}")
            else:
                print(f"    {i}. {enemy.name}: ☠️  DEAD")


def print_combat_actions(vader, force_powers, in_boss_fight=False):
    """Print available combat actions"""
    print("\n" + "─" * 60)
    print("YOUR ACTION:")
    print("─" * 60)
    print("  1. ⚔️  Lightsaber Attack (40+ damage)")
    print("  2. 🌊 Force Push [10 FP] (Area damage: 15)")
    print("  3. 🫱 Force Choke [20 FP] (Single target: 35 damage)")
    
    if vader.current_force_points >= 30:
        print("  4. 💥 Force Repulse [25 FP] (Area damage: 40)")
    
    print("  5. 🛡️  Defend (+50% defense this turn)")
    
    if vader.current_force_points < vader.max_force_points * 0.5:
        print("  6. 🧘 Meditate (Restore 30 FP, vulnerable)")
    
    print("\n  0. 📊 Status (View detailed stats)")


def get_player_combat_choice(vader, num_enemies):
    """Get player's combat choice"""
    while True:
        try:
            choice = input("\nEnter action number: ").strip()
            
            if choice == "0":
                return "status", None
            
            choice_num = int(choice)
            
            # Map choices to actions
            if choice_num == 1:
                if num_enemies == 1:
                    return "attack", "1"
                else:
                    target = input("Target enemy number: ").strip()
                    return "attack", target
            elif choice_num == 2:
                return "force_push", None
            elif choice_num == 3:
                target = input("Target enemy number: ").strip()
                return "choke", target
            elif choice_num == 4 and vader.current_force_points >= 30:
                return "repulse", None
            elif choice_num == 5:
                return "defend", None
            elif choice_num == 6 and vader.current_force_points < vader.max_force_points * 0.5:
                return "meditate", None
            else:
                print("❌ Invalid choice. Try again.")
        except ValueError:
            print("❌ Please enter a number.")
        except KeyboardInterrupt:
            return "flee", None


def create_enemies_from_trigger(trigger_info):
    """Create enemies based on combat trigger"""
    enemies = []
    
    enemy_types = trigger_info.get('enemy_types', ['stormtrooper'])
    
    for enemy_type_str in enemy_types:
        # Map string to EnemyType enum
        if enemy_type_str == "pirate_thug" or enemy_type_str == "pirate_leader":
            enemy = create_enemy(EnemyType.REBEL_SOLDIER)
            enemy.name = "Pirate Thug" if "thug" in enemy_type_str else "Pirate Leader"
            if "leader" in enemy_type_str:
                enemy.max_hp = 50
                enemy.current_hp = 50
                enemy.attack_damage = 20
        else:
            # Default to stormtrooper
            enemy = create_enemy(EnemyType.STORMTROOPER)
        
        enemies.append(enemy)
    
    return enemies


def run_regular_combat(vader, suit, force_powers, enemies, tutorial=False):
    """
    Run a regular combat encounter.
    Returns (victory, fled)
    """
    global combat_system
    
    # Initialize combat
    combat_system.start_combat(enemies)
    
    if tutorial:
        print("\n" + "═" * 60)
        print("📖 TUTORIAL COMBAT")
        print("═" * 60)
        print("\nBasics:")
        print("  • Choose actions each turn")
        print("  • Manage your Force Points (FP)")
        print("  • Watch for helpless enemies (execute them!)")
        print("  • Your suit can take damage - be careful!")
        input("\n[Press Enter to begin...]")
    
    # Combat loop
    while combat_system.combat_state.combat_active:
        turn = combat_system.combat_state.turn_number
        
        # Show status
        print_combat_status(vader, suit, enemies, turn=turn)
        
        # Check for helpless enemies
        helpless = [e for e in enemies if e.is_alive and e.is_helpless()]
        if helpless:
            print(f"\n⚠️  {helpless[0].name} is HELPLESS! You can execute them.")
        
        # Vader's turn
        print_combat_actions(vader, force_powers)
        
        action, target = get_player_combat_choice(vader, len([e for e in enemies if e.is_alive]))
        
        if action == "status":
            print_vader_status(vader, suit)
            continue
        
        if action == "flee":
            print("\n💨 Attempting to retreat...")
            result = combat_system.vader_retreat()
            if result['success']:
                return False, True
            else:
                print("❌ Retreat failed! Enemies block your escape.")
        
        elif action == "attack":
            # Find target
            try:
                target_idx = int(target) - 1
                alive_enemies = [e for e in enemies if e.is_alive]
                if 0 <= target_idx < len(alive_enemies):
                    target_enemy = alive_enemies[target_idx]
                    result = combat_system.vader_attack(target_enemy.id)
                    
                    if result['killed']:
                        print(f"\n⚔️  {target_enemy.name} eliminated!")
                    else:
                        print(f"\n⚔️  Hit {target_enemy.name} for {result['damage']} damage!")
            except (ValueError, IndexError):
                print("❌ Invalid target!")
                continue
        
        elif action == "force_push":
            result = combat_system.vader_use_force_power("force_push")
            if result['success']:
                print(f"\n🌊 Force Push hits {len(result.get('targets_hit', []))} enemies!")
                for kill in result.get('kills', []):
                    print(f"   💀 {kill} killed!")
        
        elif action == "choke":
            try:
                target_idx = int(target) - 1
                alive_enemies = [e for e in enemies if e.is_alive]
                if 0 <= target_idx < len(alive_enemies):
                    target_enemy = alive_enemies[target_idx]
                    result = combat_system.vader_use_force_power("force_choke", target_enemy.id)
                    if result['success']:
                        print(f"\n🫱 Force Choke grips {target_enemy.name}!")
            except (ValueError, IndexError):
                print("❌ Invalid target!")
                continue
        
        elif action == "repulse":
            result = combat_system.vader_use_force_power("force_repulse")
            if result['success']:
                print(f"\n💥 Force Repulse devastates the battlefield!")
        
        elif action == "defend":
            combat_system.vader_defend()
        
        elif action == "meditate":
            result = combat_system.vader_meditate()
            print(f"\n🧘 Restored {result['fp_restored']} Force Points")
        
        input("\n[Press Enter for enemy turn...]")
        
        # Enemy turn
        print("\n" + "─" * 60)
        print("ENEMY TURN")
        print("─" * 60)
        combat_system.enemy_turn()
        
        # Show combat log
        for log in combat_system.combat_log[-10:]:  # Last 10 entries
            if "ENEMY TURN" not in log and "Combat" not in log and "═" not in log:
                print(log)
        
        # End turn
        combat_system.end_turn()
        
        input("\n[Press Enter to continue...]")
        
        # Check victory conditions
        if not combat_system.combat_state.combat_active:
            break
    
    # Combat ended
    if combat_system.combat_state.victory_type in ["total_victory", "intimidation_victory"]:
        print("\n" + "╔" + "═" * 58 + "╗")
        print(f"║  {'🏆 VICTORY':^56}  ║")
        print("╚" + "═" * 58 + "╝")
        return True, False
    else:
        print("\n" + "╔" + "═" * 58 + "╗")
        print(f"║  {'💀 DEFEAT':^56}  ║")
        print("╚" + "═" * 58 + "╝")
        return False, False


def run_boss_fight(vader, suit, force_powers, boss, scripted_loss=False, hp_threshold_for_pause=None):
    """
    Run a boss fight encounter.
    
    Args:
        vader: Vader instance
        suit: Suit system
        force_powers: Force power system
        boss: Boss enemy
        scripted_loss: If True, triggers scripted loss at certain point
        hp_threshold_for_pause: If set, pause combat at this HP% for story choice
    
    Returns:
        (victory: bool, special_state: str or bool)
        special_state can be:
            - True: scripted_loss_triggered
            - "paused": combat paused for story choice
            - False: normal completion
    """
    global boss_system, saved_boss_hp_percent
    
    # Initialize boss fight
    boss_system.start_boss_fight(boss, scripted_loss=scripted_loss)
    
    # Boss introduction
    print("\n" + "╔" + "═" * 58 + "╗")
    print(f"║  {'⚔️  BOSS FIGHT':^56}  ║")
    print("╚" + "═" * 58 + "╝")
    print(f"\n👑 {boss.name}")
    print(f"   {boss.title}")
    print(f"\n   HP: {boss.current_hp}/{boss.max_hp}")
    print(f"   Phase: {boss.current_phase.name}")
    
    if scripted_loss:
        print("\n⚠️  This is a story encounter...")
    
    if hp_threshold_for_pause:
        print(f"\n⚔️  The duel will pause at {hp_threshold_for_pause}% HP for a critical choice...")
    
    input("\n[Press Enter to begin the duel...]")
    
    # Boss fight loop
    while boss.current_hp > 0 and vader.current_health > 0:
        boss_system.turn_number += 1
        turn = boss_system.turn_number
        
        # Check for HP threshold pause (BEFORE other checks)
        if hp_threshold_for_pause:
            hp_percent = (boss.current_hp / boss.max_hp) * 100
            if hp_percent <= hp_threshold_for_pause:
                # PAUSE COMBAT FOR STORY CHOICE
                saved_boss_hp_percent = hp_percent
                
                print("\n" + "═" * 60)
                print("⏸️  COMBAT PAUSED")
                print("═" * 60)
                print(f"\n{boss.name} HP: {boss.current_hp}/{boss.max_hp} ({hp_percent:.0f}%)")
                print("\nThe duel has reached a critical moment...")
                input("[Press Enter to continue story...]")
                
                return True, "paused"  # Signal to continue to choice scene
        
        # Check for triggers (dialogue, events)
        trigger = boss_system.check_triggers()
        if trigger and trigger.dialogue:
            print("\n" + "─" * 60)
            print(f"💬 {boss.name}: \"{trigger.dialogue}\"")
            print("─" * 60)
            input("[Press Enter...]")
        
        # Check scripted loss
        if scripted_loss and boss_system.check_scripted_loss():
            print("\n" + "═" * 60)
            print("💥 SCRIPTED EVENT")
            print("═" * 60)
            print("\n*CRACK* Your damaged leg gives out!")
            print(f"{boss.name} raises his hand...")
            print("A massive Force push sends you flying off the mountain!")
            input("\n[Press Enter...]")
            return False, True  # Signal scripted loss
        
        # Show combat status
        print_combat_status(vader, suit, [], boss=boss, turn=turn)
        
        # Vader's turn
        print_combat_actions(vader, force_powers, in_boss_fight=True)
        
        action, target = get_player_combat_choice(vader, 1)
        
        if action == "status":
            print_vader_status(vader, suit)
            continue
        
        if action == "attack":
            damage = 40 + (vader.stats.strength * 2)
            result = boss_system.vader_attacks_boss(damage)
            print(f"\n⚔️  Lightsaber strike! {result['damage']} damage!")
            
            if result.get('phase_changed'):
                print(f"\n⚡ {boss.name} enters {result['new_phase'].name}! ⚡")
                input("[Press Enter...]")
        
        elif action == "force_push":
            result = boss_system.vader_uses_force_on_boss("Force Push", 15)
            vader.spend_force_points(10)
            print(f"\n🌊 Force Push! {result['damage']} damage!")
        
        elif action == "choke":
            result = boss_system.vader_uses_force_on_boss("Force Choke", 35)
            vader.spend_force_points(20)
            print(f"\n🫱 Force Choke grips the boss! {result['damage']} damage!")
        
        elif action == "repulse":
            result = boss_system.vader_uses_force_on_boss("Force Repulse", 40)
            vader.spend_force_points(25)
            print(f"\n💥 Force Repulse! {result['damage']} damage!")
        
        elif action == "defend":
            print("\n🛡️  Defensive stance!")
        
        elif action == "meditate":
            vader.restore_force_points(30)
            print(f"\n🧘 Restored 30 Force Points")
        
        input("\n[Press Enter for boss action...]")
        
        # Boss's turn
        print("\n" + "─" * 60)
        print(f"{boss.name.upper()}'S TURN")
        print("─" * 60)
        
        boss_action = boss_system.boss_choose_action()
        if boss_action:
            result = boss_system.execute_boss_action(boss_action)
            
            if result.get('vader_defeated'):
                print("\n💀 You have been defeated!")
                input("[Press Enter...]")
                return False, False
        else:
            # Basic attack
            damage = boss.base_damage
            vader.take_damage(damage)
            print(f"\n⚔️  {boss.name} attacks for {damage} damage!")
        
        # End turn
        boss_system.end_turn()
        
        # FP regeneration
        fp_regen = vader.regenerate_force_points(suit)
        if fp_regen > 0:
            print(f"\n🔵 Force regenerated: +{fp_regen} FP")
        
        input("\n[Press Enter to continue...]")
        
        # Check if boss defeated
        if boss.current_hp <= 0:
            print("\n" + "╔" + "═" * 58 + "╗")
            print(f"║  {'🏆 BOSS DEFEATED':^56}  ║")
            print("╚" + "═" * 58 + "╝")
            print(f"\n{boss.name} falls before you!")
            input("[Press Enter...]")
            return True, False
    
    # Vader defeated
    return False, False


# ============================================================
# SCENE PLAYER (ENHANCED WITH COMBAT)
# ============================================================

def play_scene(story, scene_id, vader, suit, force_powers, show_status=False):
    """
    Play through a single scene WITH COMBAT INTEGRATION.
    Returns (continue_playing, next_scene_id)
    """
    # Start the scene
    success, msg, scene = story.start_scene(scene_id)
    
    if not success:
        print(f"❌ Error: {msg}")
        return False, None
    
    # Print scene header
    print_scene_header(scene)
    
    # Get and display dialogue
    dialogue = story.get_dialogue_for_scene(scene_id)
    
    for line in dialogue:
        print_dialogue_line(line)
        input("\n[Press Enter to continue...]")
    
    # ============================================================
    # COMBAT TRIGGER - ENHANCED WITH PHASE SUPPORT!
    # ============================================================
    
    if scene.trigger_combat:
        combat_info = scene.trigger_combat
        
        # Check if this is a boss fight
        if combat_info.get('boss_fight'):
            boss_id = combat_info.get('boss_id')
            scripted_loss = combat_info.get('scripted_loss', False)
            hp_threshold_for_pause = combat_info.get('hp_threshold_for_pause')
            continue_from_phase1 = combat_info.get('continue_from_phase1', False)
            starting_hp_percent = combat_info.get('starting_hp_percent', 60)
            
            # Create the appropriate boss
            if boss_id == 'infila_first':
                # First duel - scripted loss
                boss = create_infila_first_duel()
                victory, special_state = run_boss_fight(
                    vader, suit, force_powers, boss, 
                    scripted_loss=True
                )
                
                if not victory and special_state:  # Scripted loss triggered
                    # This was meant to happen - continue story
                    pass
                elif not victory:
                    print("\n💀 Unexpected defeat...")
                    return False, None
            
            elif boss_id == 'infila_final_phase1':
                # Final duel Phase 1 - fight until 60% HP, then PAUSE
                boss = create_infila_final_phase1()
                victory, special_state = run_boss_fight(
                    vader, suit, force_powers, boss,
                    hp_threshold_for_pause=60  # Pause at 60% for water tank choice
                )
                
                if special_state == "paused":
                    # Combat paused! Continue to water tank choice
                    print("\n⏸️  The duel pauses at a critical moment...")
                    print("You sense something below - an opportunity...")
                    input("[Press Enter to assess the situation...]")
                    # Scene will auto-advance to water tank choice
                elif not victory:
                    print("\n💀 You have been defeated...")
                    return False, None
            
            elif boss_id == 'infila_final_easy':
                # Phase 2 - Massacre path (EASY)
                boss = create_infila_final_phase2(
                    water_tank_destroyed=True,
                    starting_hp_percent=saved_boss_hp_percent
                )
                
                print("\n" + "═" * 60)
                print("⚔️  THE DUEL RESUMES")
                print("═" * 60)
                print(f"\n💔 {boss.name} is distracted by the screams below...")
                print(f"   HP: {boss.current_hp}/{boss.max_hp}")
                print("   [EASY MODE - Boss weakened by grief]")
                input("\n[Press Enter to continue...]")
                
                victory, _ = run_boss_fight(vader, suit, force_powers, boss)
                
                if not victory:
                    print("\n💀 Defeated despite the advantage...")
                    return False, None
            
            elif boss_id == 'infila_final_hard':
                # Phase 2 - Honor path (HARD)
                boss = create_infila_final_phase2(
                    water_tank_destroyed=False,
                    starting_hp_percent=saved_boss_hp_percent
                )
                
                print("\n" + "═" * 60)
                print("⚔️  THE DUEL RESUMES")
                print("═" * 60)
                print(f"\n⚡ {boss.name} is fully focused on you...")
                print(f"   HP: {boss.current_hp}/{boss.max_hp}")
                print("   [HARD MODE - Boss at full strength]")
                input("\n[Press Enter to continue...]")
                
                victory, _ = run_boss_fight(vader, suit, force_powers, boss)
                
                if not victory:
                    print("\n💀 He was too strong...")
                    return False, None
            
            elif boss_id == 'infila_final':
                # Legacy support - if somehow old trigger is hit
                water_tank_destroyed = story.state.has_flag('ambalaar_massacre')
                boss = create_infila_final_duel(water_tank_destroyed)
                victory, _ = run_boss_fight(vader, suit, force_powers, boss)
                
                if not victory:
                    print("\n💀 You have been defeated...")
                    return False, None
        
        else:
            # Regular combat encounter
            enemy_types = combat_info.get('enemy_types', ['stormtrooper'])
            
            # Map enemy types
            enemies = []
            for enemy_type_str in enemy_types:
                if enemy_type_str == "pirate_thug" or enemy_type_str == "pirate_leader":
                    enemy = create_enemy(EnemyType.REBEL_SOLDIER)
                    enemy.name = "Pirate Thug" if "thug" in enemy_type_str else "Pirate Leader"
                    if "leader" in enemy_type_str:
                        enemy.max_hp = 50
                        enemy.current_hp = 50
                        enemy.attack_damage = 20
                elif enemy_type_str == "clone_trooper":
                    enemy = create_enemy(EnemyType.STORMTROOPER)
                    enemy.name = "Clone Trooper"
                    enemy.max_hp = 40
                    enemy.current_hp = 40
                else:
                    enemy = create_enemy(EnemyType.STORMTROOPER)
                
                enemies.append(enemy)
            
            tutorial = combat_info.get('tutorial', False)
            
            victory, fled = run_regular_combat(vader, suit, force_powers, enemies, tutorial)
            
            if not victory and not fled:
                print("\n💀 You have been defeated...")
                return False, None
            elif fled:
                print("\n💨 You have retreated from combat.")
    
    # ============================================================
    # END OF COMBAT SECTION
    # ============================================================
    
    # Check if scene auto-advances
    if scene.auto_next:
        print(f"\n⏭️  Continuing to next scene...")
        input("[Press Enter...]")
        return True, scene.auto_next
    
    # Get available choices
    choices = story.get_available_choices(scene_id)
    
    if not choices:
        print("\n[End of scene]")
        return False, None
    
    # Display choices
    print("\n" + "─" * 60)
    print("YOUR CHOICE:")
    print("─" * 60)
    
    for i, choice in enumerate(choices, 1):
        print_choice(i, choice)
    
    # Get player input
    while True:
        try:
            print("\n")
            choice_input = input("Enter choice number (or 'status' to see Vader's state, 'quit' to exit): ").strip().lower()
            
            if choice_input == 'quit':
                return False, None
            
            if choice_input == 'status':
                print_vader_status(story.vader, story.suit)
                continue
            
            choice_num = int(choice_input)
            if 1 <= choice_num <= len(choices):
                selected_choice = choices[choice_num - 1]
                break
            else:
                print(f"❌ Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Make the choice
    success, msg, consequences = story.make_choice(scene_id, selected_choice.id)
    
    if not success:
        print(f"❌ Error: {msg}")
        return False, None
    
    # Show Vader's response if there is one
    if selected_choice.response:
        print("\n")
        print_dialogue_line(selected_choice.response)
        input("\n[Press Enter...]")
    
    # Show consequences
    if consequences.get('darkness_change') or consequences.get('control_change') or consequences.get('suppression_change') or consequences.get('rage_change'):
        print("\n" + "─" * 60)
        print("CONSEQUENCES:")
        if consequences.get('darkness_change'):
            print(f"  💀 Darkness {consequences['darkness_change']:+d} → {story.vader.psychological_state.darkness}")
        if consequences.get('control_change'):
            print(f"  🧠 Control {consequences['control_change']:+d} → {story.vader.psychological_state.control}")
        if consequences.get('suppression_change'):
            print(f"  🔒 Suppression {consequences['suppression_change']:+d} → {story.vader.psychological_state.suppression}")
        if consequences.get('rage_change'):
            print(f"  😡 Rage {consequences['rage_change']:+d} → {story.vader.psychological_state.rage}")
        
        if consequences.get('relationship_changes'):
            for faction, change in consequences['relationship_changes'].items():
                print(f"  👥 {faction.title()} relationship {change:+d}")
        
        print("─" * 60)
        
        if show_status:
            print_vader_status(story.vader, story.suit)
    
    # Return next scene
    next_scene = consequences.get('next_scene')
    return True, next_scene


# ============================================================
# MAIN DEMO FUNCTION
# ============================================================

def main():
    """Main demo function"""
    global combat_system, boss_system
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    STAR WARS: DARTH VADER - FULL GAME DEMO               ║")
    print("║                                                            ║")
    print("║    ⚔️  NOW WITH ACTUAL COMBAT! ⚔️                        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n📖 Experience Vader's awakening and first mission")
    print("   WITH REAL COMBAT ENCOUNTERS!")
    print("\n   • Fight pirates, clones, and Jedi Master Infil'a")
    print("   • Use Force powers and lightsaber techniques")
    print("   • Make choices that shape the story")
    print("\n   Type 'status' during choices to see Vader's state.")
    print("   Type '0' during combat to see detailed status.\n")
    
    input("Press Enter to begin...")
    
    # Initialize systems
    print("\n⏳ Initializing game systems...")
    vader = DarthVader()
    suit = SuitSystem()
    force_powers = ForcePowerSystem()
    
    # Initialize combat systems
    combat_system = CombatSystem(vader, suit, force_powers)
    boss_system = BossFightSystem(vader, suit)
    
    print("✓ Combat system initialized")
    
    # Create story system
    story = StorySystem(vader, suit)
    
    # Load opening scenes
    print("⏳ Loading opening sequence...")
    opening_scenes = create_opening_scenes()
    for scene_id, scene in opening_scenes.items():
        story.register_scene(scene)
    print(f"✓ Loaded {len(opening_scenes)} opening scenes")
    
    # Load Kyber mission scenes
    print("⏳ Loading Kyber Crystal mission...")
    kyber_scenes = create_kyber_mission_scenes()
    for scene_id, scene in kyber_scenes.items():
        story.register_scene(scene)
    print(f"✓ Loaded {len(kyber_scenes)} mission scenes")
    
    print(f"\n✓ Total: {len(opening_scenes) + len(kyber_scenes)} scenes loaded")
    print(f"✓ Ready for combat!\n")
    
    input("Press Enter to start...")
    
    # ================================================================
    # PART 1: OPENING SEQUENCE
    # ================================================================
    
    print("\n")
    print_separator("═")
    print("  PART 1: THE AWAKENING")
    print_separator("═")
    
    current_scene = "the_void"
    
    # Play through opening
    while current_scene and current_scene != "tutorial_complete":
        try:
            continue_playing, next_scene = play_scene(
                story, current_scene, vader, suit, force_powers
            )
            
            if not continue_playing:
                break
            
            current_scene = next_scene
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Story interrupted.")
            return
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return
    
    # Transition to mission
    if current_scene == "tutorial_complete":
        try:
            play_scene(story, current_scene, vader, suit, force_powers)
        except Exception as e:
            print(f"Error in final scene: {e}")
        
        print("\n")
        print_separator("═")
        print("  OPENING COMPLETE - NOW WITH COMBAT!")
        print_separator("═")
        
        print("\n📊 Your status:")
        print_vader_status(vader, suit)
        
        input("\n[Press Enter for Mission 1...]")
        
        # ================================================================
        # PART 2: KYBER MISSION
        # ================================================================
        
        print("\n")
        print_separator("═")
        print("  MISSION 1: THE BLEEDING OF THE KYBER CRYSTAL")
        print_separator("═")
        
        current_scene = "kyber_balcony"
        
        while current_scene:
            try:
                continue_playing, next_scene = play_scene(
                    story, current_scene, vader, suit, force_powers
                )
                
                if not continue_playing:
                    break
                
                current_scene = next_scene
                
            except KeyboardInterrupt:
                print("\n\n⏸️  Mission interrupted.")
                break
            except Exception as e:
                print(f"\n\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                break
    
    # ================================================================
    # FINAL SUMMARY
    # ================================================================
    
    print("\n")
    print_separator("═")
    print("  DEMO COMPLETE")
    print_separator("═")
    
    print("\n📊 FINAL STATUS:")
    print_vader_status(vader, suit)
    
    summary = story.get_story_summary()
    print("\n📖 STORY SUMMARY:")
    print(f"  Story Arc: {summary['story_arc'].upper()}")
    print(f"  Jedi Killed: {summary['jedi_killed']}")
    print(f"  Major Choices: {summary['major_choices']}")
    
    print("\n" + "═" * 60)
    print("Thank you for playing!")
    print("Combat is now FULLY INTEGRATED!")
    print("═" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo exited.")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()