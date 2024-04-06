from __future__ import annotations

from typing import List, TYPE_CHECKING

import config
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You dropped the {item.name}.")
        if item.name == "Health Potion":
            config.health_potion_total = config.health_potion_total - 1
        elif item.name == "Lightning Scroll":
            config.lightning_scroll_total = config.lightning_scroll_total - 1
        elif item.name == "Confusion Scroll":
            config.confusion_scroll_total = config.confusion_scroll_total - 1
        elif item.name == "Fireball Scroll":
            config.fireball_scroll_total = config.confusion_scroll_total - 1
        elif item.name == "Berserker Scroll":
            config.berserker_scroll_total = config.berserker_scroll_total - 1
        elif item.name == "Genocide Scroll":
            config.genocide_scroll_total = config.genocide_scroll_total - 1
        elif item.name == "Lamp of Iris":
            config.lamp_of_Iris_scroll_total = config.lamp_of_Iris_scroll_total - 1
