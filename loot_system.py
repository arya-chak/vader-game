"""
Loot System for Darth Vader RPG
Manages enemy loot drops, quest items, and special rewards.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
from inventory_system import Item, ItemType, ItemRarity


class LootType(Enum):
    """Types of loot"""
    CREDITS = "credits"
    EQUIPMENT = "equipment"
    CONSUMABLE = "consumable"
    QUEST_ITEM = "quest_item"
    TROPHY = "trophy"


@dataclass
class LootDrop:
    """Represents a single loot drop"""
    item: Optional[Item]  # None if credits only
    credits: int = 0
    rarity: ItemRarity = ItemRarity.COMMON
    guaranteed: bool = False  # Always drops if True
    drop_chance: float = 1.0  # 0.0 to 1.0, probability of dropping


class LootTable:
    """
    Defines loot tables for different enemy types and encounters.
    Used to generate loot when enemies are defeated.
    """
    
    def __init__(self):
        self.pirate_thug_table = self._create_pirate_thug_loot()
        self.pirate_leader_table = self._create_pirate_leader_loot()
        self.clone_trooper_table = self._create_clone_trooper_loot()
        self.stormtrooper_table = self._create_stormtrooper_loot()
        
        # Special boss loot
        self.infila_final_loot = self._create_infila_final_loot()
        self.infila_first_duel_loot = self._create_infila_first_duel_loot()
    
    def _create_pirate_thug_loot(self) -> List[LootDrop]:
        """Loot table for basic pirate thugs"""
        return [
            # Credits are primary loot
            LootDrop(item=None, credits=25, guaranteed=True),
        ]
    
    def _create_pirate_leader_loot(self) -> List[LootDrop]:
        """Loot table for pirate leader"""
        return [
            # More credits as reward
            LootDrop(item=None, credits=75, guaranteed=True),
        ]
    
    def _create_clone_trooper_loot(self) -> List[LootDrop]:
        """Loot table for clone troopers"""
        return [
            # Standard military credits
            LootDrop(item=None, credits=40, guaranteed=True),
        ]
    
    def _create_stormtrooper_loot(self) -> List[LootDrop]:
        """Loot table for stormtroopers"""
        return [
            # Standard Imperial credits
            LootDrop(item=None, credits=50, guaranteed=True),
        ]
    
    def _create_infila_first_duel_loot(self) -> List[LootDrop]:
        """Loot from first duel with Infila (scripted loss - no loot)"""
        return []  # No loot on scripted loss
    
    def _create_infila_final_loot(self) -> List[LootDrop]:
        """Loot from defeating Infila - the Kyber Crystal"""
        # NOTE: Item is created fresh each time loot is generated
        # Don't store the item in the loot drop - create it on demand
        return [
            LootDrop(
                item=None,  # We'll create it on demand
                credits=500,
                rarity=ItemRarity.LEGENDARY,
                guaranteed=True
            ),
        ]
    
    def get_loot_for_enemy(self, enemy_name: str, enemy_type: str) -> List[LootDrop]:
        """
        Get loot table for a specific enemy.
        
        Args:
            enemy_name: Display name of enemy
            enemy_type: Type of enemy (stormtrooper, clone_trooper, pirate_thug, etc.)
        
        Returns:
            List of possible loot drops
        """
        if "pirate" in enemy_type.lower() or "pirate" in enemy_name.lower():
            if "leader" in enemy_name.lower():
                return self.pirate_leader_table
            else:
                return self.pirate_thug_table
        elif "clone" in enemy_type.lower() or "clone" in enemy_name.lower():
            return self.clone_trooper_table
        elif "stormtrooper" in enemy_type.lower():
            return self.stormtrooper_table
        else:
            return self.stormtrooper_table  # Default
    
    def get_boss_loot(self, boss_name: str) -> List[LootDrop]:
        """
        Get loot table for a specific boss.
        
        Args:
            boss_name: Name of the boss
        
        Returns:
            List of guaranteed boss loot drops
        """
        if "infila" in boss_name.lower() and "final" in boss_name.lower():
            return self.infila_final_loot
        elif "infila" in boss_name.lower() and "first" in boss_name.lower():
            return self.infila_first_duel_loot
        else:
            return []  # Unknown boss, no loot


class LootGenerator:
    """
    Generates loot drops based on enemy defeats.
    Handles randomization and probability calculations.
    """
    
    def __init__(self):
        self.loot_table = LootTable()
    
    def generate_enemy_loot(self, enemy_name: str, enemy_type: str) -> Tuple[List[Item], int]:
        """
        Generate loot for a defeated enemy.
        
        Args:
            enemy_name: Display name of enemy
            enemy_type: Type of enemy
        
        Returns:
            Tuple of (items_list, total_credits)
        """
        loot_table = self.loot_table.get_loot_for_enemy(enemy_name, enemy_type)
        
        items = []
        total_credits = 0
        
        for loot_drop in loot_table:
            # Check if loot drops
            if loot_drop.guaranteed or random.random() <= loot_drop.drop_chance:
                if loot_drop.item:
                    items.append(loot_drop.item)
                total_credits += loot_drop.credits
        
        return items, total_credits
    
    def generate_boss_loot(self, boss_name: str) -> Tuple[List[Item], int]:
        """
        Generate loot for a defeated boss.
        
        Args:
            boss_name: Name/ID of the boss
        
        Returns:
            Tuple of (items_list, total_credits)
        """
        loot_table = self.loot_table.get_boss_loot(boss_name)
        
        items = []
        total_credits = 0
        
        for loot_drop in loot_table:
            if loot_drop.item:
                items.append(loot_drop.item)
            total_credits += loot_drop.credits
        
        # Special handling: Create Kyber Crystal for Infila FINAL PHASE 2 ONLY
        # (NOT for infila_first scripted loss, NOT for infila_final_phase1)
        if "infila_final_easy" in boss_name.lower() or "infila_final_hard" in boss_name.lower():
            kyber_crystal = Item(
                id="kyber_crystal_infila",
                name="Kyber Crystal - Blue",
                description="A pristine kyber crystal harvested from Jedi Master Kirak Infil'a's lightsaber. "
                            "Still resonates with the light side of the Force, but can be corrupted through pain and rage. "
                            "This is the crystal needed to forge your new red lightsaber.",
                item_type=ItemType.QUEST,
                rarity=ItemRarity.LEGENDARY,
                is_unique=True,
                can_sell=False,
                can_discard=False,
                value=0
            )
            items.append(kyber_crystal)
            total_credits += 500  # Add the credits here too
        
        return items, total_credits
    
    def display_loot_notification(self, items: List[Item], credits: int):
        """
        Display a nice notification of what was looted.
        
        Args:
            items: List of items looted
            credits: Credits looted
        """
        if not items and credits == 0:
            return
        
        print("\n" + "="*70)
        print("LOOT ACQUIRED".center(70))
        print("="*70)
        
        if credits > 0:
            print(f"\n💰 Credits: +{credits}")
        
        if items:
            print(f"\n📦 Items:")
            for item in items:
                rarity_display = f"[{item.rarity.name}]"
                print(f"   • {item.name} {rarity_display}")
                print(f"     {item.description[:60]}...")
        
        print("="*70 + "\n")


class SpecialLoot:
    """
    Special loot items that aren't generated randomly.
    Used for unique quest items, ships, etc.
    """
    
    @staticmethod
    def create_starship() -> Item:
        """Create the player's starship"""
        ship = Item(
            id="vader_eta2_interceptor",
            name="Eta-2 Actis-class Interceptor",
            description="Your personal starship. Once Anakin's personal fighter, now dark as the Empire itself. "
                        "Can be upgraded with new parts and weapons.",
            item_type=ItemType.QUEST,
            rarity=ItemRarity.LEGENDARY,
            is_unique=True,
            can_sell=False,
            can_discard=False,
            value=0
        )
        return ship
    
    @staticmethod
    def create_kyber_crystal() -> Item:
        """Create the kyber crystal quest item"""
        crystal = Item(
            id="kyber_crystal_infila",
            name="Kyber Crystal - Blue",
            description="A pristine kyber crystal harvested from Jedi Master Kirak Infil'a's lightsaber. "
                        "Still resonates with the light side of the Force. Required for the Kyber Bleeding ritual.",
            item_type=ItemType.QUEST,
            rarity=ItemRarity.LEGENDARY,
            is_unique=True,
            can_sell=False,
            can_discard=False,
            value=0
        )
        return crystal