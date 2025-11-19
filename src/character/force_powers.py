"""
Darth Vader Force Powers System
Manages Force abilities, their usage, learning, and progression.
Includes special mechanics for Vader's limitations (e.g., Force Lightning difficulty).
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ForcePowerCategory(Enum):
    """Categories of Force powers"""
    TELEKINESIS = "telekinesis"
    SENSE = "sense"
    CONTROL = "control"
    DARK_SIDE = "dark_side"
    COMBAT = "combat"
    UTILITY = "utility"


class ForcePowerTier(Enum):
    """Power tiers - higher tiers are more powerful and costly"""
    BASIC = 1
    ADVANCED = 2
    MASTER = 3
    LEGENDARY = 4


@dataclass
class ForcePower:
    """Represents a Force power that Vader can learn and use"""
    id: str
    name: str
    description: str
    category: ForcePowerCategory
    tier: ForcePowerTier
    
    # Usage costs
    force_point_cost: int
    cooldown_turns: int = 0  # Turns before can use again
    
    # Learning requirements
    requires_darkness: int = 0  # Minimum darkness level (0-100)
    requires_control: int = 0  # Minimum control level (0-100)
    requires_level: int = 1
    requires_powers: List[str] = field(default_factory=list)  # Prerequisite powers
    
    # Special requirements
    requires_kyber_gauntlets: bool = False  # For Force Lightning
    suit_damage_risk: int = 0  # Using power can damage suit (0-100%)
    
    # Effects
    base_damage: int = 0  # For offensive powers
    duration_turns: int = 1  # For sustained powers
    area_effect: bool = False  # Single target vs multiple
    
    # Scaling
    scales_with_darkness: bool = False  # Power increases with darkness
    scales_with_rage: bool = False  # Power increases with rage
    
    # Status
    learned: bool = False
    current_cooldown: int = 0
    mastery_level: int = 0  # 0-100, increases with use
    
    # Learning cost
    experience_cost: int = 100


class ForcePowerSystem:
    """
    Manages Vader's Force abilities, learning, and usage.
    """
    
    def __init__(self):
        # Available and learned powers
        self.available_powers: Dict[str, ForcePower] = self._initialize_powers()
        self.learned_powers: Dict[str, ForcePower] = {}
        
        # Add starting powers to learned_powers
        for power_id, power in self.available_powers.items():
            if power.learned:
                self.learned_powers[power_id] = power
        
        # Active effects (powers currently in effect)
        self.active_effects: Dict[str, int] = {}  # power_id: turns_remaining
        
        # Usage tracking
        self.force_points_spent_total = 0
        self.powers_used_count: Dict[str, int] = {}
        
        # Combat-specific tracking (reset between combats)
        self.legendary_uses_this_combat = 0  # Track legendary power spam
        self.force_sensitive_kills = 0  # Bonus FP from killing Force users
        
        # Force Lightning special tracking
        self.force_lightning_unlocked = False
        self.force_lightning_attempts = 0
        self.force_lightning_successes = 0
    
    def _initialize_powers(self) -> Dict[str, ForcePower]:
        """Initialize all available Force powers"""
        powers = {}
        
        # ============================================================
        # TELEKINESIS POWERS
        # ============================================================
        
        powers["force_push"] = ForcePower(
            id="force_push",
            name="Force Push",
            description="Push enemies away with telekinetic force. Can affect multiple targets.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.BASIC,
            force_point_cost=10,
            base_damage=15,
            area_effect=True,
            learned=True,  # Vader starts with this
            experience_cost=0
        )
        
        powers["force_pull"] = ForcePower(
            id="force_pull",
            name="Force Pull",
            description="Pull an enemy toward you or disarm them.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.BASIC,
            force_point_cost=8,
            base_damage=10,
            learned=True,  # Vader starts with this
            experience_cost=0
        )
        
        powers["force_grip"] = ForcePower(
            id="force_grip",
            name="Force Grip",
            description="Crush objects or immobilize enemies telekinetically.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=15,
            cooldown_turns=2,
            base_damage=25,
            duration_turns=2,
            requires_darkness=30,
            requires_level=2,
            requires_powers=["force_push"],
            scales_with_darkness=True,
            experience_cost=150
        )
        
        powers["force_choke"] = ForcePower(
            id="force_choke",
            name="Force Choke",
            description="Vader's signature move. Strangle enemies from a distance.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=20,
            cooldown_turns=1,
            base_damage=35,
            duration_turns=3,
            requires_darkness=40,
            requires_level=3,
            requires_powers=["force_grip"],
            scales_with_darkness=True,
            scales_with_rage=True,
            learned=True,  # Vader's iconic ability
            experience_cost=0
        )
        
        powers["force_crush"] = ForcePower(
            id="force_crush",
            name="Force Crush",
            description="Devastating telekinetic attack. Can crush armor, droids, or internal organs.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.MASTER,
            force_point_cost=30,
            cooldown_turns=3,
            base_damage=60,
            requires_darkness=60,
            requires_level=5,
            requires_powers=["force_choke"],
            scales_with_darkness=True,
            scales_with_rage=True,
            experience_cost=300
        )
        
        powers["force_maelstrom"] = ForcePower(
            id="force_maelstrom",
            name="Force Maelstrom",
            description="Create a telekinetic storm that tears apart everything nearby.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.LEGENDARY,
            force_point_cost=50,
            cooldown_turns=5,
            base_damage=80,
            area_effect=True,
            requires_darkness=80,
            requires_level=8,
            requires_powers=["force_crush"],
            scales_with_darkness=True,
            scales_with_rage=True,
            experience_cost=500
        )
        
        # ============================================================
        # SENSE POWERS
        # ============================================================
        
        powers["force_sense"] = ForcePower(
            id="force_sense",
            name="Force Sense",
            description="Detect nearby life forms and danger.",
            category=ForcePowerCategory.SENSE,
            tier=ForcePowerTier.BASIC,
            force_point_cost=5,
            duration_turns=5,
            learned=True,  # Vader starts with this
            experience_cost=0
        )
        
        powers["battle_meditation"] = ForcePower(
            id="battle_meditation",
            name="Battle Meditation",
            description="Enhance your combat awareness and reaction time.",
            category=ForcePowerCategory.SENSE,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=15,
            duration_turns=4,
            requires_control=30,
            requires_level=3,
            requires_powers=["force_sense"],
            experience_cost=200
        )
        
        powers["force_precognition"] = ForcePower(
            id="force_precognition",
            name="Force Precognition",
            description="Glimpse the immediate future. Dramatically increases defense and counterattacks.",
            category=ForcePowerCategory.SENSE,
            tier=ForcePowerTier.MASTER,
            force_point_cost=25,
            cooldown_turns=3,
            duration_turns=3,
            requires_control=50,
            requires_level=6,
            requires_powers=["battle_meditation"],
            experience_cost=350
        )
        
        # ============================================================
        # CONTROL POWERS
        # ============================================================
        
        powers["force_barrier"] = ForcePower(
            id="force_barrier",
            name="Force Barrier",
            description="Create a protective Force shield.",
            category=ForcePowerCategory.CONTROL,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=20,
            duration_turns=3,
            requires_control=25,
            requires_level=2,
            experience_cost=150
        )
        
        powers["force_speed"] = ForcePower(
            id="force_speed",
            name="Force Speed",
            description="Enhance physical speed and reflexes.",
            category=ForcePowerCategory.CONTROL,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=15,
            duration_turns=3,
            requires_level=3,
            experience_cost=200
        )
        
        powers["force_body"] = ForcePower(
            id="force_body",
            name="Force Body",
            description="Use the Force to enhance physical resilience and ignore pain.",
            category=ForcePowerCategory.CONTROL,
            tier=ForcePowerTier.MASTER,
            force_point_cost=30,
            duration_turns=4,
            requires_control=40,
            requires_level=5,
            requires_powers=["force_barrier"],
            experience_cost=300
        )
        
        # ============================================================
        # DARK SIDE POWERS
        # ============================================================
        
        powers["force_rage"] = ForcePower(
            id="force_rage",
            name="Force Rage",
            description="Channel anger into devastating power. Increases damage but reduces control.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=20,
            duration_turns=4,
            requires_darkness=50,
            requires_level=4,
            scales_with_rage=True,
            experience_cost=200
        )
        
        powers["force_fear"] = ForcePower(
            id="force_fear",
            name="Force Fear",
            description="Project terror into your enemies' minds. Can cause panic or paralysis.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=18,
            area_effect=True,
            requires_darkness=40,
            requires_level=3,
            scales_with_darkness=True,
            experience_cost=180
        )
        
        powers["force_drain"] = ForcePower(
            id="force_drain",
            name="Force Drain",
            description="Drain life force from enemies to heal yourself.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.MASTER,
            force_point_cost=25,
            cooldown_turns=2,
            base_damage=30,
            requires_darkness=60,
            requires_level=5,
            scales_with_darkness=True,
            experience_cost=300
        )
        
        powers["force_scream"] = ForcePower(
            id="force_scream",
            name="Force Scream",
            description="Release accumulated pain and rage as a devastating Force shockwave.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.MASTER,
            force_point_cost=35,
            cooldown_turns=4,
            base_damage=50,
            area_effect=True,
            requires_darkness=70,
            requires_level=6,
            requires_powers=["force_rage"],
            scales_with_rage=True,
            experience_cost=350
        )
        
        powers["force_lightning"] = ForcePower(
            id="force_lightning",
            name="Force Lightning",
            description="EXTREMELY DIFFICULT: Channel dark side energy as devastating lightning. Requires kyber gauntlets and risks suit damage.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.LEGENDARY,
            force_point_cost=40,
            cooldown_turns=3,
            base_damage=70,
            requires_darkness=75,
            requires_control=60,  # Need high control due to difficulty
            requires_level=7,
            requires_kyber_gauntlets=True,
            suit_damage_risk=30,  # 30% chance to damage suit when used
            scales_with_darkness=True,
            experience_cost=600
        )
        
        powers["force_storm"] = ForcePower(
            id="force_storm",
            name="Force Storm",
            description="FORBIDDEN: Create a massive Force tempest. Ultimate dark side power.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.LEGENDARY,
            force_point_cost=60,
            cooldown_turns=6,
            base_damage=100,
            area_effect=True,
            requires_darkness=90,
            requires_level=9,
            requires_powers=["force_lightning", "force_maelstrom"],
            scales_with_darkness=True,
            scales_with_rage=True,
            experience_cost=800
        )
        
        # ============================================================
        # FORCE UNLEASHED POWERS
        # Spectacular, high-impact abilities from TFU games
        # ============================================================
        
        powers["force_repulse"] = ForcePower(
            id="force_repulse",
            name="Force Repulse",
            description="Explosive Force blast in all directions. Devastating area attack.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=25,
            cooldown_turns=2,
            base_damage=40,
            area_effect=True,
            requires_darkness=35,
            requires_level=4,
            requires_powers=["force_push"],
            scales_with_rage=True,
            experience_cost=220
        )
        
        powers["force_lightning_bomb"] = ForcePower(
            id="force_lightning_bomb",
            name="Force Lightning Bomb",
            description="Channel lightning into a target, then detonate it. Requires kyber gauntlets.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.LEGENDARY,
            force_point_cost=50,
            cooldown_turns=4,
            base_damage=85,
            area_effect=True,
            requires_darkness=80,
            requires_level=8,
            requires_kyber_gauntlets=True,
            requires_powers=["force_lightning"],
            suit_damage_risk=25,
            scales_with_darkness=True,
            experience_cost=700
        )
        
        powers["force_blast"] = ForcePower(
            id="force_blast",
            name="Force Blast",
            description="Concentrated Force projectile. Can be charged for more damage.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=18,
            cooldown_turns=1,
            base_damage=35,
            requires_level=3,
            requires_powers=["force_push"],
            scales_with_darkness=True,
            experience_cost=180
        )
        
        powers["sith_strike"] = ForcePower(
            id="sith_strike",
            name="Sith Strike",
            description="Devastating lightsaber combo infused with dark side energy.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=20,
            cooldown_turns=2,
            base_damage=50,
            requires_darkness=40,
            requires_level=4,
            requires_powers=["saber_throw"],
            scales_with_rage=True,
            experience_cost=200
        )
        
        powers["aerial_assault"] = ForcePower(
            id="aerial_assault",
            name="Aerial Assault",
            description="Force-enhanced jump attack. Strike from above with crushing force.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=15,
            base_damage=40,
            requires_level=3,
            requires_powers=["force_speed"],
            experience_cost=180
        )
        
        powers["saber_slam"] = ForcePower(
            id="saber_slam",
            name="Saber Slam",
            description="Drive lightsaber into ground with Force power. Creates shockwave.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.MASTER,
            force_point_cost=25,
            cooldown_turns=3,
            base_damage=55,
            area_effect=True,
            requires_darkness=50,
            requires_level=5,
            requires_powers=["sith_strike"],
            scales_with_rage=True,
            experience_cost=280
        )
        
        powers["force_fury"] = ForcePower(
            id="force_fury",
            name="Force Fury",
            description="Channel pure rage into overwhelming power. Massive boost to all abilities.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.MASTER,
            force_point_cost=40,
            cooldown_turns=5,
            duration_turns=5,
            requires_darkness=65,
            requires_level=6,
            requires_powers=["force_rage"],
            scales_with_rage=True,
            experience_cost=400
        )
        
        powers["force_grip_throw"] = ForcePower(
            id="force_grip_throw",
            name="Force Grip & Throw",
            description="Grab enemy with Force, then hurl them into obstacles or other enemies.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=22,
            cooldown_turns=1,
            base_damage=45,
            requires_darkness=35,
            requires_level=3,
            requires_powers=["force_grip"],
            scales_with_darkness=True,
            experience_cost=190
        )
        
        powers["impale"] = ForcePower(
            id="impale",
            name="Impale",
            description="Telekinetically drive your lightsaber through multiple enemies.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.MASTER,
            force_point_cost=30,
            cooldown_turns=3,
            base_damage=70,
            area_effect=True,
            requires_darkness=55,
            requires_level=5,
            requires_powers=["saber_throw"],
            scales_with_darkness=True,
            experience_cost=320
        )
        
        powers["force_lightning_shield"] = ForcePower(
            id="force_lightning_shield",
            name="Lightning Shield",
            description="Surround yourself with crackling Force lightning. Damages nearby enemies. Requires kyber gauntlets.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.MASTER,
            force_point_cost=35,
            cooldown_turns=4,
            duration_turns=4,
            base_damage=25,
            area_effect=True,
            requires_darkness=70,
            requires_level=7,
            requires_kyber_gauntlets=True,
            requires_powers=["force_lightning"],
            suit_damage_risk=20,
            scales_with_darkness=True,
            experience_cost=500
        )
        
        powers["force_saber_combo"] = ForcePower(
            id="force_saber_combo",
            name="Force-Enhanced Saber Combo",
            description="Blur of lightsaber strikes enhanced by the Force. Extremely fast and deadly.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.MASTER,
            force_point_cost=28,
            cooldown_turns=2,
            base_damage=65,
            requires_level=6,
            requires_powers=["sith_strike", "force_speed"],
            scales_with_rage=True,
            experience_cost=350
        )
        
        powers["devastation"] = ForcePower(
            id="devastation",
            name="Devastation",
            description="Ultimate Force Unleashed ability. Obliterate everything around you.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.LEGENDARY,
            force_point_cost=70,
            cooldown_turns=7,
            base_damage=120,
            area_effect=True,
            requires_darkness=85,
            requires_level=10,
            requires_powers=["force_fury", "force_repulse"],
            scales_with_darkness=True,
            scales_with_rage=True,
            experience_cost=900
        )
        
        powers["sith_saber_flurry"] = ForcePower(
            id="sith_saber_flurry",
            name="Sith Saber Flurry",
            description="Relentless barrage of lightsaber attacks. Each strike fuels the next.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.LEGENDARY,
            force_point_cost=45,
            cooldown_turns=4,
            base_damage=90,
            requires_darkness=75,
            requires_level=8,
            requires_powers=["force_saber_combo"],
            scales_with_rage=True,
            experience_cost=650
        )
        
        powers["force_shockwave"] = ForcePower(
            id="force_shockwave",
            name="Force Shockwave",
            description="Ground-traveling Force wave that trips and damages enemies.",
            category=ForcePowerCategory.TELEKINESIS,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=20,
            cooldown_turns=2,
            base_damage=30,
            area_effect=True,
            requires_level=4,
            requires_powers=["force_repulse"],
            experience_cost=200
        )
        
        powers["force_destruction"] = ForcePower(
            id="force_destruction",
            name="Force Destruction",
            description="Disintegrate matter at molecular level. Instantly destroy weaker enemies.",
            category=ForcePowerCategory.DARK_SIDE,
            tier=ForcePowerTier.LEGENDARY,
            force_point_cost=55,
            cooldown_turns=5,
            base_damage=95,
            requires_darkness=88,
            requires_level=9,
            requires_powers=["force_crush"],
            scales_with_darkness=True,
            experience_cost=750
        )
        
        # ============================================================
        # COMBAT POWERS
        # ============================================================
        
        powers["saber_throw"] = ForcePower(
            id="saber_throw",
            name="Saber Throw",
            description="Hurl your lightsaber with deadly precision.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.BASIC,
            force_point_cost=12,
            base_damage=30,
            requires_level=2,
            learned=True,  # Vader knows this
            experience_cost=0
        )
        
        powers["saber_barrier"] = ForcePower(
            id="saber_barrier",
            name="Saber Barrier",
            description="Create an impenetrable defense with your lightsaber and the Force.",
            category=ForcePowerCategory.COMBAT,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=15,
            duration_turns=2,
            requires_level=4,
            requires_powers=["saber_throw"],
            experience_cost=200
        )
        
        # ============================================================
        # UTILITY POWERS
        # ============================================================
        
        powers["force_persuasion"] = ForcePower(
            id="force_persuasion",
            name="Force Persuasion",
            description="Influence weak-minded individuals.",
            category=ForcePowerCategory.UTILITY,
            tier=ForcePowerTier.BASIC,
            force_point_cost=10,
            requires_control=20,
            requires_level=2,
            learned=True,  # Vader starts with this
            experience_cost=0
        )
        
        powers["mind_probe"] = ForcePower(
            id="mind_probe",
            name="Mind Probe",
            description="Forcefully extract information from someone's mind.",
            category=ForcePowerCategory.UTILITY,
            tier=ForcePowerTier.ADVANCED,
            force_point_cost=20,
            requires_darkness=30,
            requires_level=3,
            requires_powers=["force_persuasion"],
            experience_cost=180
        )
        
        powers["force_cloak"] = ForcePower(
            id="force_cloak",
            name="Force Cloak",
            description="Bend light and perception to become nearly invisible.",
            category=ForcePowerCategory.UTILITY,
            tier=ForcePowerTier.MASTER,
            force_point_cost=30,
            duration_turns=4,
            requires_control=60,
            requires_level=6,
            experience_cost=400
        )
        
        return powers
    
    def can_learn_power(self, power_id: str, vader_level: int, 
                       vader_darkness: int, vader_control: int,
                       has_kyber_gauntlets: bool, experience: int) -> Tuple[bool, str]:
        """
        Check if Vader can learn a Force power.
        Returns (can_learn, reason_if_not)
        """
        if power_id not in self.available_powers:
            return False, "Power not found"
        
        power = self.available_powers[power_id]
        
        if power.learned:
            return False, "Already learned"
        
        # Level requirement
        if vader_level < power.requires_level:
            return False, f"Requires level {power.requires_level}"
        
        # Darkness requirement
        if vader_darkness < power.requires_darkness:
            return False, f"Requires {power.requires_darkness} darkness (currently {vader_darkness})"
        
        # Control requirement
        if vader_control < power.requires_control:
            return False, f"Requires {power.requires_control} control (currently {vader_control})"
        
        # Experience cost
        if experience < power.experience_cost:
            return False, f"Requires {power.experience_cost} experience (have {experience})"
        
        # Prerequisite powers
        for req_power_id in power.requires_powers:
            if req_power_id not in self.learned_powers:
                req_name = self.available_powers[req_power_id].name
                return False, f"Requires: {req_name}"
        
        # Special requirements
        if power.requires_kyber_gauntlets and not has_kyber_gauntlets:
            return False, "Requires Kyber-Enhanced Gauntlets upgrade"
        
        return True, "Can learn"
    
    def learn_power(self, power_id: str) -> Tuple[bool, str]:
        """
        Learn a Force power.
        Returns (success, message)
        """
        if power_id not in self.available_powers:
            return False, "Power not found"
        
        power = self.available_powers[power_id]
        power.learned = True
        self.learned_powers[power_id] = power
        
        # Special handling for Force Lightning
        if power_id == "force_lightning":
            self.force_lightning_unlocked = True
        
        message = f"Learned: {power.name}\n{power.description}"
        
        if power.suit_damage_risk > 0:
            message += f"\n[WARNING] Using this power has {power.suit_damage_risk}% chance to damage suit"
        
        return True, message
    
    def can_use_power(self, power_id: str, current_force_points: int) -> Tuple[bool, str]:
        """
        Check if a power can be used right now.
        Returns (can_use, reason_if_not)
        """
        if power_id not in self.learned_powers:
            return False, "Power not learned"
        
        power = self.learned_powers[power_id]
        
        # Check cooldown
        if power.current_cooldown > 0:
            return False, f"On cooldown: {power.current_cooldown} turns remaining"
        
        # Check Force points
        if current_force_points < power.force_point_cost:
            return False, f"Need {power.force_point_cost} Force Points (have {current_force_points})"
        
        return True, "Can use"
    
    def use_power(self, power_id: str, vader_darkness: int, vader_rage: int,
                  suit_system=None) -> Tuple[bool, str, Dict]:
        """
        Use a Force power. Calculate effects and handle consequences.
        Returns (success, message, effects_dict)
        """
        if power_id not in self.learned_powers:
            return False, "Power not learned", {}
        
        power = self.learned_powers[power_id]
        
        # Track legendary power usage
        if power.tier == ForcePowerTier.LEGENDARY:
            self.legendary_uses_this_combat += 1
        
        # Calculate damage/effectiveness
        final_damage = power.base_damage
        
        if power.scales_with_darkness:
            darkness_bonus = (vader_darkness // 10) * 5  # +5 damage per 10 darkness
            final_damage += darkness_bonus
        
        if power.scales_with_rage:
            rage_bonus = (vader_rage // 10) * 3  # +3 damage per 10 rage
            final_damage += rage_bonus
        
        # Set cooldown
        power.current_cooldown = power.cooldown_turns
        
        # Track usage
        self.force_points_spent_total += power.force_point_cost
        self.powers_used_count[power_id] = self.powers_used_count.get(power_id, 0) + 1
        
        # Increase mastery
        power.mastery_level = min(100, power.mastery_level + 2)
        
        # Handle Force Lightning special case
        suit_damage = 0
        lightning_success = True
        if power_id == "force_lightning":
            self.force_lightning_attempts += 1
            
            # Random chance to damage suit
            import random
            if random.randint(1, 100) <= power.suit_damage_risk:
                suit_damage = random.randint(10, 25)
                if suit_system:
                    suit_system.take_suit_damage(suit_damage)
            
            # Success rate increases with mastery
            success_chance = 60 + (power.mastery_level // 2)  # 60-110% success
            if random.randint(1, 100) > success_chance:
                lightning_success = False
                final_damage = final_damage // 3  # Weak, uncontrolled burst
            else:
                self.force_lightning_successes += 1
        
        # Add to active effects if duration > 1
        if power.duration_turns > 1:
            self.active_effects[power_id] = power.duration_turns
        
        effects = {
            "damage": final_damage,
            "area_effect": power.area_effect,
            "duration": power.duration_turns,
            "suit_damage": suit_damage,
            "force_points_spent": power.force_point_cost
        }
        
        message = f"Used: {power.name}"
        if final_damage > 0:
            message += f" - Dealt {final_damage} damage"
        
        if power_id == "force_lightning":
            if not lightning_success:
                message += "\n[UNSTABLE] Force Lightning partially failed due to cybernetic limitations!"
            if suit_damage > 0:
                message += f"\n[WARNING] Suit damaged: -{suit_damage}% integrity"
        
        return True, message, effects
    
    def update_cooldowns(self):
        """Reduce cooldowns by 1 turn. Call at end of each turn."""
        for power in self.learned_powers.values():
            if power.current_cooldown > 0:
                power.current_cooldown -= 1
        
        # Update active effect durations
        expired_effects = []
        for power_id, turns_remaining in self.active_effects.items():
            self.active_effects[power_id] = turns_remaining - 1
            if self.active_effects[power_id] <= 0:
                expired_effects.append(power_id)
        
        # Remove expired effects
        for power_id in expired_effects:
            del self.active_effects[power_id]
    
    def reset_combat_tracking(self):
        """Reset combat-specific tracking. Call at start of each combat."""
        self.legendary_uses_this_combat = 0
        self.force_sensitive_kills = 0
    
    def on_enemy_killed(self, enemy_is_force_sensitive: bool = False) -> int:
        """
        Called when an enemy is killed. Returns bonus FP gained.
        """
        bonus_fp = 5  # Base bonus for any kill with lightsaber/Force
        
        if enemy_is_force_sensitive:
            bonus_fp = 10  # More FP from Force-sensitive enemies
            self.force_sensitive_kills += 1
        
        return bonus_fp
    
    def check_legendary_exhaustion(self, vader) -> bool:
        """
        Check if using too many legendary powers causes exhaustion.
        Returns True if exhaustion applied.
        """
        if self.legendary_uses_this_combat >= 3:
            # Force exhaustion penalty
            vader.force_exhaustion_turns = 3  # 3 turns of reduced regen
            self.legendary_uses_this_combat = 0  # Reset counter
            return True
        return False
    
    def get_powers_by_category(self, category: ForcePowerCategory) -> List[ForcePower]:
        """Get all available powers in a category."""
        return [p for p in self.available_powers.values() if p.category == category]
    
    def get_powers_by_tier(self, tier: ForcePowerTier) -> List[ForcePower]:
        """Get all powers of a specific tier."""
        return [p for p in self.available_powers.values() if p.tier == tier]
    
    def get_learnable_powers(self, vader_level: int, vader_darkness: int,
                            vader_control: int, has_kyber_gauntlets: bool,
                            experience: int) -> List[ForcePower]:
        """Get list of powers that can currently be learned."""
        learnable = []
        for power_id, power in self.available_powers.items():
            can_learn, _ = self.can_learn_power(
                power_id, vader_level, vader_darkness, vader_control,
                has_kyber_gauntlets, experience
            )
            if can_learn:
                learnable.append(power)
        return learnable
    
    def get_force_power_summary(self) -> Dict:
        """Return summary of Force power status."""
        return {
            "total_powers": len(self.available_powers),
            "learned_powers": len(self.learned_powers),
            "force_points_spent_total": self.force_points_spent_total,
            "most_used_power": max(self.powers_used_count.items(), 
                                  key=lambda x: x[1])[0] if self.powers_used_count else None,
            "force_lightning_unlocked": self.force_lightning_unlocked,
            "force_lightning_success_rate": f"{(self.force_lightning_successes / self.force_lightning_attempts * 100):.1f}%" if self.force_lightning_attempts > 0 else "N/A",
            "active_effects": list(self.active_effects.keys())
        }
    
    def __repr__(self):
        return f"<ForcePowerSystem: {len(self.learned_powers)}/{len(self.available_powers)} powers learned>"


# Example usage and testing
if __name__ == "__main__":
    force_system = ForcePowerSystem()
    
    print("=== Vader's Force Powers ===")
    print(f"Total Powers: {len(force_system.available_powers)}")
    print(f"Starting Powers: {len(force_system.learned_powers)}")
    
    # Show powers by category
    print("\n=== Powers by Category ===")
    for category in ForcePowerCategory:
        powers = force_system.get_powers_by_category(category)
        print(f"\n{category.value.upper()}: {len(powers)} powers")
        for power in powers[:3]:  # Show first 3 of each category
            tier_marker = "★" * power.tier.value
            learned = "✓" if power.learned else " "
            print(f"  [{learned}] {tier_marker} {power.name} ({power.force_point_cost} FP)")
    
    # Show Force Lightning requirements
    print("\n=== FORCE LIGHTNING Requirements ===")
    fl_power = force_system.available_powers["force_lightning"]
    print(f"Name: {fl_power.name}")
    print(f"Cost: {fl_power.force_point_cost} Force Points")
    print(f"Requirements:")
    print(f"  - Level: {fl_power.requires_level}")
    print(f"  - Darkness: {fl_power.requires_darkness}")
    print(f"  - Control: {fl_power.requires_control}")
    print(f"  - Kyber Gauntlets: {fl_power.requires_kyber_gauntlets}")
    print(f"  - Experience Cost: {fl_power.experience_cost}")
    print(f"Risks: {fl_power.suit_damage_risk}% chance to damage suit")
    
    # Test learning a power
    print("\n=== Learning a Power ===")
    can_learn, reason = force_system.can_learn_power(
        "force_grip", vader_level=3, vader_darkness=40,
        vader_control=30, has_kyber_gauntlets=False, experience=200
    )
    print(f"Can learn Force Grip: {can_learn} - {reason}")
    
    if can_learn:
        success, message = force_system.learn_power("force_grip")
        print(message)
    
    # Test using a power
    print("\n=== Using Force Choke ===")
    can_use, reason = force_system.can_use_power("force_choke", current_force_points=50)
    print(f"Can use Force Choke: {can_use} - {reason}")
    
    if can_use:
        success, message, effects = force_system.use_power(
            "force_choke", vader_darkness=60, vader_rage=70
        )
        print(message)
        print(f"Damage dealt: {effects['damage']}")
    
    # Show summary
    print("\n=== Force Power Summary ===")
    summary = force_system.get_force_power_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")