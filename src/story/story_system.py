"""
Story System for Darth Vader RPG
Manages narrative scenes, dialogue trees, choices, and story progression.
"""

from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class ChoiceType(Enum):
    """Types of choices that affect different aspects"""
    DIALOGUE = "dialogue"  # Just advances conversation
    MORAL = "moral"  # Affects darkness/control
    TACTICAL = "tactical"  # Affects mission outcome
    RELATIONSHIP = "relationship"  # Affects faction standing
    COMMITMENT = "commitment"  # Major story fork


class StoryFlag(Enum):
    """Major story progression flags"""
    AWAKENED = "awakened"
    FIRST_MISSION = "first_mission"
    FIRST_JEDI_KILL = "first_jedi_kill"
    MET_INQUISITOR = "met_inquisitor"
    PALPATINE_SUSPICIOUS = "palpatine_suspicious"
    LOYALTY_TESTED = "loyalty_tested"
    BETRAYAL_PATH = "betrayal_path"
    REDEMPTION_PATH = "redemption_path"


@dataclass
class DialogueLine:
    """A single line of dialogue"""
    speaker: str  # Character name
    text: str
    emotion: Optional[str] = None  # "angry", "calculating", "pained", etc.
    internal_thought: Optional[str] = None  # Vader's inner monologue
    
    # Conditions for this line to appear
    requires_flags: List[str] = field(default_factory=list)
    requires_darkness: Optional[int] = None
    requires_control: Optional[int] = None


@dataclass
class Choice:
    """A choice the player can make"""
    id: str
    text: str  # What the player sees
    choice_type: ChoiceType
    
    # What happens when chosen
    response: Optional[DialogueLine] = None  # Vader's response
    next_scene_id: Optional[str] = None  # Jump to another scene
    
    # Consequences
    darkness_change: int = 0
    control_change: int = 0
    suppression_change: int = 0
    rage_change: int = 0
    
    # Relationship changes
    relationship_changes: Dict[str, int] = field(default_factory=dict)
    
    # Story flags to set
    set_flags: List[str] = field(default_factory=list)
    
    # Requirements to show this choice
    requires_flags: List[str] = field(default_factory=list)
    requires_darkness_min: Optional[int] = None
    requires_darkness_max: Optional[int] = None
    requires_control_min: Optional[int] = None
    
    # Custom callback for complex effects
    callback: Optional[Callable] = None
    
    # UI hints
    tooltip: Optional[str] = None  # Extra info shown to player
    is_recommended: bool = False  # Highlight for new players


@dataclass
class Scene:
    """A story scene with dialogue and choices"""
    id: str
    title: str
    description: str
    
    # Dialogue in this scene
    dialogue: List[DialogueLine] = field(default_factory=list)
    
    # Choices available at end of scene
    choices: List[Choice] = field(default_factory=list)
    
    # Scene type affects presentation
    scene_type: str = "dialogue"  # "dialogue", "combat", "decision", "cutscene"
    
    # Location/setting
    location: Optional[str] = None
    
    # Requirements to access this scene
    requires_flags: List[str] = field(default_factory=list)
    
    # Auto-advance to next scene (no choices)
    auto_next: Optional[str] = None
    
    # Trigger combat after scene
    trigger_combat: Optional[Dict] = None
    
    # Custom scene logic
    on_enter: Optional[Callable] = None
    on_exit: Optional[Callable] = None


class StoryState:
    """Tracks the current state of the story"""
    
    def __init__(self):
        # Current position in story
        self.current_scene_id: Optional[str] = None
        self.previous_scene_id: Optional[str] = None
        
        # Story progression flags
        self.flags: Dict[str, bool] = {}
        
        # Choices made throughout the game
        self.choices_made: Dict[str, str] = {}  # scene_id: choice_id
        
        # Mission tracking
        self.current_mission: Optional[str] = None
        self.missions_completed: List[str] = []
        self.missions_failed: List[str] = []
        
        # Story-specific counters
        self.jedi_killed = 0
        self.civilians_spared = 0
        self.civilians_killed = 0
        self.imperials_killed = 0
        
        # Special encounters
        self.named_characters_met: List[str] = []
        self.named_characters_killed: List[str] = []
        
        # Story arc tracking
        self.story_arc: str = "dark_lord"  # "dark_lord", "conflicted", "redemption", "betrayal"
        self.arc_progress: int = 0  # 0-100 progress in current arc
    
    def set_flag(self, flag: str):
        """Set a story flag"""
        self.flags[flag] = True
    
    def has_flag(self, flag: str) -> bool:
        """Check if a story flag is set"""
        return self.flags.get(flag, False)
    
    def clear_flag(self, flag: str):
        """Clear a story flag"""
        if flag in self.flags:
            del self.flags[flag]
    
    def record_choice(self, scene_id: str, choice_id: str):
        """Record a choice made in a scene"""
        self.choices_made[scene_id] = choice_id
    
    def get_choice(self, scene_id: str) -> Optional[str]:
        """Get the choice made in a specific scene"""
        return self.choices_made.get(scene_id)
    
    def update_story_arc(self, darkness: int, control: int, suppression: int):
        """Update story arc based on psychological state"""
        # Determine which arc the player is on
        if darkness >= 80 and suppression >= 70:
            self.story_arc = "dark_lord"
        elif darkness <= 30 and suppression <= 30:
            self.story_arc = "redemption"
        elif self.has_flag("betrayed_emperor"):
            self.story_arc = "betrayal"
        elif darkness >= 40 and darkness <= 70:
            self.story_arc = "conflicted"


class StorySystem:
    """
    Main story system managing narrative progression.
    """
    
    def __init__(self, vader, suit_system):
        self.vader = vader
        self.suit = suit_system
        
        # Story state
        self.state = StoryState()
        
        # All available scenes
        self.scenes: Dict[str, Scene] = {}
        
        # Scene history for back-tracking
        self.scene_history: List[str] = []
        
        # Narrative log for the player
        self.narrative_log: List[str] = []
    
    def register_scene(self, scene: Scene):
        """Register a scene in the story system"""
        self.scenes[scene.id] = scene
    
    def can_access_scene(self, scene_id: str) -> Tuple[bool, str]:
        """
        Check if a scene can be accessed based on requirements.
        Returns (can_access, reason_if_not)
        """
        if scene_id not in self.scenes:
            return False, "Scene not found"
        
        scene = self.scenes[scene_id]
        
        # Check flag requirements
        for flag in scene.requires_flags:
            if not self.state.has_flag(flag):
                return False, f"Missing required flag: {flag}"
        
        return True, "Can access"
    
    def start_scene(self, scene_id: str) -> Tuple[bool, str, Optional[Scene]]:
        """
        Start a scene. Returns (success, message, scene_object)
        """
        can_access, reason = self.can_access_scene(scene_id)
        
        if not can_access:
            return False, reason, None
        
        scene = self.scenes[scene_id]
        
        # Store previous scene
        if self.state.current_scene_id:
            self.state.previous_scene_id = self.state.current_scene_id
            self.scene_history.append(self.state.current_scene_id)
        
        # Set current scene
        self.state.current_scene_id = scene_id
        
        # Run on_enter callback if exists
        if scene.on_enter:
            scene.on_enter(self.vader, self.suit, self.state)
        
        # Log narrative event
        self.log_narrative(f"[Scene: {scene.title}]")
        
        return True, "Scene started", scene
    
    def get_available_choices(self, scene_id: str) -> List[Choice]:
        """
        Get list of choices available in a scene based on current state.
        """
        if scene_id not in self.scenes:
            return []
        
        scene = self.scenes[scene_id]
        available = []
        
        for choice in scene.choices:
            # Check flag requirements
            if choice.requires_flags:
                if not all(self.state.has_flag(flag) for flag in choice.requires_flags):
                    continue
            
            # Check darkness requirements
            darkness = self.vader.psychological_state.darkness
            if choice.requires_darkness_min and darkness < choice.requires_darkness_min:
                continue
            if choice.requires_darkness_max and darkness > choice.requires_darkness_max:
                continue
            
            # Check control requirements
            control = self.vader.psychological_state.control
            if choice.requires_control_min and control < choice.requires_control_min:
                continue
            
            available.append(choice)
        
        return available
    
    def make_choice(self, scene_id: str, choice_id: str) -> Tuple[bool, str, Dict]:
        """
        Player makes a choice. Apply consequences and advance story.
        Returns (success, message, consequences_dict)
        """
        if scene_id not in self.scenes:
            return False, "Scene not found", {}
        
        scene = self.scenes[scene_id]
        
        # Find the choice
        choice = None
        for c in scene.choices:
            if c.id == choice_id:
                choice = c
                break
        
        if not choice:
            return False, "Choice not found", {}
        
        # Record the choice
        self.state.record_choice(scene_id, choice_id)
        
        # Apply psychological changes
        if choice.darkness_change != 0:
            self.vader.modify_darkness(choice.darkness_change)
        if choice.control_change != 0:
            self.vader.modify_control(choice.control_change)
        if choice.suppression_change != 0:
            self.vader.modify_suppression(choice.suppression_change)
        if choice.rage_change != 0:
            self.vader.psychological_state.rage = max(0, min(100,
                self.vader.psychological_state.rage + choice.rage_change))
        
        # Apply relationship changes
        for faction, change in choice.relationship_changes.items():
            if faction in self.vader.relationships:
                self.vader.relationships[faction] += change
        
        # Set story flags
        for flag in choice.set_flags:
            self.state.set_flag(flag)
        
        # Run custom callback if exists
        if choice.callback:
            choice.callback(self.vader, self.suit, self.state)
        
        # Update story arc
        self.state.update_story_arc(
            self.vader.psychological_state.darkness,
            self.vader.psychological_state.control,
            self.vader.psychological_state.suppression
        )
        
        # Prepare consequences summary
        consequences = {
            "darkness_change": choice.darkness_change,
            "control_change": choice.control_change,
            "suppression_change": choice.suppression_change,
            "rage_change": choice.rage_change,
            "relationship_changes": choice.relationship_changes,
            "flags_set": choice.set_flags,
            "next_scene": choice.next_scene_id
        }
        
        # Log choice
        self.log_narrative(f"[Choice: {choice.text}]")
        
        # Run scene on_exit if exists
        if scene.on_exit:
            scene.on_exit(self.vader, self.suit, self.state)
        
        # Auto-advance to next scene if specified
        if choice.next_scene_id:
            success, msg, next_scene = self.start_scene(choice.next_scene_id)
            consequences["scene_started"] = success
        
        message = f"Choice made: {choice.text}"
        if choice.response:
            message += f"\n{choice.response.speaker}: {choice.response.text}"
        
        return True, message, consequences
    
    def get_dialogue_for_scene(self, scene_id: str) -> List[DialogueLine]:
        """
        Get all dialogue lines for a scene, filtered by current state.
        """
        if scene_id not in self.scenes:
            return []
        
        scene = self.scenes[scene_id]
        available_dialogue = []
        
        for line in scene.dialogue:
            # Check flag requirements
            if line.requires_flags:
                if not all(self.state.has_flag(flag) for flag in line.requires_flags):
                    continue
            
            # Check darkness requirement
            if line.requires_darkness:
                if self.vader.psychological_state.darkness < line.requires_darkness:
                    continue
            
            # Check control requirement
            if line.requires_control:
                if self.vader.psychological_state.control < line.requires_control:
                    continue
            
            available_dialogue.append(line)
        
        return available_dialogue
    
    def log_narrative(self, message: str):
        """Add an entry to the narrative log"""
        self.narrative_log.append(message)
    
    def get_story_summary(self) -> Dict:
        """Get a summary of story progress"""
        return {
            "current_scene": self.state.current_scene_id,
            "story_arc": self.state.story_arc,
            "arc_progress": self.state.arc_progress,
            "jedi_killed": self.state.jedi_killed,
            "missions_completed": len(self.state.missions_completed),
            "flags_set": len(self.state.flags),
            "major_choices": len(self.state.choices_made),
            "named_characters_met": len(self.state.named_characters_met)
        }
    
    def __repr__(self):
        return f"<StorySystem: {self.state.current_scene_id}, {len(self.scenes)} scenes>"


# Helper functions for building scenes

def create_dialogue(speaker: str, text: str, emotion: str = None, 
                   thought: str = None) -> DialogueLine:
    """Helper to create dialogue lines"""
    return DialogueLine(
        speaker=speaker,
        text=text,
        emotion=emotion,
        internal_thought=thought
    )


def create_choice(choice_id: str, text: str, choice_type: ChoiceType,
                 darkness: int = 0, control: int = 0, 
                 next_scene: str = None, **kwargs) -> Choice:
    """Helper to create choices"""
    return Choice(
        id=choice_id,
        text=text,
        choice_type=choice_type,
        darkness_change=darkness,
        control_change=control,
        next_scene_id=next_scene,
        **kwargs
    )


# Example usage and testing
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    from character.vader import DarthVader
    from character.suit_system import SuitSystem
    
    # Create Vader and systems
    vader = DarthVader()
    suit = SuitSystem()
    
    # Create story system
    story = StorySystem(vader, suit)
    
    print("=== STORY SYSTEM TEST ===\n")
    
    # Create a simple test scene
    test_scene = Scene(
        id="test_awakening",
        title="The Awakening",
        description="You awaken on the operating table...",
        dialogue=[
            create_dialogue(
                "Medical Droid",
                "Subject is stabilizing. Lord Vader, can you hear me?",
                emotion="clinical"
            ),
            create_dialogue(
                "Vader",
                "Where... where is Padmé?",
                emotion="desperate",
                thought="Everything hurts. The pain is... everything."
            )
        ],
        choices=[
            create_choice(
                "demand_answer",
                "DEMAND to know where Padmé is",
                ChoiceType.MORAL,
                darkness=5,
                rage_change=10,
                tooltip="Give in to anger and desperation"
            ),
            create_choice(
                "stay_calm",
                "Ask calmly about her condition",
                ChoiceType.MORAL,
                control=5,
                darkness=-2,
                tooltip="Maintain composure despite pain"
            )
        ]
    )
    
    # Register scene
    story.register_scene(test_scene)
    
    # Start scene
    success, msg, scene = story.start_scene("test_awakening")
    print(f"Scene started: {success}")
    print(f"Title: {scene.title}")
    print(f"\n--- Dialogue ---")
    
    dialogue = story.get_dialogue_for_scene("test_awakening")
    for line in dialogue:
        emotion_marker = f" [{line.emotion}]" if line.emotion else ""
        print(f"{line.speaker}{emotion_marker}: {line.text}")
        if line.internal_thought:
            print(f"  (Thought: {line.internal_thought})")
    
    print(f"\n--- Choices ---")
    choices = story.get_available_choices("test_awakening")
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice.text}")
        if choice.tooltip:
            print(f"   {choice.tooltip}")
    
    # Make a choice
    print(f"\n--- Making Choice ---")
    success, msg, consequences = story.make_choice("test_awakening", "demand_answer")
    print(f"Result: {msg}")
    print(f"Darkness change: +{consequences['darkness_change']}")
    print(f"Rage change: +{consequences['rage_change']}")
    
    print(f"\n--- Story Summary ---")
    summary = story.get_story_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")