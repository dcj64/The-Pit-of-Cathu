from __future__ import annotations

from components.base_component import BaseComponent
from equipment_types import EquipmentType

from entity import Item


class Equippable(BaseComponent):
    """Defines which equipment slot an item occupies.

    Numerical bonuses are stored on Item.stats and are handled by Equipment.
    """

    parent: Item

    def __init__(self, equipment_type: EquipmentType):
        self.equipment_type = equipment_type
