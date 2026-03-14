from __future__ import annotations

from typing import Optional

from components.base_component import BaseComponent
from equipment_types import EquipmentType

from entity import Actor, Item


class Equipment(BaseComponent[Actor]):
    #parent: Actor

    def __init__(self,
            weapon: Optional[Item] = None,
            armor: Optional[Item] = None,
            amulet: Optional[Item] = None,
            ring1: Optional[Item] = None,
            ring2:Optional[Item] = None,
    ):
        self.weapon = weapon
        self.armor = armor
        self.amulet = amulet
        self.ring1 = ring1
        self.ring2 = ring2

    @property
    def power_bonus(self) -> int:
        return self.stat_bonus("power")


    @property
    def defense_bonus(self) -> int:
        return self.stat_bonus("defense")


    @property
    def light_bonus(self) -> int:
        return self.stat_bonus("light")


    @property
    def regen_bonus(self) -> int:
        return self.stat_bonus("regen")
    
    
    def stat_bonus(self, stat_name: str) -> int:
        """Return total bonus for a given stat from all equipped items."""
        bonus = 0

        for item in self.all_equipped_items():
            if not item:
                continue

            # New JSON stat system
            if hasattr(item, "stats"):
                bonus += item.stats.get(stat_name, 0)

            # Old equippable system (for backwards compatibility)
            if item.equippable:
                bonus += getattr(item.equippable, f"{stat_name}_bonus", 0)

        return bonus

    def item_is_equipped(self, item: Item) -> bool:
        return (
            self.weapon == item
            or self.armor == item
            or self.amulet == item
            or self.ring1 == item
            or self.ring2 == item
        )
    
    def equipped_items(self) -> list[Item]:
        items = []

        if self.weapon:
            items.append(self.weapon)

        if self.armor:
            items.append(self.armor)

        if self.amulet:
            items.append(self.amulet)

        if self.ring1:
            items.append(self.ring1)

        if self.ring2:
            items.append(self.ring2)

        return items
    
    
    def all_equipped_items(self):
        """Return a list of all equipped items."""
        return [
            self.weapon,
            self.armor,
            self.amulet,
            self.ring1,
            self.ring2,
        ]
        

    def rings_equipped(self) -> int:
        count = 0
        if self.ring1:
            count += 1
        if self.ring2:
            count += 1
        return count
    
    def equipped_rings(self) -> list[Item]:
        rings = []
        if self.ring1:
            rings.append(self.ring1)
        if self.ring2:
            rings.append(self.ring2)
        return rings


    def equipped_amulet(self) -> Optional[Item]:
        return self.amulet


    def amulet_equipped(self) -> int:
        return 1 if self.amulet else 0
    

    def unequip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        slot = None
        if (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.WEAPON
        ):
            slot = "weapon"
        elif (
                equippable_item.equippable
                and equippable_item.equippable.equipment_type == EquipmentType.ARMOR
        ):
            slot = "armor"
        elif (
                equippable_item.equippable
                and equippable_item.equippable.equipment_type == EquipmentType.AMULET
        ):
            slot = "amulet"
        elif (
                equippable_item.equippable
                and equippable_item.equippable.equipment_type == EquipmentType.RING
        ):  
            if self.ring1 is None:
                slot = "ring1"
            elif self.ring2 is None:
                slot = "ring2"
            else:
                slot = "ring1"

        if slot is None:
            return

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)