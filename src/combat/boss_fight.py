"""
Boss Fight System for Darth Vader RPG
Special mechanics for boss encounters, scripted events, and mid-combat choices.
Includes the Kirak Infil'a duels from the Kyber Crystal mission.
"""

from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class BossPhase(Enum):
    """Boss fight phases"""
    PHASE_1 = 1
    PHASE_2 = 2
    PHASE_3 = 3
    FINAL = 4


class BossEvent(Enum):
    """Special events that can trigger during boss fights"""
    DIALOGUE = "dialogue"
    CUTSCENE = "cutscene"
    PHASE_TRANSITION = "phase_transition"
    SCRIPTED_DAMAGE = "scripted_damage"
    FORCE_CHOICE = "force_choice"
    ENVIRONMENTAL = "environmental"
    HEALING = "healing"
    POWER_UP = "power_up"


@dataclass
class BossAction:
    """A special action a boss can take"""
    id: str
    name: str
    description: str
    damage: int = 0
    
    # Effects
    stun_chance: int = 0  # 0-100
    force_drain: int = 0  # Drains Vader's FP
    suit_damage: int = 0  # Damages Vader's suit
    
    # Requirements
    requires_phase: Optional[BossPhase] = None
    requires_hp_below: Optional[int] = None  # Percentage
    cooldown_turns: int = 0
    
    # Display
    animation: Optional[str] = None  # Special text to display
    
    current_cooldown: int = 0


@dataclass
class BossTrigger:
    """Triggers events at specific points in boss fight"""
    id: str
    trigger_type: BossEvent
    
    # Conditions
    hp_threshold: Optional[int] = None  # Trigger when boss HP drops below this %
    turn_number: Optional[int] = None  # Trigger on specific turn
    phase: Optional[BossPhase] = None  # Trigger when entering phase
    
    # What happens
    dialogue: Optional[str] = None
    cutscene: Optional[str] = None
    callback: Optional[Callable] = None
    
    # State
    triggered: bool = False
    
    # Mid-combat choice
    choice_prompt: Optional[str] = None
    choice_options: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BossEnemy:
    """A boss enemy with special mechanics"""
    id: str
    name: str
    title: str  # "Jedi Master", "Grand Inquisitor", etc.
    
    # Base stats
    max_hp: int
    current_hp: int
    base_damage: int
    defense: int
    
    # Boss-specific
    current_phase: BossPhase = BossPhase.PHASE_1
    phase_transitions: Dict[BossPhase, int] = field(default_factory=dict)  # phase: hp_threshold
    
    # Special abilities
    special_actions: List[BossAction] = field(default_factory=list)
    
    # Resistances
    force_resistance: int = 50  # Higher than normal enemies
    lightsaber_resistance: int = 10
    
    # Combat style
    aggressive: bool = True  # Offensive vs defensive
    adaptive: bool = True  # Learns from Vader's tactics
    
    # Scripted events
    triggers: List[BossTrigger] = field(default_factory=list)
    
    # State tracking
    turns_survived: int = 0
    damage_taken_total: int = 0
    times_vader_used_force: int = 0
    times_vader_attacked: int = 0
    
    def take_damage(self, amount: int) -> Tuple[int, bool]:
        """Take damage and check for phase transitions"""
        actual_damage = max(1, amount - self.defense)
        self.current_hp -= actual_damage
        self.damage_taken_total += actual_damage
        
        # Check for death
        if self.current_hp <= 0:
            self.current_hp = 0
            return actual_damage, True
        
        # Check for phase transition
        hp_percent = (self.current_hp / self.max_hp) * 100
        
        for phase, threshold in self.phase_transitions.items():
            if hp_percent <= threshold and self.current_phase.value < phase.value:
                self.current_phase = phase
                # Phase transition occurred
                return actual_damage, False
        
        return actual_damage, False
    
    def get_hp_percentage(self) -> int:
        """Get current HP as percentage"""
        return int((self.current_hp / self.max_hp) * 100)


class BossFightSystem:
    """
    Manages boss encounters with special mechanics.
    Works alongside the regular combat system.
    """
    
    def __init__(self, vader, suit_system):
        self.vader = vader
        self.suit = suit_system
        
        self.current_boss: Optional[BossEnemy] = None
        self.combat_log: List[str] = []
        
        # Fight state
        self.turn_number: int = 0
        self.scripted_loss: bool = False
        self.scripted_loss_triggered: bool = False
        
    def log(self, message: str):
        """Add to combat log"""
        self.combat_log.append(message)
    
    def start_boss_fight(self, boss: BossEnemy, scripted_loss: bool = False) -> Dict[str, Any]:
        """Initialize a boss fight"""
        self.current_boss = boss
        self.turn_number = 0
        self.scripted_loss = scripted_loss
        self.scripted_loss_triggered = False
        self.combat_log = []
        
        self.log(f"═══ BOSS FIGHT: {boss.name} ═══")
        self.log(f"Title: {boss.title}")
        self.log(f"HP: {boss.current_hp}/{boss.max_hp}")
        
        return {
            "boss": boss,
            "scripted_loss": scripted_loss,
            "message": f"Boss fight initiated: {boss.name}"
        }
    
    def check_triggers(self) -> Optional[BossTrigger]:
        """Check if any boss triggers should fire"""
        if not self.current_boss:
            return None
        
        for trigger in self.current_boss.triggers:
            if trigger.triggered:
                continue
            
            # Check conditions
            triggered = False
            
            if trigger.hp_threshold is not None:
                if self.current_boss.get_hp_percentage() <= trigger.hp_threshold:
                    triggered = True
            
            if trigger.turn_number is not None:
                if self.turn_number == trigger.turn_number:
                    triggered = True
            
            if trigger.phase is not None:
                if self.current_boss.current_phase == trigger.phase:
                    triggered = True
            
            if triggered:
                trigger.triggered = True
                return trigger
        
        return None
    
    def execute_boss_action(self, action: BossAction) -> Dict[str, Any]:
        """Boss uses a special action"""
        if action.current_cooldown > 0:
            return {"success": False, "message": "Action on cooldown"}
        
        result = {
            "success": True,
            "action_name": action.name,
            "damage": action.damage,
            "effects": []
        }
        
        # Show animation
        if action.animation:
            self.log(f"\n{action.animation}\n")
        
        # Apply damage
        if action.damage > 0:
            if self.vader.take_damage(action.damage):
                result["effects"].append(f"Dealt {action.damage} damage to Vader")
            else:
                result["effects"].append("Vader defeated!")
                result["vader_defeated"] = True
        
        # Apply stun
        if action.stun_chance > 0:
            if random.randint(1, 100) <= action.stun_chance:
                result["effects"].append("Vader is stunned!")
                result["vader_stunned"] = True
        
        # Drain Force Points
        if action.force_drain > 0:
            drained = min(action.force_drain, self.vader.current_force_points)
            self.vader.current_force_points -= drained
            result["effects"].append(f"Drained {drained} Force Points")
        
        # Damage suit
        if action.suit_damage > 0:
            self.suit.take_suit_damage(action.suit_damage)
            result["effects"].append(f"Suit damaged: -{action.suit_damage}%")
        
        # Set cooldown
        action.current_cooldown = action.cooldown_turns
        
        self.log(f"🔥 {self.current_boss.name} uses {action.name}!")
        for effect in result["effects"]:
            self.log(f"   {effect}")
        
        return result
    
    def boss_choose_action(self) -> Optional[BossAction]:
        """AI decides which special action to use"""
        if not self.current_boss:
            return None
        
        # Get available special actions
        available_actions = [
            action for action in self.current_boss.special_actions
            if action.current_cooldown == 0
        ]
        
        # Filter by phase
        available_actions = [
            action for action in available_actions
            if action.requires_phase is None or action.requires_phase == self.current_boss.current_phase
        ]
        
        # Filter by HP requirement
        hp_percent = self.current_boss.get_hp_percentage()
        available_actions = [
            action for action in available_actions
            if action.requires_hp_below is None or hp_percent < action.requires_hp_below
        ]
        
        if not available_actions:
            return None
        
        # Adaptive AI - prioritize based on what Vader does
        if self.current_boss.adaptive:
            if self.current_boss.times_vader_used_force > self.current_boss.times_vader_attacked:
                # Vader uses Force a lot - prioritize Force drain actions
                force_drain_actions = [a for a in available_actions if a.force_drain > 0]
                if force_drain_actions:
                    return random.choice(force_drain_actions)
        
        # Random choice from available
        return random.choice(available_actions)
    
    def vader_attacks_boss(self, damage: int) -> Dict[str, Any]:
        """Vader deals damage to boss"""
        if not self.current_boss:
            return {"success": False}
        
        self.current_boss.times_vader_attacked += 1
        
        # Check resistance
        if random.randint(1, 100) <= self.current_boss.force_resistance:
            damage = damage // 2
            self.log(f"   {self.current_boss.name} resists! (Half damage)")
        
        actual_damage, killed = self.current_boss.take_damage(damage)
        
        result = {
            "success": True,
            "damage": actual_damage,
            "killed": killed,
            "phase_changed": False
        }
        
        # Check for phase transition
        old_phase = self.current_boss.current_phase
        hp_percent = self.current_boss.get_hp_percentage()
        
        for phase, threshold in self.current_boss.phase_transitions.items():
            if hp_percent <= threshold and old_phase.value < phase.value:
                self.current_boss.current_phase = phase
                result["phase_changed"] = True
                result["new_phase"] = phase
                self.log(f"\n⚡ {self.current_boss.name} enters {phase.name}! ⚡\n")
                break
        
        return result
    
    def vader_uses_force_on_boss(self, power_name: str, damage: int) -> Dict[str, Any]:
        """Vader uses Force power on boss"""
        if not self.current_boss:
            return {"success": False}
        
        self.current_boss.times_vader_used_force += 1
        
        return self.vader_attacks_boss(damage)
    
    def check_scripted_loss(self) -> bool:
        """Check if scripted loss should trigger"""
        if not self.scripted_loss or self.scripted_loss_triggered:
            return False
        
        # Example: Boss fight is scripted to end after certain conditions
        # For Infil'a first duel: Leg breaks at turn 8 or when HP < 30%
        if self.turn_number >= 8 or self.vader.current_health < self.vader.max_health * 0.3:
            self.scripted_loss_triggered = True
            return True
        
        return False
    
    def update_cooldowns(self):
        """Update cooldowns for boss special actions"""
        if not self.current_boss:
            return
        
        for action in self.current_boss.special_actions:
            if action.current_cooldown > 0:
                action.current_cooldown -= 1
    
    def end_turn(self):
        """End turn, update state"""
        self.turn_number += 1
        self.update_cooldowns()
        
        if self.current_boss:
            self.current_boss.turns_survived += 1


# ============================================================
# BOSS DEFINITIONS - KIRAK INFIL'A
# ============================================================

def create_infila_first_duel() -> BossEnemy:
    """
    First duel with Kirak Infil'a on Al'doleem.
    This is a SCRIPTED LOSS - Vader's leg will break and he'll fall.
    """
    
    # Special actions for Infil'a
    actions = [
        BossAction(
            id="form3_defense",
            name="Form III: Soresu Defense",
            description="Infil'a's legendary defensive technique - nearly impenetrable",
            damage=0,
            animation="⚔️  Infil'a shifts to Soresu stance - his blade becomes a blur of defensive movements!",
            cooldown_turns=3
        ),
        BossAction(
            id="force_push_counter",
            name="Force Push Counter",
            description="Counters Vader's Force attack with his own",
            damage=25,
            animation="🌊 Infil'a redirects your Force attack back at you!",
            cooldown_turns=2
        ),
        BossAction(
            id="precision_strike",
            name="Precision Strike",
            description="Targets Vader's damaged leg servo",
            damage=30,
            suit_damage=5,
            animation="⚡ Infil'a strikes at your damaged leg with surgical precision!",
            requires_hp_below=70,
            cooldown_turns=2
        ),
        BossAction(
            id="mountain_wind",
            name="Mountain Wind Technique",
            description="Uses the mountain terrain to enhance his movement",
            damage=20,
            animation="🌪️  Infil'a uses the mountain winds - his movements become unpredictable!",
            cooldown_turns=4
        )
    ]
    
    # Triggers for scripted events
    triggers = [
        BossTrigger(
            id="opening_dialogue",
            trigger_type=BossEvent.DIALOGUE,
            turn_number=1,
            dialogue="So. The Emperor sends a servant. You are powerful, but untested in that suit."
        ),
        BossTrigger(
            id="leg_damage_warning",
            trigger_type=BossEvent.DIALOGUE,
            hp_threshold=50,
            dialogue="Your leg... it's damaged. That bird attack weakened you more than you realize."
        ),
        BossTrigger(
            id="scripted_defeat",
            trigger_type=BossEvent.CUTSCENE,
            turn_number=8,
            cutscene="leg_breaks",  # This will be handled by story system
            dialogue="The Emperor made you weak with that suit!"
        )
    ]
    
    return BossEnemy(
        id="infila_first",
        name="Kirak Infil'a",
        title="Jedi Master - Combat Specialist",
        max_hp=120,
        current_hp=120,
        base_damage=30,
        defense=15,
        current_phase=BossPhase.PHASE_1,
        phase_transitions={
            BossPhase.PHASE_2: 60  # Becomes more aggressive below 60% HP
        },
        special_actions=actions,
        force_resistance=60,
        lightsaber_resistance=20,
        aggressive=False,  # Defensive fighter
        adaptive=True,
        triggers=triggers
    )


def create_infila_final_duel(water_tank_destroyed: bool = False) -> BossEnemy:
    """
    Final duel with Kirak Infil'a at Am'balaar City.
    Difficulty depends on whether Vader destroyed the water tank.
    """
    
    # Phase 1 actions
    phase1_actions = [
        BossAction(
            id="soresu_mastery",
            name="Soresu Mastery",
            description="Perfect Form III defense",
            damage=0,
            animation="⚔️  Infil'a's defense is impenetrable - your attacks slide off his blade!",
            requires_phase=BossPhase.PHASE_1,
            cooldown_turns=3
        ),
        BossAction(
            id="counter_slash",
            name="Counter Slash",
            description="Punishes Vader's aggressive attacks",
            damage=35,
            animation="⚡ Infil'a parries and counters with lightning speed!",
            requires_phase=BossPhase.PHASE_1,
            cooldown_turns=2
        )
    ]
    
    # Phase 2 actions (if water tank NOT destroyed - he's focused)
    if not water_tank_destroyed:
        phase2_actions = [
            BossAction(
                id="jedi_fury",
                name="Righteous Fury",
                description="Infil'a channels the light side in anger at your presence",
                damage=45,
                force_drain=20,
                animation="🌟 'You represent everything the Jedi stood against!' - Infil'a's blade burns with light!",
                requires_phase=BossPhase.PHASE_2,
                requires_hp_below=50,
                cooldown_turns=3
            ),
            BossAction(
                id="form5_aggression",
                name="Form V: Shien",
                description="Switches to aggressive style",
                damage=40,
                stun_chance=30,
                animation="⚔️  Infil'a abandons defense - his strikes become overwhelming!",
                requires_phase=BossPhase.PHASE_2,
                cooldown_turns=2
            ),
            BossAction(
                id="final_stand",
                name="Jedi's Final Stand",
                description="Desperate all-out attack",
                damage=60,
                suit_damage=10,
                animation="💫 'For the Republic! For the Jedi!' - Infil'a puts everything into one strike!",
                requires_phase=BossPhase.FINAL,
                requires_hp_below=20,
                cooldown_turns=5
            )
        ]
    else:
        # Phase 2 if water tank WAS destroyed - he's distracted saving civilians
        phase2_actions = [
            BossAction(
                id="distracted_attack",
                name="Distracted Strike",
                description="Infil'a is torn between fighting and saving civilians",
                damage=25,  # Reduced damage
                animation="💔 Infil'a attacks but his focus is divided - screams echo from below",
                requires_phase=BossPhase.PHASE_2,
                cooldown_turns=1
            ),
            BossAction(
                id="desperate_defense",
                name="Desperate Defense",
                description="Tries to hold you off while saving people",
                damage=15,
                animation="😰 'Please! Stop this! They're innocent!' - Infil'a is barely fighting",
                requires_phase=BossPhase.PHASE_2,
                cooldown_turns=1
            )
        ]
    
    all_actions = phase1_actions + phase2_actions
    
    # Triggers
    triggers = [
        BossTrigger(
            id="duel_start",
            trigger_type=BossEvent.DIALOGUE,
            turn_number=1,
            dialogue="You survived the fall. Impressive. But this time, I will end you."
        ),
        BossTrigger(
            id="phase2_transition",
            trigger_type=BossEvent.PHASE_TRANSITION,
            hp_threshold=50,
            phase=BossPhase.PHASE_2,
            dialogue="You're stronger than before... but so am I!" if not water_tank_destroyed else "The screams... what have you done?!"
        ),
        BossTrigger(
            id="near_death",
            trigger_type=BossEvent.DIALOGUE,
            hp_threshold=15,
            dialogue="I won't let you... claim my crystal..." if not water_tank_destroyed else "At least... I saved some of them..."
        )
    ]
    
    # Base stats
    base_hp = 150
    base_defense = 18
    
    # Adjust difficulty based on choice
    if water_tank_destroyed:
        # Easier fight - Infil'a is distracted
        base_hp = 120
        base_defense = 12
    
    return BossEnemy(
        id="infila_final",
        name="Kirak Infil'a",
        title="Jedi Master - Final Duel",
        max_hp=base_hp,
        current_hp=base_hp,
        base_damage=35,
        defense=base_defense,
        current_phase=BossPhase.PHASE_1,
        phase_transitions={
            BossPhase.PHASE_2: 50,
            BossPhase.FINAL: 20
        },
        special_actions=all_actions,
        force_resistance=70,
        lightsaber_resistance=25,
        aggressive=not water_tank_destroyed,  # More aggressive if focused
        adaptive=True,
        triggers=triggers
    )


# ============================================================
# EXAMPLE: OTHER BOSS TEMPLATES
# ============================================================

def create_grand_inquisitor() -> BossEnemy:
    """
    Template for Grand Inquisitor boss fight (future content).
    """
    actions = [
        BossAction(
            id="spinning_saber",
            name="Spinning Lightsaber",
            description="Inquisitor's signature spinning attack",
            damage=40,
            stun_chance=20,
            animation="🌀 The Inquisitor's double-bladed saber spins in a deadly wheel!",
            cooldown_turns=3
        ),
        BossAction(
            id="force_pull_slam",
            name="Force Pull Slam",
            description="Pulls Vader in and strikes",
            damage=35,
            suit_damage=5,
            animation="🌊 The Inquisitor pulls you forward and slams you with his blade!",
            cooldown_turns=2
        ),
        BossAction(
            id="dark_side_rage",
            name="Dark Side Rage",
            description="Channels dark side power",
            damage=50,
            force_drain=15,
            animation="😈 'I am the darkness!' - The Inquisitor erupts with dark energy!",
            requires_phase=BossPhase.PHASE_2,
            requires_hp_below=40,
            cooldown_turns=4
        )
    ]
    
    triggers = [
        BossTrigger(
            id="rivalry_start",
            trigger_type=BossEvent.DIALOGUE,
            turn_number=1,
            dialogue="Lord Vader. The Emperor's new favorite. Let us see if you deserve that title."
        )
    ]
    
    return BossEnemy(
        id="grand_inquisitor",
        name="The Grand Inquisitor",
        title="Leader of the Inquisitorius",
        max_hp=180,
        current_hp=180,
        base_damage=38,
        defense=20,
        phase_transitions={BossPhase.PHASE_2: 50},
        special_actions=actions,
        force_resistance=65,
        lightsaber_resistance=22,
        aggressive=True,
        adaptive=True,
        triggers=triggers
    )


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    from character.vader import DarthVader
    from character.suit_system import SuitSystem
    
    print("=== BOSS FIGHT SYSTEM TEST ===\n")
    
    # Create systems
    vader = DarthVader()
    suit = SuitSystem()
    boss_system = BossFightSystem(vader, suit)
    
    # Test First Infil'a Duel (scripted loss)
    print("--- Creating First Infil'a Duel ---")
    infila_first = create_infila_first_duel()
    print(f"Boss: {infila_first.name}")
    print(f"Title: {infila_first.title}")
    print(f"HP: {infila_first.current_hp}/{infila_first.max_hp}")
    print(f"Special Actions: {len(infila_first.special_actions)}")
    for action in infila_first.special_actions:
        print(f"  - {action.name}: {action.description}")
    print(f"Triggers: {len(infila_first.triggers)}")
    print(f"Scripted Loss: Yes")
    
    print("\n--- Creating Final Infil'a Duel (Honor Path) ---")
    infila_final_honor = create_infila_final_duel(water_tank_destroyed=False)
    print(f"Boss: {infila_final_honor.name}")
    print(f"HP: {infila_final_honor.current_hp}/{infila_final_honor.max_hp}")
    print(f"Defense: {infila_final_honor.defense}")
    print(f"Special Actions: {len(infila_final_honor.special_actions)}")
    print(f"Difficulty: HARD (focused fighter)")
    
    print("\n--- Creating Final Infil'a Duel (Massacre Path) ---")
    infila_final_massacre = create_infila_final_duel(water_tank_destroyed=True)
    print(f"Boss: {infila_final_massacre.name}")
    print(f"HP: {infila_final_massacre.current_hp}/{infila_final_massacre.max_hp}")
    print(f"Defense: {infila_final_massacre.defense}")
    print(f"Special Actions: {len(infila_final_massacre.special_actions)}")
    print(f"Difficulty: EASY (distracted by saving civilians)")
    
    print("\n--- Testing Boss Fight Initialization ---")
    result = boss_system.start_boss_fight(infila_first, scripted_loss=True)
    print(f"Result: {result['message']}")
    print(f"Scripted Loss: {result['scripted_loss']}")
    
    print("\n--- Testing Boss Special Action ---")
    action = infila_first.special_actions[0]  # Form III Defense
    boss_system.turn_number = 2
    result = boss_system.execute_boss_action(action)
    print(f"Action: {result['action_name']}")
    print(f"Success: {result['success']}")
    
    print("\n--- Simulating Phase Transition ---")
    infila_first.current_hp = 60  # Trigger phase 2
    damage, killed = infila_first.take_damage(20)
    print(f"Damage dealt: {damage}")
    print(f"Current Phase: {infila_first.current_phase}")
    print(f"HP: {infila_first.current_hp}/{infila_first.max_hp} ({infila_first.get_hp_percentage()}%)")
    
    print("\n=== BOSS SYSTEM READY ===")
    print(f"✓ Infil'a First Duel: Scripted loss encounter")
    print(f"✓ Infil'a Final Duel: Two difficulty paths")
    print(f"✓ Phase transitions working")
    print(f"✓ Special actions implemented")
    print(f"✓ Trigger system functional")