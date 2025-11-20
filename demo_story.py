"""
Story System Demo
Play through the opening sequence and the first mission - Vader's awakening and the hunt for the Kyber crystal.
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
    print(f"  🛡️  Suit Integrity: {suit.integrity}%")
    print("─" * 60)


def print_choice(index, choice):
    """Print a choice with formatting"""
    # Don't show tooltips or stat changes - let players make authentic choices!
    # The choice text itself should be enough to convey the meaning
    print(f"  {index}. {choice.text}")


def play_scene(story, scene_id, show_status=False):
    """
    Play through a single scene.
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
    
    # Check for combat trigger
    if scene.trigger_combat:
        print("\n" + "═" * 60)
        print("⚔️  COMBAT ENCOUNTER!")
        print("═" * 60)
        combat_info = scene.trigger_combat
        print(f"\nEnemy Types: {combat_info.get('enemy_types', 'Unknown')}")
        print(f"Difficulty: {combat_info.get('difficulty', 'Normal')}")
        
        if combat_info.get('tutorial'):
            print("\n📖 Tutorial Fight: Learn the combat basics")
        
        if combat_info.get('scripted_loss'):
            print("\n⚠️  Warning: This is a scripted encounter")
        
        print("\n[Combat would trigger here - not yet implemented in demo]")
        print("[Press Enter to continue story...]")
        input()
        
        # For now, just assume combat succeeded
        combat_success = True
        
        if not combat_success:
            print("\n❌ Combat lost! Story may diverge...")
    
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


def main():
    """Main demo function"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    STAR WARS: DARTH VADER - EXTENDED STORY DEMO           ║")
    print("║                                                            ║")
    print("║    Opening: The Operating Table                           ║")
    print("║    Mission 1: The Bleeding of the Kyber Crystal           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n📖 You are about to experience Vader's first moments in the suit")
    print("   and his first mission as a Sith Lord.")
    print("\n   Every choice matters. Your decisions will shape his path.")
    print("\n   Type 'status' at any choice to see Vader's psychological state.")
    print("   Type 'quit' to exit.\n")
    
    input("Press Enter to begin...")
    
    # Initialize systems
    vader = DarthVader()
    suit = SuitSystem()
    force_powers = ForcePowerSystem()
    
    # Create story system
    story = StorySystem(vader, suit)
    
    # Load opening scenes
    print("\n⏳ Loading opening sequence...")
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
    print(f"✓ Story system initialized\n")
    
    input("Press Enter to start the opening sequence...")
    
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
            continue_playing, next_scene = play_scene(story, current_scene)
            
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
    
    # Check if opening completed
    if current_scene == "tutorial_complete":
        # Play the tutorial complete scene
        try:
            play_scene(story, current_scene)
        except Exception as e:
            print(f"Error in final scene: {e}")
        
        # Transition to mission
        print("\n")
        print_separator("═")
        print("  OPENING SEQUENCE COMPLETE")
        print_separator("═")
        
        print("\n📊 Your psychological profile after awakening:")
        print_vader_status(vader, suit)
        
        print("\n")
        input("Press Enter to begin Mission 1: The Bleeding of the Kyber Crystal...")
        
        # ================================================================
        # PART 2: KYBER CRYSTAL MISSION
        # ================================================================
        
        print("\n")
        print_separator("═")
        print("  MISSION 1: THE BLEEDING OF THE KYBER CRYSTAL")
        print_separator("═")
        print("\n📜 MISSION BRIEFING:")
        print("   The Emperor has commanded you to obtain a Sith lightsaber.")
        print("   You must hunt a Jedi, take their kyber crystal, and corrupt it.")
        print("   Only then will you truly be Darth Vader.")
        print_separator("─")
        
        input("\nPress Enter to begin the mission...")
        
        # Start Kyber mission
        current_scene = "kyber_balcony"
        
        while current_scene:
            try:
                continue_playing, next_scene = play_scene(story, current_scene)
                
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
    print("  STORY COMPLETE")
    print_separator("═")
    
    print("\n📊 FINAL PSYCHOLOGICAL PROFILE:")
    print_vader_status(vader, suit)
    
    # Show story summary
    summary = story.get_story_summary()
    print("\n📖 STORY SUMMARY:")
    print(f"  Story Arc: {summary['story_arc'].upper()}")
    print(f"  Scenes Played: {len(story.scene_history) + 1}")
    print(f"  Major Choices Made: {summary['major_choices']}")
    print(f"  Story Flags Set: {summary['flags_set']}")
    if summary['jedi_killed'] > 0:
        print(f"  Jedi Eliminated: {summary['jedi_killed']}")
    
    # Show which paths they took
    print("\n🎭 YOUR PATH:")
    
    # Opening choices
    if story.state.has_flag("iconic_nooo"):
        print("  ⚡ Opening: You unleashed the iconic 'NOOO' - full rage path")
    elif story.state.has_flag("silent_grief"):
        print("  🎭 Opening: You silently accepted your fate - the mask path")
    elif story.state.has_flag("early_resentment"):
        print("  ⚔️  Opening: You blamed Palpatine - seeds of betrayal planted")
    
    if story.state.has_flag("suspects_truth"):
        print("  🤔 Opening: You suspect Palpatine may be lying about Padmé")
    if story.state.has_flag("blames_jedi"):
        print("  ⚔️  Opening: You blame the Jedi for everything")
    
    # Kyber mission choices
    if story.state.has_flag("brighthome_massacre"):
        print("  💀 Brighthome: You slaughtered the clone garrison")
    elif story.state.has_flag("brighthome_peaceful"):
        print("  🤝 Brighthome: You used security codes - efficiency over bloodshed")
    
    if story.state.has_flag("ambalaar_massacre"):
        print("  🌊 Am'balaar: You destroyed the water tank - thousands died")
    elif story.state.has_flag("ambalaar_spared"):
        print("  ⚔️  Am'balaar: You fought honorably - the city was spared")
    
    if story.state.has_flag("mustafar_vision_love"):
        print("  💔 Mustafar: The crystal showed you Padmé and your children")
    elif story.state.has_flag("mustafar_vision_brotherhood"):
        print("  🤝 Mustafar: The crystal showed you Obi-Wan's forgiveness")
    
    if story.state.has_flag("crystal_bled"):
        print("  🔴 Mission Complete: You bled the kyber crystal - your lightsaber is red")
    
    # Show alignment
    alignment = vader.psychological_state.calculate_dark_side_alignment()
    print(f"\n🌟 ALIGNMENT: {alignment}")
    
    # Show key stats
    print(f"\n📈 KEY STATS:")
    print(f"  Level: {vader.level}")
    print(f"  Jedi Killed: {story.state.jedi_killed}")
    print(f"  Civilians Killed: {story.state.civilians_killed}")
    print(f"  Imperials Killed: {story.state.imperials_killed}")
    
    print("\n" + "═" * 60)
    print("Thank you for playing the extended demo!")
    print("This demo covers Vader's awakening and his first mission.")
    print("The full game will continue with more missions, combat,")
    print("suit upgrades, and story choices leading to multiple endings.")
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