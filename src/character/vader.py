"""
Darth Vader Character Class
Core character system for the player character.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class VaderStats:
    """Core statistics for Darth Vader"""
    # Physical attributes (1-10 scale, Vader starts powerful)
    strength: int = 9  # Raw physical power (Force-enhanced)
    dexterity: int = 6  # Reduced due to suit limitations
    constitution: int = 8  # Surviving extensive injuries
    
    # Mental attributes
    intelligence: int = 8  # Tactical genius
    wisdom: int = 5  # Clouded by pain and anger (can increase/decrease)
    charisma: int = 7  # Intimidating presence, but no longer Anakin's charm
    
    # Force attributes
    force_power: int = 10  # Raw Force strength (Vader is immensely powerful)
    force_control: int = 6  # Control over emotions/powers (starts lower, can improve)
    
    # Combat skills (1-10 scale)
    lightsaber_skill: int = 10  # Master duelist
    force_mastery: int = 9  # Exceptional Force user
    tactics: int = 9  # Military strategist
    intimidation: int = 10  # Legendary fear factor


@dataclass
class PsychologicalState:
    """Tracks Vader's mental and emotional state"""
    # Core psychological metrics (0-100 scale)
    darkness: int = 50  # How far into dark side (starts mid, can go either way)
    control: int = 40  # Emotional control vs being ruled by emotion
    suppression: int = 30  # How well Anakin memories are buried
    
    # Specific emotional states
    rage: int = 60  # Current anger level (fuels power but clouds judgment)
    pain_tolerance: int = 30  # How well he handles constant pain
    
    # Tracking memories
    anakin_memories_active: List[str] = field(default_factory=list)
    triggered_memories: Dict[str, int] = field(default_factory=dict)  # memory_id: times triggered
    
    def calculate_dark_side_alignment(self) -> str:
        """Returns alignment description based on darkness level"""
        if self.darkness >= 80:
            return "Fully Consumed by Darkness"
        elif self.darkness >= 60:
            return "Deep in the Dark Side"
        elif self.darkness >= 40:
            return "Embracing Darkness"
        elif self.darkness >= 20:
            return "Conflicted"
        else:
            return "Clinging to Light"


class DarthVader:
    """
    Main character class for Darth Vader.
    Manages all aspects of the player character's state and progression.
    """
    
    def __init__(self, name: str = "Darth Vader"):
        self.name = name
        self.title = "Dark Lord of the Sith"
        self.former_identity = "Anakin Skywalker"
        
        # Core stats
        self.stats = VaderStats()
        self.psychological_state = PsychologicalState()
        
        # Level/progression
        self.level = 1
        self.experience = 0
        
        # Suit status (we'll build this system next)
        self.suit_integrity = 100  # Placeholder
        self.pain_level = 40  # Constant pain from suit
        
        # Force Points (resource for Force powers)
        self.max_force_points = 100
        self.current_force_points = 100
        self.force_point_regen_rate = 10  # Base regeneration per turn
        self.force_exhaustion_turns = 0  # Penalty duration for overuse
        
        # Health (more abstract than traditional HP)
        self.max_health = 150  # Vader is tough to kill
        self.current_health = 150
        
        # Inventory (simplified for now)
        self.lightsaber = "Red Lightsaber (Vader's)"
        self.equipment: List[str] = ["Sith Armor Suit"]
        
        # Story tracking
        self.missions_completed: List[str] = []
        self.choices_made: Dict[str, str] = {}  # choice_id: option_selected
        self.jedi_killed = 0
        self.civilians_killed = 0
        self.imperials_killed = 0  # Tracking betrayals/going rogue
        
        # Relationships (reputation with key characters/factions)
        self.relationships: Dict[str, int] = {
            "palpatine": 50,  # Complex master-servant relationship
            "imperial_officers": 30,  # Feared but not liked
            "inquisitorius": 20,  # Rivalry
            "501st_legion": 80,  # Respected commander during Clone Wars
        }
    
    def add_experience(self, amount: int) -> Optional[str]:
        """
        Add experience and check for level up.
        Returns message if leveled up, None otherwise.
        """
        self.experience += amount
        
        # Simple level-up calculation (can be adjusted)
        required_xp = self.level * 100
        
        if self.experience >= required_xp:
            self.level += 1
            self.experience -= required_xp
            self._apply_level_up_bonuses()
            return f"LEVEL UP! You are now level {self.level}"
        
        return None
    
    def _apply_level_up_bonuses(self):
        """Apply stat increases on level up"""
        # Increase Force points
        self.max_force_points += 10
        self.current_force_points = self.max_force_points
        
        # Slight health increase (Vader becomes more resilient)
        self.max_health += 15
        self.current_health = self.max_health
        
        # Can potentially increase control or other stats based on playstyle
        # This will be expanded later with choice-based progression
    
    def modify_darkness(self, amount: int, reason: str = ""):
        """
        Modify darkness level with consequences.
        Positive amount = more dark, negative = less dark (rare)
        """
        old_alignment = self.psychological_state.calculate_dark_side_alignment()
        
        self.psychological_state.darkness = max(0, min(100, 
            self.psychological_state.darkness + amount))
        
        new_alignment = self.psychological_state.calculate_dark_side_alignment()
        
        # If alignment changed significantly, trigger narrative response
        if old_alignment != new_alignment:
            return f"Your path deepens... {new_alignment}"
        
        return None
    
    def modify_control(self, amount: int):
        """Modify emotional control"""
        self.psychological_state.control = max(0, min(100,
            self.psychological_state.control + amount))
    
    def modify_suppression(self, amount: int):
        """Modify how well Anakin memories are suppressed"""
        self.psychological_state.suppression = max(0, min(100,
            self.psychological_state.suppression + amount))
    
    def take_damage(self, amount: int) -> bool:
        """
        Take damage. Returns True if still alive, False if defeated.
        """
        self.current_health -= amount
        
        # Vader is hard to kill - pain can fuel him
        if self.current_health <= 0:
            # Check if rage/dark side can keep him going
            if self.psychological_state.rage > 80:
                self.current_health = 1  # Too angry to die
                return True
            return False
        
        return True
    
    def heal(self, amount: int):
        """Restore health (meditation, medical attention)"""
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def spend_force_points(self, amount: int) -> bool:
        """
        Attempt to spend Force points for powers.
        Returns True if successful, False if not enough points.
        """
        if self.current_force_points >= amount:
            self.current_force_points -= amount
            return True
        return False
    
    def restore_force_points(self, amount: int):
        """Restore Force points (meditation, rest)"""
        self.current_force_points = min(self.max_force_points, 
                                       self.current_force_points + amount)
    
    def regenerate_force_points(self, suit_system=None) -> int:
        """
        Regenerate Force Points at the end of turn.
        Returns amount regenerated.
        """
        base_regen = self.force_point_regen_rate
        
        # Apply exhaustion penalty
        if self.force_exhaustion_turns > 0:
            base_regen = base_regen // 2  # Half regeneration when exhausted
            self.force_exhaustion_turns -= 1
        
        # Apply suit damage penalty
        if suit_system and suit_system.breathing_disrupted:
            base_regen = base_regen // 2  # Half regeneration with breathing issues
        
        # Rage bonus (high rage converts pain to power)
        if self.psychological_state.rage >= 80:
            base_regen += 5  # Bonus FP from rage
        
        # Apply regeneration
        old_fp = self.current_force_points
        self.current_force_points = min(self.max_force_points, 
                                       self.current_force_points + base_regen)
        
        return self.current_force_points - old_fp  # Return actual amount regenerated
    
    def record_choice(self, choice_id: str, option: str, tags: List[str] = None):
        """
        Record a major choice made by the player.
        Tags can include: "violent", "merciful", "deceptive", "dark_side", "light_side"
        """
        self.choices_made[choice_id] = option
        
        # Apply psychological effects based on tags
        if tags:
            if "dark_side" in tags or "violent" in tags:
                self.modify_darkness(5)
            if "merciful" in tags or "light_side" in tags:
                self.modify_darkness(-3)
                self.modify_control(2)
            if "controlled" in tags:
                self.modify_control(3)
            if "rage" in tags:
                self.psychological_state.rage = min(100, 
                    self.psychological_state.rage + 10)
    
    def get_status_summary(self) -> Dict:
        """Return a summary of Vader's current state"""
        return {
            "name": self.name,
            "level": self.level,
            "health": f"{self.current_health}/{self.max_health}",
            "force_points": f"{self.current_force_points}/{self.max_force_points}",
            "suit_integrity": f"{self.suit_integrity}%",
            "pain_level": f"{self.pain_level}%",
            "alignment": self.psychological_state.calculate_dark_side_alignment(),
            "darkness": self.psychological_state.darkness,
            "control": self.psychological_state.control,
            "missions_completed": len(self.missions_completed),
            "jedi_eliminated": self.jedi_killed
        }
    
    def __repr__(self):
        return f"<DarthVader: Level {self.level}, Darkness {self.psychological_state.darkness}/100>"


# Example usage and testing
if __name__ == "__main__":
    # Create Vader instance
    vader = DarthVader()
    
    print(f"Created: {vader.name}")
    print(f"Title: {vader.title}")
    print(f"Alignment: {vader.psychological_state.calculate_dark_side_alignment()}")
    print(f"\nInitial Stats:")
    print(f"  Strength: {vader.stats.strength}")
    print(f"  Force Power: {vader.stats.force_power}")
    print(f"  Lightsaber Skill: {vader.stats.lightsaber_skill}")
    print(f"\nPsychological State:")
    print(f"  Darkness: {vader.psychological_state.darkness}/100")
    print(f"  Control: {vader.psychological_state.control}/100")
    print(f"  Rage: {vader.psychological_state.rage}/100")
    
    # Test some mechanics
    print(f"\n--- Testing Mechanics ---")
    vader.modify_darkness(20, "Killed innocent civilians")
    print(f"After dark act: {vader.psychological_state.calculate_dark_side_alignment()}")
    
    vader.add_experience(150)
    print(f"Level: {vader.level}, XP: {vader.experience}")
    
    print(f"\nStatus Summary:")
    for key, value in vader.get_status_summary().items():
        print(f"  {key}: {value}")