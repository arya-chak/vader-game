"""
Inventory System for Darth Vader RPG
Manages items, equipment, and loot collection.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ItemRarity(Enum):
    """Item rarity levels"""
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


class ItemType(Enum):
    """Types of items in inventory"""
    LIGHTSABER = "lightsaber"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    UPGRADE = "upgrade"
    TROPHY = "trophy"
    QUEST = "quest_item"


@dataclass
class Item:
    """Represents a single item"""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    quantity: int = 1
    
    # Stats/effects
    damage_bonus: int = 0
    defense_bonus: int = 0
    force_point_bonus: int = 0
    darkness_bonus: int = 0
    
    # Crafting/loot info
    value: int = 0  # Credit value
    weight: int = 0  # Encumbrance (future system)
    
    # Special properties
    is_unique: bool = False
    is_cursed: bool = False
    can_sell: bool = True
    can_discard: bool = True


@dataclass
class Equipment:
    """Currently equipped items"""
    lightsaber: Optional[Item] = None
    chest_armor: Optional[Item] = None
    leg_armor: Optional[Item] = None
    arm_armor: Optional[Item] = None
    accessory: Optional[Item] = None
    
    def get_all_equipped(self) -> List[Item]:
        """Return list of all equipped items"""
        equipped = []
        if self.lightsaber:
            equipped.append(self.lightsaber)
        if self.chest_armor:
            equipped.append(self.chest_armor)
        if self.leg_armor:
            equipped.append(self.leg_armor)
        if self.arm_armor:
            equipped.append(self.arm_armor)
        if self.accessory:
            equipped.append(self.accessory)
        return equipped
    
    def get_total_bonuses(self) -> Dict[str, int]:
        """Calculate total stat bonuses from all equipped items"""
        bonuses = {
            "damage": 0,
            "defense": 0,
            "force_points": 0,
            "darkness": 0
        }
        
        for item in self.get_all_equipped():
            bonuses["damage"] += item.damage_bonus
            bonuses["defense"] += item.defense_bonus
            bonuses["force_points"] += item.force_point_bonus
            bonuses["darkness"] += item.darkness_bonus
        
        return bonuses


class Inventory:
    """
    Manages Vader's inventory of items.
    Can hold unlimited unique items, but limited quantities of consumables.
    """
    
    def __init__(self, max_consumables: int = 99):
        self.items: Dict[str, Item] = {}  # item_id: Item
        self.equipment = Equipment()
        self.max_consumables = max_consumables
        self.credits = 0
        
        # Initialize with starting gear
        self._initialize_starting_items()
    
    def _initialize_starting_items(self):
        """Set up Vader's starting equipment"""
        # Vader's iconic lightsaber
        vader_saber = Item(
            id="vader_red_saber",
            name="Vader's Lightsaber",
            description="A dark red lightsaber, forged in the fires of pain and rage. The blade crackles with barely contained fury.",
            item_type=ItemType.LIGHTSABER,
            rarity=ItemRarity.LEGENDARY,
            damage_bonus=15,
            is_unique=True,
            can_discard=False,
            value=0
        )
        self.items[vader_saber.id] = vader_saber
        self.equipment.lightsaber = vader_saber
        
        # Vader's suit armor (starts equipped)
        suit_armor = Item(
            id="vader_suit",
            name="Vader's Suit",
            description="The life support armor that keeps Vader alive. Imposing, terrifying, and surprisingly durable.",
            item_type=ItemType.ARMOR,
            rarity=ItemRarity.LEGENDARY,
            defense_bonus=20,
            is_unique=True,
            can_sell=False,
            can_discard=False,
            value=0
        )
        self.items[suit_armor.id] = suit_armor
        self.equipment.chest_armor = suit_armor
        
        # Starting credits
        self.credits = 100
    
    def add_item(self, item: Item) -> bool:
        """
        Add an item to inventory.
        For consumables, adds to quantity if item already exists.
        For unique items that already exist, returns False (can't have duplicates).
        Returns True if successful.
        """
        if item.id in self.items:
            existing = self.items[item.id]
            if item.item_type == ItemType.CONSUMABLE:
                # Check max consumables limit
                if existing.quantity + item.quantity > self.max_consumables:
                    return False
                existing.quantity += item.quantity
                return True
            else:
                # Unique items can't stack
                return False
        else:
            self.items[item.id] = item
            return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove an item from inventory by quantity.
        Returns True if successful.
        """
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        if item.quantity <= quantity:
            del self.items[item_id]
        else:
            item.quantity -= quantity
        
        return True
    
    def equip_item(self, item_id: str) -> tuple[bool, str]:
        """
        Equip an item to appropriate slot.
        Returns (success, message)
        """
        if item_id not in self.items:
            return False, "Item not found in inventory"
        
        item = self.items[item_id]
        
        # Determine slot based on item type
        if item.item_type == ItemType.LIGHTSABER:
            if self.equipment.lightsaber:
                old_saber = self.equipment.lightsaber
                self.items[old_saber.id] = old_saber
            self.equipment.lightsaber = item
            del self.items[item_id]
            return True, f"Equipped {item.name}"
        
        elif item.item_type == ItemType.ARMOR:
            # For simplicity, assume all armor goes to chest
            if self.equipment.chest_armor:
                old_armor = self.equipment.chest_armor
                self.items[old_armor.id] = old_armor
            self.equipment.chest_armor = item
            del self.items[item_id]
            return True, f"Equipped {item.name}"
        
        elif item.item_type == ItemType.ACCESSORY:
            if self.equipment.accessory:
                old_accessory = self.equipment.accessory
                self.items[old_accessory.id] = old_accessory
            self.equipment.accessory = item
            del self.items[item_id]
            return True, f"Equipped {item.name}"
        
        else:
            return False, f"Cannot equip {item.item_type.value}"
    
    def unequip_item(self, slot: str) -> tuple[bool, str]:
        """
        Unequip an item from a slot.
        Returns (success, message)
        """
        item = None
        
        if slot == "lightsaber":
            item = self.equipment.lightsaber
            self.equipment.lightsaber = None
        elif slot == "chest":
            item = self.equipment.chest_armor
            self.equipment.chest_armor = None
        elif slot == "legs":
            item = self.equipment.leg_armor
            self.equipment.leg_armor = None
        elif slot == "arms":
            item = self.equipment.arm_armor
            self.equipment.arm_armor = None
        elif slot == "accessory":
            item = self.equipment.accessory
            self.equipment.accessory = None
        else:
            return False, "Unknown slot"
        
        if not item:
            return False, "Nothing equipped in that slot"
        
        self.add_item(item)
        return True, f"Unequipped {item.name}"
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item from inventory"""
        return self.items.get(item_id)
    
    def get_all_items_of_type(self, item_type: ItemType) -> List[Item]:
        """Get all items of a specific type"""
        return [item for item in self.items.values() if item.item_type == item_type]
    
    def add_credits(self, amount: int) -> None:
        """
        Add credits to inventory.
        
        Args:
            amount: Number of credits to add
        """
        self.credits += amount
    
    def process_loot(self, items: List[Item], credits: int) -> Dict:
        """
        Process loot from a defeated enemy or boss.
        Adds items and credits to inventory.
        
        Args:
            items: List of Item objects to add
            credits: Number of credits to add
        
        Returns:
            Dictionary with results: {
                'items_added': list of item names,
                'items_failed': list of items that couldn't be added,
                'credits_added': total credits added,
                'new_items': bool indicating if inventory changed
            }
        """
        results = {
            'items_added': [],
            'items_failed': [],
            'credits_added': credits,
            'new_items': False
        }
        
        # Add items
        for item in items:
            if self.add_item(item):
                results['items_added'].append(item.name)
                results['new_items'] = True
            else:
                results['items_failed'].append(item.name)
        
        # Add credits
        if credits > 0:
            self.add_credits(credits)
            results['new_items'] = True
        
        return results
    
    def get_inventory_summary(self) -> Dict:
        """Get a summary of inventory"""
        return {
            "total_items": len(self.items),
            "total_quantity": sum(item.quantity for item in self.items.values()),
            "credits": self.credits,
            "equipped": {
                "lightsaber": self.equipment.lightsaber.name if self.equipment.lightsaber else "None",
                "chest": self.equipment.chest_armor.name if self.equipment.chest_armor else "None",
                "legs": self.equipment.leg_armor.name if self.equipment.leg_armor else "None",
                "arms": self.equipment.arm_armor.name if self.equipment.arm_armor else "None",
                "accessory": self.equipment.accessory.name if self.equipment.accessory else "None",
            }
        }