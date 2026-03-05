from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent


if TYPE_CHECKING:
    from entity import Item


class Inventory(BaseComponent):

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    def drop(self, item: Item) -> None:
        if self.parent.equipment.item_is_equipped(item):
            self.parent.equipment.toggle_equip(item, add_message=False)

        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You dropped the {item.name}.")


