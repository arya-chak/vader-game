"""
Story System Demo
Play through the opening sequence - Vader's awakening on the operating table.
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
    print("║    STAR WARS: DARTH VADER - STORY SYSTEM DEMO             ║")
    print("║                                                            ║")
    print("║    The Operating Table: Episode III - Aftermath           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    print("\n📖 You are about to experience Vader's first moments in the suit.")
    print("   Every choice matters. Your decisions will shape his path.")
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
    opening_scenes = create_opening_scenes()
    for scene_id, scene in opening_scenes.items():
        story.register_scene(scene)
    
    print(f"\n✓ Loaded {len(opening_scenes)} scenes")
    print(f"✓ Story system initialized")
    
    # Start with the opening scene
    current_scene = "the_void"
    
    # Play through the story
    while current_scene:
        try:
            continue_playing, next_scene = play_scene(story, current_scene)
            
            if not continue_playing:
                break
            
            current_scene = next_scene
            
        except KeyboardInterrupt:
            print("\n\n⏸️  Story interrupted.")
            break
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            break
    
    # Show final status
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
    
    # Show which path they took
    print("\n🎭 YOUR PATH:")
    if story.state.has_flag("iconic_nooo"):
        print("  ⚡ You unleashed the iconic 'NOOO' - full rage path")
    elif story.state.has_flag("silent_grief"):
        print("  🎭 You silently accepted your fate - the mask path")
    elif story.state.has_flag("early_resentment"):
        print("  ⚔️  You blamed Palpatine - seeds of betrayal planted")
    
    if story.state.has_flag("suspects_truth"):
        print("  🤔 You suspect Palpatine may be lying about Padmé")
    if story.state.has_flag("blames_jedi"):
        print("  ⚔️  You blame the Jedi for everything")
    
    # Show alignment
    alignment = vader.psychological_state.calculate_dark_side_alignment()
    print(f"\n🌟 ALIGNMENT: {alignment}")
    
    print("\n" + "═" * 60)
    print("Thank you for playing the demo!")
    print("The full game will continue from here with missions,")
    print("combat, suit upgrades, and more story choices.")
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