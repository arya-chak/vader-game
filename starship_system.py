"""
Starship System for Darth Vader RPG
Manages Vader's fleet: 2 personal starfighters + 1 command ship.
Each ship has unique upgrades, weapons, and capabilities.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class StarshipType(Enum):
    """Types of ships available to Vader"""
    ETA2_INTERCEPTOR = "eta2_interceptor"  # Personal fighter #1
    TIE_ADVANCED = "tie_advanced"  # Personal fighter #2 (unlock later)
    EXECUTOR_DESTROYER = "executor_destroyer"  # Command ship (unlock later)


class StarshipRole(Enum):
    """Role of the starship"""
    FIGHTER = "fighter"  # Space combat, dogfighting
    COMMAND = "command"  # Strategy, fleet control


class StarshipComponent(Enum):
    """Different components of starships that can be upgraded"""
    HULL = "hull"
    HYPERDRIVE = "hyperdrive"
    WEAPONS = "weapons"
    SHIELDS = "shields"
    ENGINES = "engines"
    TARGETING = "targeting"
    SENSORS = "sensors"


@dataclass
class StarshipUpgrade:
    """Represents a starship component upgrade"""
    id: str
    name: str
    description: str
    component: StarshipComponent
    tier: int  # 1-5
    
    # Costs
    credits_cost: int
    materials_required: Dict[str, int] = field(default_factory=dict)
    
    # Effects
    hull_bonus: int = 0
    weapon_damage_bonus: int = 0
    shield_strength_bonus: int = 0
    hyperdrive_speed_bonus: int = 0
    sensor_range_bonus: int = 0
    
    # Requirements
    requires_upgrades: List[str] = field(default_factory=list)
    min_level: int = 1
    
    installed: bool = False


@dataclass
class Starship:
    """Represents a single starship"""
    ship_type: StarshipType
    name: str
    description: str
    role: StarshipRole
    
    # Ownership
    owned: bool = False
    unlock_condition: str = ""  # How to acquire (e.g., "Defeat pirates", "Level 10")
    
    # Component integrity (0-100)
    hull_integrity: int = 100
    hyperdrive_integrity: int = 100
    weapons_integrity: int = 100
    shields_integrity: int = 100
    engines_integrity: int = 100
    targeting_integrity: int = 100
    sensors_integrity: int = 100
    
    # Ship status
    is_flight_ready: bool = False  # Until owned
    needs_maintenance: bool = False
    
    # Systems
    hyperdrive_active: bool = True
    weapons_online: bool = True
    shields_available: bool = False
    cloaking_available: bool = False
    
    # Weapons (different for each ship)
    primary_weapon: str = ""
    primary_weapon_damage: int = 0
    primary_weapon_ammo: int = 0
    
    secondary_weapon: str = ""
    secondary_weapon_damage: int = 0
    secondary_weapon_ammo: int = 0
    
    # Upgrades installed
    installed_upgrades: Dict[str, StarshipUpgrade] = field(default_factory=dict)
    
    # Resources
    credits_stored: int = 0
    fuel: int = 100
    
    # Stats
    missions_flown: int = 0
    enemies_destroyed: int = 0
    escape_count: int = 0
    docking_location: str = "Unknown"
    
    def get_overall_integrity(self) -> int:
        """Calculate overall hull integrity"""
        components = [
            self.hull_integrity,
            self.hyperdrive_integrity,
            self.weapons_integrity,
            self.shields_integrity,
            self.engines_integrity,
            self.targeting_integrity,
            self.sensors_integrity,
        ]
        return sum(components) // len(components)
    
    def take_damage(self, amount: int, component: Optional[str] = None):
        """Damage the ship"""
        if component == "hull":
            self.hull_integrity = max(0, self.hull_integrity - amount)
        elif component == "hyperdrive":
            self.hyperdrive_integrity = max(0, self.hyperdrive_integrity - amount)
            if self.hyperdrive_integrity < 30:
                self.hyperdrive_active = False
        elif component == "weapons":
            self.weapons_integrity = max(0, self.weapons_integrity - amount)
            if self.weapons_integrity < 20:
                self.weapons_online = False
        elif component == "shields":
            self.shields_integrity = max(0, self.shields_integrity - amount)
        elif component == "engines":
            self.engines_integrity = max(0, self.engines_integrity - amount)
        elif component == "targeting":
            self.targeting_integrity = max(0, self.targeting_integrity - amount)
        elif component == "sensors":
            self.sensors_integrity = max(0, self.sensors_integrity - amount)
        else:
            # Distribute damage across all components
            per_component = amount // 7
            self.hull_integrity = max(0, self.hull_integrity - per_component)
            self.hyperdrive_integrity = max(0, self.hyperdrive_integrity - per_component)
            self.weapons_integrity = max(0, self.weapons_integrity - per_component)
            self.shields_integrity = max(0, self.shields_integrity - per_component)
            self.engines_integrity = max(0, self.engines_integrity - per_component)
            self.targeting_integrity = max(0, self.targeting_integrity - per_component)
            self.sensors_integrity = max(0, self.sensors_integrity - per_component)
        
        if self.get_overall_integrity() < 30:
            self.needs_maintenance = True
    
    def repair_all(self):
        """Full repair of all systems"""
        self.hull_integrity = 100
        self.hyperdrive_integrity = 100
        self.weapons_integrity = 100
        self.shields_integrity = 100
        self.engines_integrity = 100
        self.targeting_integrity = 100
        self.sensors_integrity = 100
        self.hyperdrive_active = True
        self.weapons_online = True
        self.needs_maintenance = False
    
    def get_status(self) -> Dict:
        """Get ship status summary"""
        return {
            "name": self.name,
            "type": self.ship_type.value,
            "owned": self.owned,
            "overall_integrity": self.get_overall_integrity(),
            "is_flight_ready": self.is_flight_ready and self.owned,
            "hyperdrive_active": self.hyperdrive_active,
            "weapons_online": self.weapons_online,
            "shields_available": self.shields_available,
            "fuel": self.fuel,
            "missions_flown": self.missions_flown,
            "enemies_destroyed": self.enemies_destroyed,
        }


class StarshipFleet:
    """
    Manages Vader's entire fleet of ships.
    Tracks ownership, assignments, and upgrades across all vessels.
    """
    
    def __init__(self):
        # Initialize all three ships
        self.eta2_interceptor = Starship(
            ship_type=StarshipType.ETA2_INTERCEPTOR,
            name="Black Eta-2 Actis-class Interceptor",
            description="Your personal starfighter. Once Anakin's own fighter, now dark as Empire itself.",
            role=StarshipRole.FIGHTER,
            owned=False,
            unlock_condition="Defeat the pirate settlement",
            primary_weapon="Laser Cannons",
            primary_weapon_damage=40,
            primary_weapon_ammo=1000,
            secondary_weapon="Missile Launcher",
            secondary_weapon_damage=100,
            secondary_weapon_ammo=20,
        )
        
        self.tie_advanced = Starship(
            ship_type=StarshipType.TIE_ADVANCED,
            name="TIE Advanced x1",
            description="Empire's most advanced fighter. Superior speed and weapons.",
            role=StarshipRole.FIGHTER,
            owned=False,
            unlock_condition="Unlock later (Level 10+)",
            primary_weapon="Dual Laser Cannons",
            primary_weapon_damage=50,
            primary_weapon_ammo=1200,
            secondary_weapon="Proton Torpedo",
            secondary_weapon_damage=120,
            secondary_weapon_ammo=15,
        )
        
        self.executor_destroyer = Starship(
            ship_type=StarshipType.EXECUTOR_DESTROYER,
            name="Executor-class Super Star Destroyer",
            description="Flagship of the Imperial Fleet. Command and control from orbit.",
            role=StarshipRole.COMMAND,
            owned=False,
            unlock_condition="Unlock later (Level 15+)",
            primary_weapon="Turbolaser Battery",
            primary_weapon_damage=200,
            primary_weapon_ammo=5000,
            secondary_weapon="Ion Cannon Array",
            secondary_weapon_damage=150,
            secondary_weapon_ammo=2000,
        )
        
        # Track which ship is currently active
        self.active_ship: Optional[StarshipType] = None
        
        # Fleet-wide upgrades available
        self.available_upgrades: Dict[str, StarshipUpgrade] = self._initialize_upgrades()
        
        # Fleet stats
        self.total_credits: int = 0
        self.total_missions: int = 0
    
    def _initialize_upgrades(self) -> Dict[str, StarshipUpgrade]:
        """Initialize upgrades available across the fleet"""
        upgrades = {}
        
        # Fighter upgrades
        upgrades["reinforced_hull_fighter"] = StarshipUpgrade(
            id="reinforced_hull_fighter",
            name="Reinforced Hull Plating (Fighter)",
            description="Strengthen fighter hull against energy weapons.",
            component=StarshipComponent.HULL,
            tier=1,
            credits_cost=2000,
            hull_bonus=15
        )
        
        upgrades["enhanced_cannons"] = StarshipUpgrade(
            id="enhanced_cannons",
            name="Enhanced Laser Cannons",
            description="More powerful laser fire.",
            component=StarshipComponent.WEAPONS,
            tier=1,
            credits_cost=1500,
            weapon_damage_bonus=15
        )
        
        upgrades["hyperdrive_mk2"] = StarshipUpgrade(
            id="hyperdrive_mk2",
            name="Mark II Hyperdrive",
            description="Faster lightspeed jumps.",
            component=StarshipComponent.HYPERDRIVE,
            tier=2,
            credits_cost=5000,
            hyperdrive_speed_bonus=20
        )
        
        # Command ship upgrades
        upgrades["capital_hull_upgrade"] = StarshipUpgrade(
            id="capital_hull_upgrade",
            name="Enhanced Capital Hull",
            description="Improve durability of capital ships.",
            component=StarshipComponent.HULL,
            tier=3,
            credits_cost=8000,
            hull_bonus=50
        )
        
        upgrades["shield_generator_capital"] = StarshipUpgrade(
            id="shield_generator_capital",
            name="Heavy Shield Generator",
            description="Powerful shields for large vessels.",
            component=StarshipComponent.SHIELDS,
            tier=2,
            credits_cost=6000,
            shield_strength_bonus=40
        )
        
        upgrades["targeting_computer_advanced"] = StarshipUpgrade(
            id="targeting_computer_advanced",
            name="Advanced Targeting Computer",
            description="Pinpoint accuracy for capital weapons.",
            component=StarshipComponent.TARGETING,
            tier=2,
            credits_cost=4000,
            sensor_range_bonus=25
        )
        
        # Legendary upgrades
        upgrades["kyber_reactor_upgrade"] = StarshipUpgrade(
            id="kyber_reactor_upgrade",
            name="Kyber-Enhanced Reactor",
            description="Unlock the power of kyber crystals in your weapons.",
            component=StarshipComponent.WEAPONS,
            tier=5,
            credits_cost=15000,
            weapon_damage_bonus=100
        )
        
        upgrades["cloaking_device"] = StarshipUpgrade(
            id="cloaking_device",
            name="Cloaking Device",
            description="Become invisible to enemy sensors.",
            component=StarshipComponent.TARGETING,
            tier=4,
            credits_cost=10000,
            sensor_range_bonus=50
        )
        
        return upgrades
    
    def acquire_eta2(self) -> str:
        """Acquire the Eta-2 Interceptor (reward for defeating pirates)"""
        if self.eta2_interceptor.owned:
            return "You already own the Eta-2 Interceptor."
        
        self.eta2_interceptor.owned = True
        self.eta2_interceptor.is_flight_ready = True
        self.eta2_interceptor.docking_location = "Kashyyyk Spaceport"
        
        return "✓ ACQUIRED: Black Eta-2 Actis-class Interceptor\nYour personal starfighter is ready for deployment."
    
    def acquire_tie_advanced(self) -> str:
        """Unlock the TIE Advanced x1 (later in game)"""
        if self.tie_advanced.owned:
            return "You already own the TIE Advanced x1."
        
        self.tie_advanced.owned = True
        self.tie_advanced.is_flight_ready = True
        self.tie_advanced.docking_location = "Imperial Fleet"
        
        return "✓ ACQUIRED: TIE Advanced x1\nThe Empire's finest fighter is at your disposal."
    
    def acquire_executor(self) -> str:
        """Unlock the Executor-class Super Star Destroyer (endgame)"""
        if self.executor_destroyer.owned:
            return "You already command the Executor-class Super Star Destroyer."
        
        self.executor_destroyer.owned = True
        self.executor_destroyer.is_flight_ready = True
        self.executor_destroyer.docking_location = "Imperial Command Station"
        
        return "✓ ACQUIRED: Executor-class Super Star Destroyer\nYou now command the flagship of the Imperial Fleet."
    
    def get_owned_ships(self) -> List[Starship]:
        """Get list of all owned ships"""
        ships = []
        if self.eta2_interceptor.owned:
            ships.append(self.eta2_interceptor)
        if self.tie_advanced.owned:
            ships.append(self.tie_advanced)
        if self.executor_destroyer.owned:
            ships.append(self.executor_destroyer)
        return ships
    
    def get_available_ships(self) -> List[Starship]:
        """Get list of all available but unowned ships"""
        ships = []
        if not self.eta2_interceptor.owned:
            ships.append(self.eta2_interceptor)
        if not self.tie_advanced.owned:
            ships.append(self.tie_advanced)
        if not self.executor_destroyer.owned:
            ships.append(self.executor_destroyer)
        return ships
    
    def set_active_ship(self, ship_type: StarshipType) -> Tuple[bool, str]:
        """Set which ship is currently active"""
        if ship_type == StarshipType.ETA2_INTERCEPTOR and not self.eta2_interceptor.owned:
            return False, "You don't own the Eta-2 Interceptor yet."
        elif ship_type == StarshipType.TIE_ADVANCED and not self.tie_advanced.owned:
            return False, "You don't own the TIE Advanced x1 yet."
        elif ship_type == StarshipType.EXECUTOR_DESTROYER and not self.executor_destroyer.owned:
            return False, "You don't own the Executor-class Super Star Destroyer yet."
        
        self.active_ship = ship_type
        return True, f"Active ship: {self.get_ship_by_type(ship_type).name}"
    
    def get_ship_by_type(self, ship_type: StarshipType) -> Starship:
        """Get a ship by type"""
        if ship_type == StarshipType.ETA2_INTERCEPTOR:
            return self.eta2_interceptor
        elif ship_type == StarshipType.TIE_ADVANCED:
            return self.tie_advanced
        else:
            return self.executor_destroyer
    
    def get_active_ship(self) -> Optional[Starship]:
        """Get currently active ship"""
        if self.active_ship:
            return self.get_ship_by_type(self.active_ship)
        return None
    
    def install_upgrade(self, ship_type: StarshipType, upgrade_id: str, credits_available: int) -> Tuple[bool, str]:
        """Install an upgrade on a specific ship"""
        if upgrade_id not in self.available_upgrades:
            return False, "Unknown upgrade."
        
        upgrade = self.available_upgrades[upgrade_id]
        
        if upgrade.installed:
            return False, "This upgrade is already installed."
        
        if credits_available < upgrade.credits_cost:
            return False, f"Insufficient credits ({credits_available}/{upgrade.credits_cost})"
        
        ship = self.get_ship_by_type(ship_type)
        
        if not ship.owned:
            return False, f"You don't own the {ship.name} yet."
        
        # Install upgrade
        upgrade.installed = True
        ship.installed_upgrades[upgrade_id] = upgrade
        
        # Apply effects
        if upgrade.weapon_damage_bonus:
            ship.primary_weapon_damage += upgrade.weapon_damage_bonus
        if upgrade.hull_bonus:
            ship.hull_integrity = min(100, ship.hull_integrity + upgrade.hull_bonus)
        if upgrade.shield_strength_bonus:
            ship.shields_available = True
        
        return True, f"✓ Installed {upgrade.name} on {ship.name}"
    
    def get_fleet_status(self) -> Dict:
        """Get summary of entire fleet status"""
        return {
            "total_ships_owned": len(self.get_owned_ships()),
            "eta2_owned": self.eta2_interceptor.owned,
            "tie_advanced_owned": self.tie_advanced.owned,
            "executor_owned": self.executor_destroyer.owned,
            "active_ship": self.active_ship.value if self.active_ship else "None",
            "total_missions": self.total_missions,
            "fleet_credits": self.total_credits,
        }