"""
Darth Vader Suit System
Manages suit integrity, pain, life support, upgrades, and Palpatine suspicion.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SuitComponent(Enum):
    """Different components of Vader's suit that can be damaged or upgraded"""
    HELMET = "helmet"
    CHEST_PLATE = "chest_plate"
    RESPIRATOR = "respirator"
    LIFE_SUPPORT = "life_support"
    LIMBS = "limbs"
    ARMOR = "armor"
    CONTROL_PANEL = "control_panel"


@dataclass
class SuitUpgrade:
    """Represents a potential suit upgrade"""
    id: str
    name: str
    description: str
    component: SuitComponent
    tier: int  # 1-5, higher = more powerful/suspicious
    
    # Costs
    credits_cost: int
    materials_required: Dict[str, int] = field(default_factory=dict)
    imperial_favor_required: int = 0
    
    # Effects (positive and negative)
    integrity_bonus: int = 0
    pain_reduction: int = 0
    mobility_bonus: int = 0
    strength_bonus: int = 0
    
    # Trade-offs
    dark_side_fuel_penalty: int = 0
    palpatine_suspicion: int = 0
    
    # Requirements
    requires_upgrades: List[str] = field(default_factory=list)
    min_level: int = 1
    
    installed: bool = False
    hidden_from_palpatine: bool = False  # Did player try to hide this?


class SuitSystem:
    """
    Manages Vader's life support suit with damage, maintenance, and upgrades.
    Includes Palpatine suspicion mechanics and loyalty testing.
    """
    
    def __init__(self):
        # Overall suit integrity (0-100)
        self.integrity = 100
        
        # Component-specific integrity
        self.component_integrity: Dict[SuitComponent, int] = {
            component: 100 for component in SuitComponent
        }
        
        # Pain and life support
        self.base_pain_level = 40  # Constant baseline pain from injuries
        self.current_pain_level = 40
        self.pain_threshold = 60
        
        # Respiratory function
        self.respiratory_efficiency = 100
        self.breathing_disrupted = False
        
        # Life support status
        self.life_support_active = True
        self.life_support_power = 100
        self.critical_condition = False
        
        # Upgrades
        self.installed_upgrades: Dict[str, SuitUpgrade] = {}
        self.available_upgrades: Dict[str, SuitUpgrade] = self._initialize_upgrades()
        
        # Palpatine suspicion tracking
        self.total_suspicion = 0
        self.suspicion_since_last_meeting = 0  # Tracks upgrade rate
        self.missions_since_palpatine_meeting = 0
        self.palpatine_knows_upgrades: List[str] = []
        self.loyalty_test_triggered = False
        self.loyalty_test_failed = False
        
        # Resources for upgrades
        self.credits = 5000
        self.materials: Dict[str, int] = {
            "durasteel": 10,
            "electronics": 5,
            "bacta": 3,
            "kyber_fragments": 0,
            "ancient_artifacts": 0,
            "prototype_components": 0,
        }
        
        # Maintenance tracking
        self.missions_since_maintenance = 0
        self.needs_maintenance = False
    
    def _initialize_upgrades(self) -> Dict[str, SuitUpgrade]:
        """Initialize all possible suit upgrades across 5 tiers"""
        upgrades = {}
        
        # ============================================================
        # TIER 1: BASIC IMPERIAL IMPROVEMENTS (Low Suspicion)
        # Standard military upgrades, barely raises eyebrows
        # ============================================================
        
        upgrades["reinforced_armor_t1"] = SuitUpgrade(
            id="reinforced_armor_t1",
            name="Reinforced Armor Plating",
            description="Durasteel-enhanced armor reduces damage taken.",
            component=SuitComponent.ARMOR,
            tier=1,
            credits_cost=2000,
            materials_required={"durasteel": 5},
            integrity_bonus=15,
            palpatine_suspicion=3
        )
        
        upgrades["improved_respirator_t1"] = SuitUpgrade(
            id="improved_respirator_t1",
            name="Enhanced Respiratory System",
            description="Better air filtration and oxygen delivery. Slightly reduces pain.",
            component=SuitComponent.RESPIRATOR,
            tier=1,
            credits_cost=2500,
            materials_required={"electronics": 3, "bacta": 1},
            pain_reduction=5,
            dark_side_fuel_penalty=2,
            palpatine_suspicion=3
        )
        
        upgrades["servo_limbs_t1"] = SuitUpgrade(
            id="servo_limbs_t1",
            name="Upgraded Servo Motors",
            description="Improved artificial limb response. Increases mobility slightly.",
            component=SuitComponent.LIMBS,
            tier=1,
            credits_cost=2000,
            materials_required={"electronics": 4, "durasteel": 3},
            mobility_bonus=1,
            palpatine_suspicion=2
        )
        
        upgrades["life_support_t1"] = SuitUpgrade(
            id="life_support_t1",
            name="Enhanced Life Support",
            description="Improved medical monitoring and stabilization systems.",
            component=SuitComponent.LIFE_SUPPORT,
            tier=1,
            credits_cost=2500,
            materials_required={"electronics": 4, "bacta": 2},
            integrity_bonus=10,
            pain_reduction=3,
            palpatine_suspicion=2
        )
        
        upgrades["helmet_systems_t1"] = SuitUpgrade(
            id="helmet_systems_t1",
            name="Enhanced Sensor Suite",
            description="Improved visual and auditory sensors. Better battlefield awareness.",
            component=SuitComponent.HELMET,
            tier=1,
            credits_cost=1800,
            materials_required={"electronics": 5},
            palpatine_suspicion=2
        )
        
        # ============================================================
        # TIER 2: MILITARY-GRADE (Moderate Suspicion)
        # Combat-focused upgrades that military commanders might have
        # ============================================================
        
        upgrades["combat_armor_t2"] = SuitUpgrade(
            id="combat_armor_t2",
            name="Combat-Grade Armor Plating",
            description="Military specification armor. Significantly more durable.",
            component=SuitComponent.ARMOR,
            tier=2,
            credits_cost=4000,
            materials_required={"durasteel": 8, "electronics": 3},
            requires_upgrades=["reinforced_armor_t1"],
            integrity_bonus=20,
            palpatine_suspicion=6,
            min_level=2
        )
        
        upgrades["advanced_respirator_t2"] = SuitUpgrade(
            id="advanced_respirator_t2",
            name="Advanced Breathing Apparatus",
            description="Military-grade respirator with enhanced oxygen processing.",
            component=SuitComponent.RESPIRATOR,
            tier=2,
            credits_cost=4500,
            materials_required={"electronics": 6, "bacta": 2},
            requires_upgrades=["improved_respirator_t1"],
            pain_reduction=8,
            dark_side_fuel_penalty=4,
            palpatine_suspicion=7,
            min_level=2
        )
        
        upgrades["combat_servos_t2"] = SuitUpgrade(
            id="combat_servos_t2",
            name="Combat-Grade Servo System",
            description="Military-spec servo motors. Notable mobility improvement.",
            component=SuitComponent.LIMBS,
            tier=2,
            credits_cost=4000,
            materials_required={"electronics": 7, "durasteel": 5},
            requires_upgrades=["servo_limbs_t1"],
            mobility_bonus=1,
            strength_bonus=1,
            palpatine_suspicion=6,
            min_level=2
        )
        
        upgrades["redundant_life_support_t2"] = SuitUpgrade(
            id="redundant_life_support_t2",
            name="Redundant Life Support Systems",
            description="Backup systems prevent critical failures.",
            component=SuitComponent.LIFE_SUPPORT,
            tier=2,
            credits_cost=4000,
            materials_required={"electronics": 6, "durasteel": 4},
            requires_upgrades=["life_support_t1"],
            integrity_bonus=15,
            palpatine_suspicion=5,
            min_level=3
        )
        
        upgrades["tactical_hud_t2"] = SuitUpgrade(
            id="tactical_hud_t2",
            name="Tactical HUD Enhancement",
            description="Advanced heads-up display with threat analysis.",
            component=SuitComponent.HELMET,
            tier=2,
            credits_cost=3500,
            materials_required={"electronics": 7},
            requires_upgrades=["helmet_systems_t1"],
            palpatine_suspicion=4,
            min_level=2
        )
        
        # ============================================================
        # TIER 3: ADVANCED PROTOTYPE (Higher Suspicion)
        # Experimental Imperial tech, raises questions
        # ============================================================
        
        upgrades["prototype_armor_t3"] = SuitUpgrade(
            id="prototype_armor_t3",
            name="Prototype Ablative Armor",
            description="Experimental armor that dissipates energy weapon damage.",
            component=SuitComponent.ARMOR,
            tier=3,
            credits_cost=7000,
            materials_required={"durasteel": 12, "prototype_components": 2},
            requires_upgrades=["combat_armor_t2"],
            integrity_bonus=25,
            palpatine_suspicion=12,
            min_level=4
        )
        
        upgrades["pain_dampeners_t3"] = SuitUpgrade(
            id="pain_dampeners_t3",
            name="Neural Pain Dampeners",
            description="Reduces constant pain significantly. Improves control but reduces rage.",
            component=SuitComponent.CONTROL_PANEL,
            tier=3,
            credits_cost=6000,
            materials_required={"electronics": 8, "bacta": 4},
            requires_upgrades=["advanced_respirator_t2"],
            pain_reduction=15,
            dark_side_fuel_penalty=10,
            palpatine_suspicion=15,
            min_level=4
        )
        
        upgrades["precision_servos_t3"] = SuitUpgrade(
            id="precision_servos_t3",
            name="Precision Control Servos",
            description="Advanced servo control for enhanced dexterity and precision.",
            component=SuitComponent.LIMBS,
            tier=3,
            credits_cost=6500,
            materials_required={"electronics": 10, "prototype_components": 2},
            requires_upgrades=["combat_servos_t2"],
            mobility_bonus=2,
            palpatine_suspicion=10,
            min_level=4
        )
        
        upgrades["auto_medical_t3"] = SuitUpgrade(
            id="auto_medical_t3",
            name="Automated Medical Systems",
            description="Integrated medical droids monitor and treat injuries automatically.",
            component=SuitComponent.LIFE_SUPPORT,
            tier=3,
            credits_cost=6000,
            materials_required={"electronics": 9, "bacta": 5},
            requires_upgrades=["redundant_life_support_t2"],
            integrity_bonus=10,
            pain_reduction=7,
            dark_side_fuel_penalty=5,
            palpatine_suspicion=13,
            min_level=5
        )
        
        upgrades["combat_analysis_t3"] = SuitUpgrade(
            id="combat_analysis_t3",
            name="Combat Prediction AI",
            description="Experimental AI assists in predicting enemy movements.",
            component=SuitComponent.HELMET,
            tier=3,
            credits_cost=5500,
            materials_required={"electronics": 11, "prototype_components": 1},
            requires_upgrades=["tactical_hud_t2"],
            palpatine_suspicion=11,
            min_level=4
        )
        
        # ============================================================
        # TIER 4: EXPERIMENTAL SITH TECHNOLOGY (High Suspicion)
        # Dark side infused tech, will definitely catch Palpatine's eye
        # ============================================================
        
        upgrades["sith_armor_t4"] = SuitUpgrade(
            id="sith_armor_t4",
            name="Sith Alchemical Armor",
            description="Armor infused with dark side energy from ancient Sith techniques.",
            component=SuitComponent.ARMOR,
            tier=4,
            credits_cost=10000,
            materials_required={"ancient_artifacts": 2, "durasteel": 15},
            requires_upgrades=["prototype_armor_t3"],
            integrity_bonus=20,
            palpatine_suspicion=20,
            min_level=6
        )
        
        upgrades["meditation_chamber_t4"] = SuitUpgrade(
            id="meditation_chamber_t4",
            name="Integrated Meditation Chamber",
            description="Miniaturized meditation chamber tech. Accelerates Force recovery.",
            component=SuitComponent.CHEST_PLATE,
            tier=4,
            credits_cost=9000,
            materials_required={"electronics": 12, "ancient_artifacts": 1, "bacta": 6},
            requires_upgrades=["pain_dampeners_t3"],
            pain_reduction=12,
            dark_side_fuel_penalty=8,
            palpatine_suspicion=22,
            min_level=6
        )
        
        upgrades["force_reactive_limbs_t4"] = SuitUpgrade(
            id="force_reactive_limbs_t4",
            name="Force-Reactive Cybernetics",
            description="Limbs that respond to Force impulses. Near-organic response time.",
            component=SuitComponent.LIMBS,
            tier=4,
            credits_cost=10000,
            materials_required={"kyber_fragments": 3, "prototype_components": 4},
            requires_upgrades=["precision_servos_t3"],
            mobility_bonus=2,
            strength_bonus=1,
            palpatine_suspicion=18,
            min_level=6
        )
        
        upgrades["kyber_gauntlets_t4"] = SuitUpgrade(
            id="kyber_gauntlets_t4",
            name="Kyber-Enhanced Gauntlets",
            description="EXPERIMENTAL: Gauntlets with kyber crystals. Required for Force Lightning.",
            component=SuitComponent.LIMBS,
            tier=4,
            credits_cost=12000,
            materials_required={"kyber_fragments": 5, "ancient_artifacts": 2},
            requires_upgrades=["force_reactive_limbs_t4"],
            palpatine_suspicion=25,
            min_level=7
        )
        
        upgrades["force_sense_amplifier_t4"] = SuitUpgrade(
            id="force_sense_amplifier_t4",
            name="Force Sense Amplification Matrix",
            description="Ancient Sith technology that enhances Force perception.",
            component=SuitComponent.HELMET,
            tier=4,
            credits_cost=8500,
            materials_required={"ancient_artifacts": 2, "electronics": 10},
            requires_upgrades=["combat_analysis_t3"],
            palpatine_suspicion=19,
            min_level=6
        )
        
        upgrades["sith_life_support_t4"] = SuitUpgrade(
            id="sith_life_support_t4",
            name="Sith Regeneration Matrix",
            description="Life support infused with Sith alchemy. Accelerated healing.",
            component=SuitComponent.LIFE_SUPPORT,
            tier=4,
            credits_cost=9500,
            materials_required={"ancient_artifacts": 3, "bacta": 8},
            requires_upgrades=["auto_medical_t3"],
            integrity_bonus=15,
            pain_reduction=10,
            dark_side_fuel_penalty=6,
            palpatine_suspicion=21,
            min_level=6
        )
        
        # ============================================================
        # TIER 5: FORBIDDEN/ANCIENT (Very High Suspicion)
        # Pinnacle technology that makes you nearly unstoppable
        # Will definitely trigger Palpatine's loyalty test
        # ============================================================
        
        upgrades["cortosis_armor_t5"] = SuitUpgrade(
            id="cortosis_armor_t5",
            name="Force-Conductive Cortosis Weave",
            description="Legendary armor that channels Force energy and resists lightsabers.",
            component=SuitComponent.ARMOR,
            tier=5,
            credits_cost=15000,
            materials_required={"ancient_artifacts": 4, "kyber_fragments": 4, "durasteel": 20},
            requires_upgrades=["sith_armor_t4"],
            integrity_bonus=30,
            palpatine_suspicion=35,
            min_level=8
        )
        
        upgrades["ancient_respirator_t5"] = SuitUpgrade(
            id="ancient_respirator_t5",
            name="Ancient Sith Lord Respirator",
            description="Recovered from Korriban tomb. Nearly eliminates pain.",
            component=SuitComponent.RESPIRATOR,
            tier=5,
            credits_cost=13000,
            materials_required={"ancient_artifacts": 5, "bacta": 10},
            requires_upgrades=["meditation_chamber_t4"],
            pain_reduction=25,
            dark_side_fuel_penalty=15,
            palpatine_suspicion=30,
            min_level=8
        )
        
        upgrades["perfect_cybernetics_t5"] = SuitUpgrade(
            id="perfect_cybernetics_t5",
            name="Perfected Cybernetic Limbs",
            description="The pinnacle of cybernetic technology. Nearly organic performance.",
            component=SuitComponent.LIMBS,
            tier=5,
            credits_cost=16000,
            materials_required={"prototype_components": 8, "ancient_artifacts": 3, "kyber_fragments": 3},
            requires_upgrades=["kyber_gauntlets_t4"],
            mobility_bonus=3,
            strength_bonus=2,
            pain_reduction=10,
            dark_side_fuel_penalty=7,
            palpatine_suspicion=40,
            min_level=9
        )
        
        upgrades["omniscient_helmet_t5"] = SuitUpgrade(
            id="omniscient_helmet_t5",
            name="Omniscient Sith Mask",
            description="Ancient mask that grants unparalleled Force sight and battle precognition.",
            component=SuitComponent.HELMET,
            tier=5,
            credits_cost=14000,
            materials_required={"ancient_artifacts": 6, "kyber_fragments": 2},
            requires_upgrades=["force_sense_amplifier_t4"],
            palpatine_suspicion=33,
            min_level=8
        )
        
        upgrades["immortal_life_support_t5"] = SuitUpgrade(
            id="immortal_life_support_t5",
            name="Eternal Vitality Matrix",
            description="Forbidden Sith technology. Sustains life through dark side energy alone.",
            component=SuitComponent.LIFE_SUPPORT,
            tier=5,
            credits_cost=17000,
            materials_required={"ancient_artifacts": 7, "kyber_fragments": 4},
            requires_upgrades=["sith_life_support_t4"],
            integrity_bonus=25,
            pain_reduction=20,
            dark_side_fuel_penalty=12,
            palpatine_suspicion=38,
            min_level=9
        )
        
        return upgrades
    
    def get_overall_integrity(self) -> int:
        """Calculate overall suit integrity from components"""
        total = sum(self.component_integrity.values())
        average = total // len(self.component_integrity)
        self.integrity = average
        return self.integrity
    
    def take_suit_damage(self, amount: int, component: Optional[SuitComponent] = None) -> List[str]:
        """
        Damage the suit. Can target specific component or general damage.
        Returns list of status messages about consequences.
        """
        messages = []
        
        if component:
            old_value = self.component_integrity[component]
            self.component_integrity[component] = max(0, old_value - amount)
            messages.append(f"{component.value.replace('_', ' ').title()} damaged: {self.component_integrity[component]}%")
            
            # Special effects for critical components
            if component == SuitComponent.RESPIRATOR and self.component_integrity[component] < 30:
                self.breathing_disrupted = True
                messages.append("BREATHING DISRUPTED - Force regeneration reduced!")
            
            if component == SuitComponent.LIFE_SUPPORT and self.component_integrity[component] < 20:
                self.critical_condition = True
                messages.append("CRITICAL: Life support failing!")
        else:
            # General damage distributed across components
            for comp in self.component_integrity:
                damage_amount = amount // len(self.component_integrity)
                self.component_integrity[comp] = max(0, self.component_integrity[comp] - damage_amount)
        
        self.get_overall_integrity()
        
        if self.integrity < 30:
            messages.append("WARNING: Suit integrity critical!")
            self.needs_maintenance = True
        
        # Increase pain with damage
        pain_increase = amount // 2
        self.current_pain_level = min(100, self.current_pain_level + pain_increase)
        
        return messages
    
    def repair_suit(self, amount: int, component: Optional[SuitComponent] = None) -> str:
        """Repair suit damage."""
        if component:
            old_value = self.component_integrity[component]
            self.component_integrity[component] = min(100, old_value + amount)
            
            if component == SuitComponent.RESPIRATOR and self.component_integrity[component] >= 50:
                self.breathing_disrupted = False
            
            if component == SuitComponent.LIFE_SUPPORT and self.component_integrity[component] >= 40:
                self.critical_condition = False
            
            return f"{component.value.replace('_', ' ').title()} repaired to {self.component_integrity[component]}%"
        else:
            for comp in self.component_integrity:
                repair_amount = amount // len(self.component_integrity)
                self.component_integrity[comp] = min(100, self.component_integrity[comp] + repair_amount)
            
            self.get_overall_integrity()
            self.breathing_disrupted = False
            self.critical_condition = False
            
            return f"Suit repaired to {self.integrity}% integrity"
    
    def perform_maintenance(self) -> Tuple[str, int]:
        """Full maintenance cycle. Returns message and cost."""
        cost = 500 + (self.missions_since_maintenance * 100)
        
        if self.credits >= cost:
            for comp in self.component_integrity:
                self.component_integrity[comp] = 100
            
            self.get_overall_integrity()
            self.current_pain_level = self.base_pain_level
            self.breathing_disrupted = False
            self.critical_condition = False
            self.missions_since_maintenance = 0
            self.needs_maintenance = False
            self.credits -= cost
            
            return f"Maintenance complete. Suit fully restored. Cost: {cost} credits.", cost
        else:
            return f"Insufficient credits. Need {cost}, have {self.credits}.", 0
    
    def check_palpatine_suspicion_trigger(self) -> Tuple[bool, str]:
        """
        Check if upgrade rate triggers Palpatine's loyalty test.
        Returns (test_triggered, reason)
        """
        if self.loyalty_test_triggered:
            return False, "Loyalty test already occurred"
        
        # Trigger conditions
        suspicion_rate_threshold = 30  # More than 30 suspicion since last meeting
        rapid_upgrade_threshold = 3  # 3+ upgrades in short time
        
        recent_upgrades = sum(1 for u in self.installed_upgrades.values() 
                            if u.id not in self.palpatine_knows_upgrades)
        
        if self.suspicion_since_last_meeting >= suspicion_rate_threshold:
            return True, f"Upgraded too much too quickly (+{self.suspicion_since_last_meeting} suspicion)"
        
        if recent_upgrades >= rapid_upgrade_threshold and self.missions_since_palpatine_meeting < 5:
            return True, f"{recent_upgrades} upgrades in {self.missions_since_palpatine_meeting} missions"
        
        # Very high tier upgrades trigger immediately
        for upgrade_id, upgrade in self.installed_upgrades.items():
            if upgrade.tier >= 5 and upgrade_id not in self.palpatine_knows_upgrades:
                return True, f"Tier 5 upgrade detected: {upgrade.name}"
        
        return False, "Suspicion within acceptable levels"
    
    def trigger_loyalty_test(self) -> Dict:
        """
        Trigger Palpatine's loyalty test (unwinnable boss fight).
        Returns dict with test results.
        """
        self.loyalty_test_triggered = True
        self.loyalty_test_failed = True  # Vader always loses this fight
        
        # Reset to basic suit
        upgrades_lost = list(self.installed_upgrades.keys())
        self.installed_upgrades.clear()
        
        # Reset all components to base state
        for comp in self.component_integrity:
            self.component_integrity[comp] = 100
        
        # Reset stats
        self.base_pain_level = 40
        self.current_pain_level = 40
        self.total_suspicion = 0
        self.suspicion_since_last_meeting = 0
        self.palpatine_knows_upgrades.clear()
        
        return {
            "test_triggered": True,
            "result": "FAILED",
            "upgrades_lost": upgrades_lost,
            "message": "The Emperor has stripped your suit of all upgrades. You have been reminded of your place."
        }
    
    def meet_with_palpatine(self) -> Dict:
        """
        Player meets with Palpatine. Updates his knowledge and resets suspicion tracking.
        Returns dict with meeting results.
        """
        # Check if loyalty test should trigger
        test_triggered, reason = self.check_palpatine_suspicion_trigger()
        
        if test_triggered:
            return self.trigger_loyalty_test()
        
        # Normal meeting - Palpatine becomes aware of current upgrades
        new_upgrades = [u_id for u_id in self.installed_upgrades.keys() 
                       if u_id not in self.palpatine_knows_upgrades]
        
        self.palpatine_knows_upgrades.extend(new_upgrades)
        self.suspicion_since_last_meeting = 0
        self.missions_since_palpatine_meeting = 0
        
        # Calculate his reaction based on upgrade tier
        visible_high_tier = sum(1 for u_id in new_upgrades 
                               if self.installed_upgrades[u_id].tier >= 4)
        
        if visible_high_tier > 0:
            reaction = "suspicious"
            message = "The Emperor's eyes linger on your suit modifications..."
        elif len(new_upgrades) > 0:
            reaction = "aware"
            message = "The Emperor notes your improvements with mild interest."
        else:
            reaction = "satisfied"
            message = "The Emperor is pleased with your performance."
        
        return {
            "test_triggered": False,
            "reaction": reaction,
            "new_upgrades_noticed": new_upgrades,
            "message": message
        }
    
    def can_install_upgrade(self, upgrade_id: str, vader_level: int, 
                           imperial_favor: int) -> Tuple[bool, str]:
        """Check if an upgrade can be installed."""
        if upgrade_id not in self.available_upgrades:
            return False, "Upgrade not found"
        
        upgrade = self.available_upgrades[upgrade_id]
        
        if upgrade.installed:
            return False, "Already installed"
        
        if vader_level < upgrade.min_level:
            return False, f"Requires level {upgrade.min_level}"
        
        for req_id in upgrade.requires_upgrades:
            if req_id not in self.installed_upgrades:
                req_name = self.available_upgrades[req_id].name
                return False, f"Requires: {req_name}"
        
        if self.credits < upgrade.credits_cost:
            return False, f"Need {upgrade.credits_cost} credits (have {self.credits})"
        
        for material, amount in upgrade.materials_required.items():
            if self.materials.get(material, 0) < amount:
                return False, f"Need {amount} {material} (have {self.materials.get(material, 0)})"
        
        if imperial_favor < upgrade.imperial_favor_required:
            return False, f"Insufficient Imperial favor"
        
        return True, "Can install"
    
    def install_upgrade(self, upgrade_id: str, vader_stats, 
                       attempt_hide: bool = False) -> Tuple[bool, str, Dict]:
        """
        Install an upgrade. Apply stat changes and costs.
        Returns (success, message, effects_dict)
        """
        if upgrade_id not in self.available_upgrades:
            return False, "Upgrade not found", {}
        
        upgrade = self.available_upgrades[upgrade_id]
        
        # Deduct costs
        self.credits -= upgrade.credits_cost
        for material, amount in upgrade.materials_required.items():
            self.materials[material] -= amount
        
        # Apply bonuses
        if upgrade.pain_reduction > 0:
            self.base_pain_level = max(0, self.base_pain_level - upgrade.pain_reduction)
            self.current_pain_level = max(0, self.current_pain_level - upgrade.pain_reduction)
        
        if upgrade.mobility_bonus > 0:
            vader_stats.dexterity += upgrade.mobility_bonus
        
        if upgrade.strength_bonus > 0:
            vader_stats.strength += upgrade.strength_bonus
        
        if upgrade.integrity_bonus > 0:
            for comp in self.component_integrity:
                self.component_integrity[comp] = min(100, 
                    self.component_integrity[comp] + upgrade.integrity_bonus)
        
        # Mark as installed
        upgrade.installed = True
        upgrade.hidden_from_palpatine = attempt_hide
        self.installed_upgrades[upgrade_id] = upgrade
        
        # Update suspicion
        suspicion_added = upgrade.palpatine_suspicion
        if attempt_hide and upgrade.tier <= 3:
            # Can partially hide lower tier upgrades
            suspicion_added = suspicion_added // 2
        
        self.total_suspicion += suspicion_added
        self.suspicion_since_last_meeting += suspicion_added
        
        message = f"Installed: {upgrade.name}\n{upgrade.description}"
        
        effects = {
            "suspicion_added": suspicion_added,
            "pain_reduction": upgrade.pain_reduction,
            "mobility_bonus": upgrade.mobility_bonus,
            "strength_bonus": upgrade.strength_bonus,
            "dark_side_penalty": upgrade.dark_side_fuel_penalty
        }
        
        if suspicion_added > 15:
            message += f"\n[WARNING] High suspicion increase: +{suspicion_added}"
        
        return True, message, effects
    
    def get_pain_modifier(self) -> Dict[str, int]:
        """Calculate how current pain affects combat and Force use."""
        modifiers = {
            "force_power_bonus": 0,
            "control_penalty": 0,
            "attack_penalty": 0,
        }
        
        if self.current_pain_level > self.pain_threshold:
            excess_pain = self.current_pain_level - self.pain_threshold
            modifiers["force_power_bonus"] = excess_pain // 10
            modifiers["control_penalty"] = excess_pain // 15
            modifiers["attack_penalty"] = excess_pain // 20
        
        return modifiers
    
    def get_force_regen_penalty(self) -> int:
        """
        Calculate Force Point regeneration penalty based on suit damage.
        Returns percentage penalty (0-100).
        """
        penalty = 0
        
        # Breathing disruption severely affects Force regeneration
        if self.breathing_disrupted:
            penalty += 50  # 50% penalty
        
        # Critical life support affects concentration
        if self.critical_condition:
            penalty += 30  # Additional 30% penalty
        
        # Overall suit integrity affects performance
        if self.integrity < 50:
            penalty += 20  # Additional 20% penalty for low integrity
        
        return min(100, penalty)  # Cap at 100% (no regeneration)
    
    def get_upgrades_by_component(self, component: SuitComponent) -> List[SuitUpgrade]:
        """Get all available upgrades for a specific component."""
        return [u for u in self.available_upgrades.values() if u.component == component]
    
    def get_upgrades_by_tier(self, tier: int) -> List[SuitUpgrade]:
        """Get all upgrades of a specific tier."""
        return [u for u in self.available_upgrades.values() if u.tier == tier]
    
    def get_suit_status_summary(self) -> Dict:
        """Return summary of suit status for UI display"""
        return {
            "overall_integrity": f"{self.integrity}%",
            "pain_level": f"{self.current_pain_level}%",
            "life_support": "ACTIVE" if self.life_support_active else "CRITICAL",
            "breathing": "Normal" if not self.breathing_disrupted else "DISRUPTED",
            "needs_maintenance": self.needs_maintenance,
            "installed_upgrades": len(self.installed_upgrades),
            "total_suspicion": self.total_suspicion,
            "suspicion_since_meeting": self.suspicion_since_last_meeting,
            "credits": self.credits,
            "loyalty_test_risk": "HIGH" if self.suspicion_since_last_meeting > 25 else "MODERATE" if self.suspicion_since_last_meeting > 15 else "LOW"
        }
    
    def __repr__(self):
        return f"<SuitSystem: {self.integrity}% integrity, {self.current_pain_level}% pain, {len(self.installed_upgrades)} upgrades, {self.total_suspicion} suspicion>"


# Example usage and testing
if __name__ == "__main__":
    from vader import VaderStats
    
    suit = SuitSystem()
    vader_stats = VaderStats()
    
    print("=== Vader's Suit System ===")
    print(f"Integrity: {suit.integrity}%")
    print(f"Pain Level: {suit.current_pain_level}%")
    print(f"Credits: {suit.credits}")
    print(f"\nTotal Upgrades Available: {len(suit.available_upgrades)}")
    
    # Show upgrades by tier
    for tier in range(1, 6):
        tier_upgrades = suit.get_upgrades_by_tier(tier)
        print(f"\nTier {tier} Upgrades: {len(tier_upgrades)}")
        for upgrade in tier_upgrades[:2]:  # Show first 2 of each tier
            print(f"  - {upgrade.name} ({upgrade.credits_cost} credits, +{upgrade.palpatine_suspicion} suspicion)")
    
    # Show component upgrade paths
    print("\n=== Limb Upgrade Path ===")
    limb_upgrades = suit.get_upgrades_by_component(SuitComponent.LIMBS)
    for upgrade in limb_upgrades:
        tier_marker = "█" * upgrade.tier
        print(f"{tier_marker} T{upgrade.tier}: {upgrade.name}")
        if upgrade.requires_upgrades:
            print(f"     Requires: {upgrade.requires_upgrades[0]}")
    
    # Test upgrade installation
    print("\n=== Installing Upgrade ===")
    can_install, reason = suit.can_install_upgrade("servo_limbs_t1", vader_level=1, imperial_favor=50)
    print(f"Can install Tier 1 Servos: {can_install} - {reason}")
    
    if can_install:
        success, message, effects = suit.install_upgrade("servo_limbs_t1", vader_stats, attempt_hide=False)
        print(f"\n{message}")
        print(f"Suspicion added: +{effects['suspicion_added']}")
        print(f"New dexterity: {vader_stats.dexterity}")
    
    # Show status
    print("\n=== Suit Status ===")
    status = suit.get_suit_status_summary()
    for key, value in status.items():
        print(f"  {key}: {value}")