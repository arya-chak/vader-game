"""
Character Sheet Display System
Displays character stats, inventory, equipment, and force power progression.
"""

from typing import List, Dict, Optional
from inventory_system import Inventory, ItemType, ItemRarity


class CharacterSheet:
    """
    Displays and manages the character sheet interface.
    Can show: stats, inventory, equipment, force power tree
    """
    
    def __init__(self, vader, suit, force_powers, inventory):
        self.vader = vader
        self.suit = suit
        self.force_powers = force_powers
        self.inventory = inventory
    
    def display_full_sheet(self):
        """Display complete character sheet"""
        print("\n" + "="*80)
        print("CHARACTER SHEET - DARTH VADER".center(80))
        print("="*80)
        
        self.display_core_stats()
        print()
        self.display_psychological_state()
        print()
        self.display_equipped_items()
        print()
        print("="*80)
    
    def display_core_stats(self):
        """Display core character statistics"""
        print("\n" + "─"*80)
        print("CORE STATISTICS".center(80))
        print("─"*80)
        
        # Basic info
        print(f"\nName: {self.vader.name}")
        print(f"Title: {self.vader.title}")
        print(f"Level: {self.vader.level} | Experience: {self.vader.experience}")
        
        # Health and resources
        print(f"\nHealth: {self.vader.current_health}/{self.vader.max_health} HP")
        print(f"Force Points: {self.vader.current_force_points}/{self.vader.max_force_points} FP")
        print(f"Suit Integrity: {self.suit.integrity}%")
        
        # Core attributes (1-10 scale)
        print(f"\n{'ATTRIBUTE':<20} {'SCORE':<10} {'MODIFIER':<10}")
        print("─" * 40)
        
        stats = [
            ("Strength", self.vader.stats.strength),
            ("Dexterity", self.vader.stats.dexterity),
            ("Constitution", self.vader.stats.constitution),
            ("Intelligence", self.vader.stats.intelligence),
            ("Wisdom", self.vader.stats.wisdom),
            ("Charisma", self.vader.stats.charisma),
            ("Force Power", self.vader.stats.force_power),
            ("Force Control", self.vader.stats.force_control),
        ]
        
        for name, score in stats:
            modifier = "+" + str(score - 5) if score >= 5 else str(score - 5)
            print(f"{name:<20} {score}/10{'':<5} {modifier:<10}")
        
        # Combat skills
        print(f"\n{'COMBAT SKILLS':<20} {'MASTERY':<10}")
        print("─" * 30)
        
        skills = [
            ("Lightsaber Skill", self.vader.stats.lightsaber_skill),
            ("Force Mastery", self.vader.stats.force_mastery),
            ("Tactics", self.vader.stats.tactics),
            ("Intimidation", self.vader.stats.intimidation),
        ]
        
        for name, score in skills:
            print(f"{name:<20} {score}/10")
    
    def display_psychological_state(self):
        """Display psychological metrics"""
        print("\n" + "─"*80)
        print("PSYCHOLOGICAL STATE".center(80))
        print("─"*80)
        
        ps = self.vader.psychological_state
        
        # Main metrics with visual bars
        metrics = [
            ("Darkness", ps.darkness),
            ("Control", ps.control),
            ("Suppression", ps.suppression),
            ("Rage", ps.rage),
        ]
        
        for metric_name, value in metrics:
            bar = self._create_progress_bar(value, 100)
            print(f"{metric_name:<15} {bar} {value}/100")
        
        # Alignment
        alignment = ps.calculate_dark_side_alignment()
        print(f"\nAlignment: {alignment}")
        
        # Combat stats
        print(f"\nPain Tolerance: {ps.pain_tolerance}/100")
        print(f"Suit Pain Level: {self.suit.current_pain_level}%")
    
    def display_equipped_items(self):
        """Display currently equipped items"""
        print("\n" + "─"*80)
        print("EQUIPPED ITEMS".center(80))
        print("─"*80)
        
        equipment = self.inventory.equipment
        equipped = equipment.get_all_equipped()
        
        if not equipped:
            print("No items equipped")
            return
        
        for item in equipped:
            self._display_item_details(item)
        
        # Show bonuses
        bonuses = equipment.get_total_bonuses()
        if any(bonuses.values()):
            print(f"\nTotal Equipment Bonuses:")
            print(f"  Damage: +{bonuses['damage']}")
            print(f"  Defense: +{bonuses['defense']}")
            print(f"  Force Points: +{bonuses['force_points']}")
            if bonuses['darkness'] != 0:
                print(f"  Darkness: {'+' if bonuses['darkness'] > 0 else ''}{bonuses['darkness']}")
    
    def display_inventory(self):
        """Display inventory screen"""
        print("\n" + "="*80)
        print("INVENTORY".center(80))
        print("="*80)
        
        inventory_summary = self.inventory.get_inventory_summary()
        
        print(f"\nCredits: {inventory_summary['credits']}")
        print(f"Total Items: {inventory_summary['total_items']} | Total Quantity: {inventory_summary['total_quantity']}")
        
        # Group items by type
        print("\n" + "─"*80)
        print("ITEMS BY CATEGORY")
        print("─"*80)
        
        item_types = [
            ItemType.LIGHTSABER,
            ItemType.ARMOR,
            ItemType.ACCESSORY,
            ItemType.CONSUMABLE,
            ItemType.UPGRADE,
            ItemType.TROPHY,
            ItemType.QUEST
        ]
        
        for item_type in item_types:
            items = self.inventory.get_all_items_of_type(item_type)
            if items:
                print(f"\n{item_type.value.upper()}")
                print("─" * 40)
                for item in items:
                    self._display_inventory_item(item)
        
        # Show equipped
        print("\n" + "─"*80)
        print("CURRENTLY EQUIPPED")
        print("─"*80)
        for slot, item_name in inventory_summary['equipped'].items():
            print(f"  {slot.capitalize():<15} {item_name}")
    
    def display_force_power_tree(self):
        """Display force power progression tree"""
        print("\n" + "="*80)
        print("FORCE POWER PROGRESSION".center(80))
        print("="*80)
        
        # Group powers by category
        powers_by_category = {}
        for power_id, power in self.force_powers.available_powers.items():
            category = power.category.value
            if category not in powers_by_category:
                powers_by_category[category] = []
            powers_by_category[category].append(power)
        
        # Display each category
        categories = [
            "telekinesis",
            "dark_side",
            "combat",
            "sense",
            "control",
            "utility"
        ]
        
        for category in categories:
            if category not in powers_by_category:
                continue
            
            powers = powers_by_category[category]
            print(f"\n{category.upper()}")
            print("─" * 80)
            
            for power in powers:
                self._display_power_node(power)
    
    def display_power_details(self, power_id: str):
        """Display detailed info for a single force power"""
        power = self.force_powers.available_powers.get(power_id)
        if not power:
            print(f"Unknown power: {power_id}")
            return
        
        print("\n" + "="*80)
        print(f"{power.name.upper()}".center(80))
        print("="*80)
        
        print(f"\n{power.description}\n")
        
        print("─" * 40)
        print(f"Category: {power.category.value.upper()}")
        print(f"Tier: {power.tier.value}")
        print(f"Status: {'✓ LEARNED' if power.learned else '⊗ NOT LEARNED'}")
        
        print(f"\nCosts & Resources:")
        print(f"  Force Point Cost: {power.force_point_cost}")
        if power.cooldown_turns:
            print(f"  Cooldown: {power.cooldown_turns} turns")
        
        print(f"\nDamage & Effects:")
        if power.base_damage:
            print(f"  Base Damage: {power.base_damage}")
        if power.duration_turns:
            print(f"  Duration: {power.duration_turns} turns")
        if power.area_effect:
            print(f"  Area Effect: Yes")
        
        print(f"\nRequirements:")
        if power.requires_level:
            print(f"  Minimum Level: {power.requires_level}")
        if power.requires_darkness:
            print(f"  Requires Darkness: {power.requires_darkness}")
        if power.requires_control:
            print(f"  Requires Control: {power.requires_control}")
        if power.requires_powers:
            print(f"  Prerequisite Powers: {', '.join(power.requires_powers)}")
        
        print(f"\nProgression:")
        print(f"  Experience to Learn: {power.experience_cost}")
        
        print("\n" + "="*80)
    
    # Helper methods
    
    def _create_progress_bar(self, current: int, maximum: int, width: int = 30) -> str:
        """Create a visual progress bar"""
        filled = int((current / maximum) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _display_item_details(self, item):
        """Display formatted item details"""
        rarity_color = {
            ItemRarity.COMMON: "white",
            ItemRarity.UNCOMMON: "green",
            ItemRarity.RARE: "blue",
            ItemRarity.EPIC: "purple",
            ItemRarity.LEGENDARY: "gold"
        }
        
        print(f"\n{item.name} [{item.rarity.name}]")
        print(f"  {item.description}")
        
        if item.damage_bonus or item.defense_bonus or item.force_point_bonus:
            print(f"  Stats:")
            if item.damage_bonus:
                print(f"    +{item.damage_bonus} Damage")
            if item.defense_bonus:
                print(f"    +{item.defense_bonus} Defense")
            if item.force_point_bonus:
                print(f"    +{item.force_point_bonus} Force Points")
            if item.darkness_bonus:
                darkness_sign = "+" if item.darkness_bonus > 0 else ""
                print(f"    {darkness_sign}{item.darkness_bonus} Darkness")
    
    def _display_inventory_item(self, item):
        """Display item in inventory list format"""
        quantity_str = f" x{item.quantity}" if item.quantity > 1 else ""
        rarity_str = f" [{item.rarity.name}]"
        print(f"  • {item.name}{rarity_str}{quantity_str}")
    
    def _display_power_node(self, power):
        """Display a force power in the tree"""
        learned = "✓" if power.learned else "⊗"
        print(f"\n  {learned} {power.name}")
        print(f"      {power.description[:60]}...")
        print(f"      Cost: {power.force_point_cost} FP | Req Level: {power.requires_level or 'Any'}")