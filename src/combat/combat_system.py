"""
Combat System for Darth Vader
Turn-based tactical combat with Force powers, lightsaber combat, and enemy AI.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class CombatAction(Enum):
    """Available combat actions"""
    ATTACK = "attack"
    FORCE_POWER = "force_power"
    ITEM = "item"
    DEFEND = "defend"
    MOVE = "move"
    MEDITATE = "meditate"
    CALL_REINFORCEMENTS = "reinforcements"
    RETREAT = "retreat"


class EnemyType(Enum):
    """Types of enemies with different AI behaviors"""
    STORMTROOPER = "stormtrooper"
    REBEL_SOLDIER = "rebel_soldier"
    REBEL_VETERAN = "rebel_veteran"
    OFFICER = "officer"
    BATTLE_DROID = "battle_droid"
    INQUISITOR = "inquisitor"
    JEDI_SURVIVOR = "jedi_survivor"
    DARK_JEDI = "dark_jedi"


class EnemyAIBehavior(Enum):
    """AI behavior patterns"""
    AGGRESSIVE = "aggressive"  # Rush in, attack constantly
    DEFENSIVE = "defensive"  # Stay back, use cover
    TACTICAL = "tactical"  # Smart positioning, coordinated
    PANICKED = "panicked"  # Low morale, may flee
    BERSERK = "berserk"  # Reckless, high damage
    CALCULATED = "calculated"  # Droids - optimal moves only


@dataclass
class Enemy:
    """Represents an enemy combatant"""
    id: str
    name: str
    enemy_type: EnemyType
    
    # Stats
    max_hp: int
    current_hp: int
    attack_damage: int
    defense: int
    
    # AI behavior
    ai_behavior: EnemyAIBehavior
    morale: int = 100  # 0-100, affects behavior
    
    # Special abilities
    force_sensitive: bool = False
    force_powers: List[str] = field(default_factory=list)
    force_points: int = 0
    
    # Status
    is_stunned: bool = False
    is_feared: bool = False
    is_defending: bool = False
    is_alive: bool = True
    
    # Resistances
    force_resistance: int = 0  # 0-100, % chance to resist Force powers
    lightsaber_resistance: int = 0  # Armor against lightsaber
    
    # Loot
    credits_drop: int = 0
    experience_value: int = 10
    
    def take_damage(self, amount: int) -> Tuple[int, bool]:
        """
        Take damage. Returns (actual_damage_taken, is_killed)
        """
        # Apply defense
        actual_damage = max(1, amount - self.defense)
        
        self.current_hp -= actual_damage
        
        # Morale check on damage
        if self.current_hp < self.max_hp * 0.3:
            self.morale = max(0, self.morale - 20)
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            return actual_damage, True
        
        return actual_damage, False
    
    def is_helpless(self) -> bool:
        """Check if enemy is in helpless state (can be executed)"""
        return self.current_hp <= self.max_hp * 0.25 and self.current_hp > 0


@dataclass
class CombatState:
    """Tracks the state of an ongoing combat"""
    turn_number: int = 1
    vader_turn: bool = True
    combat_active: bool = True
    
    # Enemies
    enemies: List[Enemy] = field(default_factory=list)
    enemies_killed: int = 0
    
    # Vader status during combat
    vader_defended_this_turn: bool = False
    vader_can_retreat: bool = True
    
    # Combat results
    victory_type: Optional[str] = None
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    
    # Execution opportunities
    helpless_enemies: List[str] = field(default_factory=list)  # Enemy IDs


class CombatSystem:
    """
    Main combat engine managing turn-based tactical combat.
    """
    
    def __init__(self, vader, suit_system, force_power_system):
        self.vader = vader
        self.suit = suit_system
        self.force_powers = force_power_system
        
        # Current combat state
        self.combat_state: Optional[CombatState] = None
        
        # Combat log for display
        self.combat_log: List[str] = []
        
        # Reinforcement availability
        self.reinforcement_cooldown = 0
        self.reinforcements_available = {
            "stormtrooper_squad": True,
            "501st_unit": True,
            "inquisitor": True
        }
    
    def start_combat(self, enemies: List[Enemy]) -> CombatState:
        """Initialize a new combat encounter"""
        self.combat_state = CombatState(enemies=enemies)
        self.combat_log = []
        
        # Reset Force power combat tracking
        self.force_powers.reset_combat_tracking()
        
        self.log(f"═══ COMBAT START ═══")
        self.log(f"Enemies: {len(enemies)}")
        
        return self.combat_state
    
    def log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
    
    def get_available_actions(self) -> List[CombatAction]:
        """Get list of actions Vader can take this turn"""
        actions = [
            CombatAction.ATTACK,
            CombatAction.FORCE_POWER,
            CombatAction.DEFEND,
            CombatAction.MOVE
        ]
        
        # Meditation available if FP < 50%
        if self.vader.current_force_points < self.vader.max_force_points * 0.5:
            actions.append(CombatAction.MEDITATE)
        
        # Retreat available if can retreat
        if self.combat_state.vader_can_retreat:
            actions.append(CombatAction.RETREAT)
        
        return actions
    
    def vader_attack(self, target_id: str) -> Dict[str, Any]:
        """
        Vader performs a lightsaber attack.
        Returns dict with results.
        """
        target = self._get_enemy_by_id(target_id)
        if not target or not target.is_alive:
            return {"success": False, "message": "Invalid target"}
        
        # Calculate damage
        base_damage = 40 + (self.vader.stats.strength * 2)
        
        # Apply pain modifier
        pain_mods = self.suit.get_pain_modifier()
        damage_penalty = pain_mods.get("attack_penalty", 0)
        
        # Apply lightsaber resistance
        final_damage = base_damage - damage_penalty - target.lightsaber_resistance
        final_damage = max(5, final_damage)  # Minimum damage
        
        # Apply damage to target
        actual_damage, killed = target.take_damage(final_damage)
        
        self.combat_state.total_damage_dealt += actual_damage
        
        result = {
            "success": True,
            "target": target.name,
            "damage": actual_damage,
            "killed": killed
        }
        
        if killed:
            self._handle_enemy_death(target)
            self.log(f"⚔️  Vader strikes down {target.name}! (+{actual_damage} damage)")
        else:
            self.log(f"⚔️  Vader attacks {target.name} for {actual_damage} damage. ({target.current_hp}/{target.max_hp} HP)")
            
            # Check if enemy is now helpless
            if target.is_helpless() and target_id not in self.combat_state.helpless_enemies:
                self.combat_state.helpless_enemies.append(target_id)
                self.log(f"   {target.name} is helpless! Can be executed.")
        
        return result
    
    def vader_use_force_power(self, power_id: str, target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Vader uses a Force power.
        Returns dict with results.
        """
        # Check if can use power
        can_use, reason = self.force_powers.can_use_power(power_id, self.vader.current_force_points)
        if not can_use:
            return {"success": False, "message": reason}
        
        power = self.force_powers.learned_powers[power_id]
        
        # Spend Force points
        self.vader.spend_force_points(power.force_point_cost)
        
        # Use the power
        success, message, effects = self.force_powers.use_power(
            power_id,
            self.vader.psychological_state.darkness,
            self.vader.psychological_state.rage,
            self.suit
        )
        
        if not success:
            return {"success": False, "message": message}
        
        self.log(f"🌟 {message}")
        
        # Apply effects based on power
        result = {
            "success": True,
            "power_name": power.name,
            "damage": effects.get("damage", 0),
            "area_effect": effects.get("area_effect", False),
            "targets_hit": [],
            "kills": []
        }
        
        # Handle damage-dealing powers
        if effects["damage"] > 0:
            if power.area_effect:
                # Hit all alive enemies
                for enemy in self.combat_state.enemies:
                    if enemy.is_alive:
                        result["targets_hit"].append(enemy.name)
                        damage, killed = self._apply_force_damage(enemy, effects["damage"])
                        if killed:
                            result["kills"].append(enemy.name)
            elif target_id:
                # Single target
                target = self._get_enemy_by_id(target_id)
                if target and target.is_alive:
                    result["targets_hit"].append(target.name)
                    damage, killed = self._apply_force_damage(target, effects["damage"])
                    if killed:
                        result["kills"].append(target.name)
        
        # Check for legendary exhaustion
        if self.force_powers.check_legendary_exhaustion(self.vader):
            self.log(f"⚠️  Force exhaustion! Regeneration reduced for 3 turns.")
        
        return result
    
    def vader_defend(self) -> Dict[str, Any]:
        """Vader takes defensive stance"""
        self.combat_state.vader_defended_this_turn = True
        self.log(f"🛡️  Vader assumes defensive stance. (+50% defense this turn)")
        
        return {"success": True, "message": "Defending"}
    
    def vader_meditate(self) -> Dict[str, Any]:
        """Vader meditates to restore Force Points (risky - vulnerable)"""
        fp_restored = 30
        self.vader.restore_force_points(fp_restored)
        
        self.log(f"🧘 Vader meditates. (+{fp_restored} FP, vulnerable to attacks)")
        
        return {
            "success": True,
            "fp_restored": fp_restored,
            "vulnerable": True  # Enemies get bonus damage
        }
    
    def vader_retreat(self) -> Dict[str, Any]:
        """Attempt to retreat from combat"""
        # Base success chance
        success_chance = 60
        
        # Modified by suit integrity
        if self.suit.integrity < 50:
            success_chance += 20  # Easier to justify retreat when damaged
        
        # Roll for success
        roll = random.randint(1, 100)
        
        if roll <= success_chance:
            self.combat_state.combat_active = False
            self.combat_state.victory_type = "retreat"
            self.log(f"💨 Vader retreats from combat.")
            
            return {
                "success": True,
                "message": "Successfully retreated"
            }
        else:
            self.log(f"❌ Retreat failed! Enemies block escape.")
            return {
                "success": False,
                "message": "Retreat blocked",
                "penalty": True  # Enemies get free attack
            }
    
    def execute_enemy(self, target_id: str, method: str = "quick") -> Dict[str, Any]:
        """
        Execute a helpless enemy with chosen method.
        Methods: quick, choke, brutal, spare
        """
        target = self._get_enemy_by_id(target_id)
        if not target or not target.is_alive or not target.is_helpless():
            return {"success": False, "message": "Cannot execute this target"}
        
        result = {
            "success": True,
            "target": target.name,
            "method": method,
            "darkness_change": 0,
            "control_change": 0
        }
        
        if method == "quick":
            # Efficient kill
            self.log(f"⚔️  Vader quickly dispatches {target.name}.")
            target.current_hp = 0
            target.is_alive = False
            result["darkness_change"] = 0
            
        elif method == "choke":
            # Slow, terrifying death
            self.log(f"🫱 Vader slowly chokes the life from {target.name}.")
            target.current_hp = 0
            target.is_alive = False
            result["darkness_change"] = 5
            
            # Terrify other enemies
            for enemy in self.combat_state.enemies:
                if enemy.is_alive and enemy.id != target_id:
                    enemy.morale = max(0, enemy.morale - 30)
                    
        elif method == "brutal":
            # Excessive violence
            self.log(f"💀 Vader brutally dismembers {target.name}.")
            target.current_hp = 0
            target.is_alive = False
            result["darkness_change"] = 10
            result["control_change"] = -5
            
            # Terrify enemies even more
            for enemy in self.combat_state.enemies:
                if enemy.is_alive and enemy.id != target_id:
                    enemy.morale = max(0, enemy.morale - 50)
                    if enemy.morale < 20:
                        enemy.is_feared = True
                        
        elif method == "spare":
            # Show mercy
            self.log(f"🤝 Vader spares {target.name}.")
            target.is_alive = False  # Remove from combat but not killed
            result["darkness_change"] = -3
            result["control_change"] = 5
            result["killed"] = False
            result["intel_possible"] = True
        
        if result.get("killed", True):
            self._handle_enemy_death(target)
        
        # Remove from helpless list
        if target_id in self.combat_state.helpless_enemies:
            self.combat_state.helpless_enemies.remove(target_id)
        
        return result
    
    def _apply_force_damage(self, target: Enemy, damage: int) -> Tuple[int, bool]:
        """Apply Force power damage to target, considering resistance"""
        # Check Force resistance
        if target.force_resistance > 0:
            resist_roll = random.randint(1, 100)
            if resist_roll <= target.force_resistance:
                damage = damage // 2
                self.log(f"   {target.name} resists! (Half damage)")
        
        actual_damage, killed = target.take_damage(damage)
        self.combat_state.total_damage_dealt += actual_damage
        
        if killed:
            self._handle_enemy_death(target)
        
        return actual_damage, killed
    
    def _handle_enemy_death(self, enemy: Enemy):
        """Handle enemy death - XP, FP bonus, loot"""
        self.combat_state.enemies_killed += 1
        
        # Force Point bonus
        fp_bonus = self.force_powers.on_enemy_killed(enemy.force_sensitive)
        self.vader.current_force_points = min(
            self.vader.max_force_points,
            self.vader.current_force_points + fp_bonus
        )
        
        if fp_bonus > 0:
            self.log(f"   (+{fp_bonus} FP from kill)")
        
        # Credits and XP
        self.suit.credits += enemy.credits_drop
        xp_message = self.vader.add_experience(enemy.experience_value)
        if xp_message:
            self.log(f"   ⭐ {xp_message}")
    
    def enemy_turn(self):
        """Execute enemy turns with AI"""
        self.log(f"\n--- ENEMY TURN {self.combat_state.turn_number} ---")
        
        alive_enemies = [e for e in self.combat_state.enemies if e.is_alive]
        
        for enemy in alive_enemies:
            if enemy.is_stunned:
                self.log(f"{enemy.name} is stunned! (Skip turn)")
                enemy.is_stunned = False
                continue
            
            # AI decides action based on behavior and state
            action = self._enemy_ai_decision(enemy)
            self._execute_enemy_action(enemy, action)
    
    def _enemy_ai_decision(self, enemy: Enemy) -> str:
        """AI decides what action enemy should take"""
        # Panicked enemies may flee
        if enemy.morale < 20 and not enemy.force_sensitive:
            if random.randint(1, 100) <= 50:
                return "flee"
        
        # Feared enemies have reduced effectiveness
        if enemy.is_feared:
            if random.randint(1, 100) <= 30:
                return "cower"
        
        # Behavior-based decisions
        if enemy.ai_behavior == EnemyAIBehavior.AGGRESSIVE:
            return "attack"
        
        elif enemy.ai_behavior == EnemyAIBehavior.DEFENSIVE:
            if enemy.current_hp < enemy.max_hp * 0.4:
                return "defend"
            return "attack"
        
        elif enemy.ai_behavior == EnemyAIBehavior.TACTICAL:
            # Smart decisions
            if enemy.current_hp < enemy.max_hp * 0.3:
                return "defend"
            if enemy.force_sensitive and enemy.force_points >= 20:
                return "force_power"
            return "attack"
        
        elif enemy.ai_behavior == EnemyAIBehavior.CALCULATED:
            # Droids always optimal
            return "attack"
        
        else:
            return "attack"
    
    def _execute_enemy_action(self, enemy: Enemy, action: str):
        """Execute enemy action"""
        if action == "attack":
            damage = enemy.attack_damage
            
            # Vader defended this turn?
            if self.combat_state.vader_defended_this_turn:
                damage = damage // 2
                self.log(f"{enemy.name} attacks but Vader deflects! ({damage} damage)")
            else:
                self.log(f"{enemy.name} attacks Vader! ({damage} damage)")
            
            # Apply damage to Vader
            if self.vader.take_damage(damage):
                self.combat_state.total_damage_taken += damage
                
                # Random chance to damage suit
                if random.randint(1, 100) <= 15:  # 15% chance
                    suit_damage = random.randint(2, 5)
                    self.suit.take_suit_damage(suit_damage)
                    self.log(f"   ⚠️  Suit damaged! (-{suit_damage}%)")
            else:
                # Vader defeated
                self.combat_state.combat_active = False
                self.combat_state.victory_type = "defeat"
        
        elif action == "defend":
            enemy.is_defending = True
            self.log(f"{enemy.name} takes defensive position.")
        
        elif action == "flee":
            enemy.is_alive = False
            self.log(f"{enemy.name} flees in terror!")
        
        elif action == "cower":
            self.log(f"{enemy.name} cowers in fear!")
        
        elif action == "force_power":
            self.log(f"{enemy.name} uses Force power!")
            # Simple Force attack
            force_damage = random.randint(15, 25)
            self.vader.take_damage(force_damage)
            self.combat_state.total_damage_taken += force_damage
    
    def end_turn(self):
        """End current turn, regenerate resources, update state"""
        # Regenerate Vader's Force Points
        fp_regen = self.vader.regenerate_force_points(self.suit)
        if fp_regen > 0:
            self.log(f"🔵 Vader regenerates {fp_regen} Force Points ({self.vader.current_force_points}/{self.vader.max_force_points})")
        
        # Update Force power cooldowns
        self.force_powers.update_cooldowns()
        
        # Reset turn-specific flags
        self.combat_state.vader_defended_this_turn = False
        
        # Increment turn
        self.combat_state.turn_number += 1
        
        # Check victory conditions
        self._check_victory_conditions()
    
    def _check_victory_conditions(self):
        """Check if combat should end"""
        alive_enemies = [e for e in self.combat_state.enemies if e.is_alive]
        
        if len(alive_enemies) == 0:
            self.combat_state.combat_active = False
            self.combat_state.victory_type = "total_victory"
            self.log(f"\n🏆 VICTORY! All enemies defeated.")
        
        # Check if all remaining enemies fled or terrified
        non_fled = [e for e in alive_enemies if not e.is_feared or e.morale > 0]
        if len(alive_enemies) > 0 and len(non_fled) == 0:
            self.combat_state.combat_active = False
            self.combat_state.victory_type = "intimidation_victory"
            self.log(f"\n😱 INTIMIDATION VICTORY! Enemies flee in terror.")
    
    def _get_enemy_by_id(self, enemy_id: str) -> Optional[Enemy]:
        """Get enemy by ID"""
        for enemy in self.combat_state.enemies:
            if enemy.id == enemy_id:
                return enemy
        return None
    
    def get_combat_summary(self) -> Dict[str, Any]:
        """Get summary of completed combat"""
        return {
            "victory_type": self.combat_state.victory_type,
            "turns": self.combat_state.turn_number,
            "enemies_killed": self.combat_state.enemies_killed,
            "damage_dealt": self.combat_state.total_damage_dealt,
            "damage_taken": self.combat_state.total_damage_taken,
            "force_points_remaining": self.vader.current_force_points,
            "suit_integrity": self.suit.integrity,
            "vader_hp": self.vader.current_health
        }


def create_enemy(enemy_type: EnemyType, level: int = 1) -> Enemy:
    """Factory function to create enemies based on type"""
    
    if enemy_type == EnemyType.STORMTROOPER:
        return Enemy(
            id=f"stormtrooper_{random.randint(1000, 9999)}",
            name="Stormtrooper",
            enemy_type=enemy_type,
            max_hp=25,
            current_hp=25,
            attack_damage=12,
            defense=3,
            ai_behavior=EnemyAIBehavior.DEFENSIVE,
            credits_drop=50,
            experience_value=15
        )
    
    elif enemy_type == EnemyType.REBEL_VETERAN:
        return Enemy(
            id=f"rebel_vet_{random.randint(1000, 9999)}",
            name="Rebel Veteran",
            enemy_type=enemy_type,
            max_hp=40,
            current_hp=40,
            attack_damage=18,
            defense=5,
            ai_behavior=EnemyAIBehavior.TACTICAL,
            credits_drop=100,
            experience_value=25
        )
    
    elif enemy_type == EnemyType.JEDI_SURVIVOR:
        return Enemy(
            id=f"jedi_{random.randint(1000, 9999)}",
            name="Jedi Survivor",
            enemy_type=enemy_type,
            max_hp=80,
            current_hp=80,
            attack_damage=30,
            defense=10,
            ai_behavior=EnemyAIBehavior.TACTICAL,
            force_sensitive=True,
            force_powers=["force_push", "force_barrier"],
            force_points=50,
            force_resistance=40,
            lightsaber_resistance=15,
            credits_drop=0,
            experience_value=100
        )
    
    elif enemy_type == EnemyType.BATTLE_DROID:
        return Enemy(
            id=f"droid_{random.randint(1000, 9999)}",
            name="Battle Droid",
            enemy_type=enemy_type,
            max_hp=30,
            current_hp=30,
            attack_damage=15,
            defense=2,
            ai_behavior=EnemyAIBehavior.CALCULATED,
            force_resistance=100,  # Immune to mental Force powers
            credits_drop=25,
            experience_value=20
        )
    
    else:
        # Default enemy
        return Enemy(
            id=f"enemy_{random.randint(1000, 9999)}",
            name="Enemy",
            enemy_type=enemy_type,
            max_hp=30,
            current_hp=30,
            attack_damage=15,
            defense=3,
            ai_behavior=EnemyAIBehavior.AGGRESSIVE,
            credits_drop=50,
            experience_value=20
        )


# Example usage and testing
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    from character.vader import DarthVader
    from character.suit_system import SuitSystem
    from character.force_powers import ForcePowerSystem
    
    # Create Vader and systems
    vader = DarthVader()
    suit = SuitSystem()
    force_powers = ForcePowerSystem()
    
    # Create combat system
    combat = CombatSystem(vader, suit, force_powers)
    
    print("=== COMBAT SYSTEM TEST ===\n")
    
    # Create some enemies
    enemies = [
        create_enemy(EnemyType.STORMTROOPER),
        create_enemy(EnemyType.STORMTROOPER),
        create_enemy(EnemyType.REBEL_VETERAN)
    ]
    
    # Start combat
    combat.start_combat(enemies)
    
    print(f"Vader HP: {vader.current_health}/{vader.max_health}")
    print(f"Vader FP: {vader.current_force_points}/{vader.max_force_points}")
    print(f"\nEnemies:")
    for enemy in enemies:
        print(f"  - {enemy.name} ({enemy.current_hp} HP)")
    
    print(f"\n--- TURN 1: Vader's Action ---")
    # Vader uses Force Push
    result = combat.vader_use_force_power("force_push")
    print(f"Result: {result}")
    
    print(f"\n--- Enemy Actions ---")
    combat.enemy_turn()
    
    print(f"\n--- End Turn ---")
    combat.end_turn()
    
    print(f"\nVader HP: {vader.current_health}/{vader.max_health}")
    print(f"Vader FP: {vader.current_force_points}/{vader.max_force_points}")
    
    print(f"\n--- COMBAT LOG ---")
    for log_entry in combat.combat_log:
        print(log_entry)