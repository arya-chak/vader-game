"""
Combat System Demo
Demonstrates a full combat encounter with various actions.
"""

import sys
import os

# Add src directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from character.vader import DarthVader
from character.suit_system import SuitSystem
from character.force_powers import ForcePowerSystem
from combat.combat_system import CombatSystem, create_enemy, EnemyType


def print_combat_status(vader, suit, enemies, combat):
    """Print current combat status"""
    print("\n" + "═" * 60)
    print(f"TURN {combat.combat_state.turn_number}")
    print("═" * 60)
    print(f"VADER: {vader.current_health}/{vader.max_health} HP | "
          f"{vader.current_force_points}/{vader.max_force_points} FP | "
          f"Suit: {suit.integrity}%")
    print(f"Pain: {suit.current_pain_level}% | Rage: {vader.psychological_state.rage}")
    
    print(f"\nENEMIES:")
    for i, enemy in enumerate(enemies):
        if enemy.is_alive:
            status = ""
            if enemy.is_helpless():
                status = " [HELPLESS - Can Execute]"
            if enemy.is_feared:
                status += " [FEARED]"
            print(f"  {i+1}. {enemy.name} ({enemy.id}): {enemy.current_hp}/{enemy.max_hp} HP{status}")
        else:
            print(f"  {i+1}. {enemy.name}: DEAD ☠️")


def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    STAR WARS: DARTH VADER - COMBAT SYSTEM DEMO            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Initialize systems
    vader = DarthVader()
    suit = SuitSystem()
    force_powers = ForcePowerSystem()
    combat = CombatSystem(vader, suit, force_powers)
    
    # Create encounter: Rebel Base Assault
    print("MISSION: Rebel Base - Detention Level")
    print("OBJECTIVE: Eliminate all resistance\n")
    
    enemies = [
        create_enemy(EnemyType.STORMTROOPER),
        create_enemy(EnemyType.REBEL_VETERAN),
        create_enemy(EnemyType.REBEL_VETERAN),
        create_enemy(EnemyType.STORMTROOPER),
    ]
    
    # Rename for story
    enemies[0].name = "Rebel Soldier"
    enemies[1].name = "Rebel Captain"
    enemies[2].name = "Rebel Demolitionist"
    enemies[3].name = "Rebel Soldier"
    
    # Start combat
    combat.start_combat(enemies)
    print_combat_status(vader, suit, enemies, combat)
    
    # TURN 1: Force Push (Vader starts with this)
    print("\n>>> VADER'S ACTION: Force Push (Area Attack)")
    input("Press Enter to continue...")
    result = combat.vader_use_force_power("force_push")
    if result.get('success'):
        targets = result.get('targets_hit', [])
        kills = result.get('kills', [])
        print(f"✓ Targets hit: {', '.join(targets)}")
        if kills:
            print(f"  Killed: {', '.join(kills)}")
    else:
        print(f"✗ Failed: {result.get('message')}")
    
    combat.enemy_turn()
    combat.end_turn()
    print_combat_status(vader, suit, enemies, combat)
    
    # TURN 2: Force Choke on Captain
    print("\n>>> VADER'S ACTION: Force Choke on Rebel Captain")
    input("Press Enter to continue...")
    
    # Find the captain
    captain = next((e for e in enemies if "Captain" in e.name and e.is_alive), None)
    if captain:
        result = combat.vader_use_force_power("force_choke", captain.id)
        if result.get('success'):
            print(f"✓ Force Choke successful!")
        else:
            print(f"✗ Failed: {result.get('message')}")
    else:
        print("Captain already defeated, attacking another enemy...")
        alive = [e for e in enemies if e.is_alive]
        if alive:
            combat.vader_attack(alive[0].id)
    
    combat.enemy_turn()
    combat.end_turn()
    print_combat_status(vader, suit, enemies, combat)
    
    # TURN 3: Lightsaber attack on wounded enemy
    print("\n>>> VADER'S ACTION: Lightsaber Strike")
    input("Press Enter to continue...")
    
    # Find most wounded enemy
    alive_enemies = [e for e in enemies if e.is_alive]
    if alive_enemies:
        wounded = min(alive_enemies, key=lambda x: x.current_hp)
        result = combat.vader_attack(wounded.id)
        if result.get('success'):
            print(f"✓ Attacked {result['target']}: {result['damage']} damage")
            if result.get('killed'):
                print(f"  {result['target']} eliminated!")
    
    combat.enemy_turn()
    combat.end_turn()
    print_combat_status(vader, suit, enemies, combat)
    
    # TURN 4: Check for helpless enemies and execute
    print("\n>>> VADER'S ACTION: Execution Check")
    input("Press Enter to continue...")
    
    helpless = [e for e in enemies if e.is_alive and e.is_helpless()]
    if helpless:
        target = helpless[0]
        print(f"\n{target.name} is helpless!")
        print("Execution methods:")
        print("  1. Quick Kill [Neutral]")
        print("  2. Force Choke [+5 Darkness, Terrorize]")
        print("  3. Brutal [+10 Darkness, Mass Terror]")
        print("  4. Spare [-3 Darkness, +5 Control]")
        
        print("\nChoosing: Force Choke execution...")
        result = combat.execute_enemy(target.id, "choke")
        if result.get('success'):
            print(f"✓ {target.name} executed via Force Choke")
            print(f"  Darkness: +{result['darkness_change']}")
    else:
        # Just attack
        alive = [e for e in enemies if e.is_alive]
        if alive:
            result = combat.vader_attack(alive[0].id)
            print(f"✓ No helpless enemies, continuing assault")
    
    combat.enemy_turn()
    combat.end_turn()
    print_combat_status(vader, suit, enemies, combat)
    
    # Continue until combat ends
    turn_count = 0
    max_turns = 15
    
    while combat.combat_state.combat_active and turn_count < max_turns:
        alive_enemies = [e for e in enemies if e.is_alive]
        
        if not alive_enemies:
            break
        
        print("\n>>> VADER'S ACTION: Continuing assault...")
        input("Press Enter to continue...")
        
        # Smart targeting - attack weakest enemy
        target = min(alive_enemies, key=lambda x: x.current_hp)
        
        # Use Force power if FP is high, otherwise lightsaber
        if vader.current_force_points >= 20 and len(alive_enemies) > 1:
            # Use Force Push on multiple enemies
            result = combat.vader_use_force_power("force_push")
            if result.get('success'):
                print(f"✓ Force Push hits {len(result.get('targets_hit', []))} enemies")
        else:
            # Lightsaber attack
            result = combat.vader_attack(target.id)
            if result.get('success'):
                print(f"✓ Lightsaber strike on {result['target']}: {result['damage']} damage")
        
        combat.enemy_turn()
        combat.end_turn()
        print_combat_status(vader, suit, enemies, combat)
        
        turn_count += 1
    
    # Combat Summary
    print("\n" + "═" * 60)
    print("COMBAT COMPLETE")
    print("═" * 60)
    
    summary = combat.get_combat_summary()
    print(f"\nVictory Type: {summary['victory_type'].upper()}")
    print(f"Turns: {summary['turns']}")
    print(f"Enemies Killed: {summary['enemies_killed']}/{len(enemies)}")
    print(f"Damage Dealt: {summary['damage_dealt']}")
    print(f"Damage Taken: {summary['damage_taken']}")
    
    print(f"\nVader's Final Status:")
    print(f"  HP: {summary['vader_hp']}/{vader.max_health}")
    print(f"  FP: {summary['force_points_remaining']}/{vader.max_force_points}")
    print(f"  Suit Integrity: {summary['suit_integrity']}%")
    
    print(f"\n{'─' * 60}")
    print("FULL COMBAT LOG")
    print("─" * 60)
    for entry in combat.combat_log:
        print(entry)
    
    print(f"\n{'═' * 60}")
    print("The Emperor will be pleased with this demonstration of power.")
    print("═" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCombat aborted.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()