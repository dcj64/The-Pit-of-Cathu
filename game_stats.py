from __future__ import annotations


class GameStats:
    """Tracks run-wide statistics for the current game."""

    def __init__(self) -> None:
        # --- Combat ---
        self.total_monsters_killed: int = 0

        # --- Movement ---
        self.moves_used: int = 0

        # --- Items Found ---
        self.items_found: dict[str, int] = {
            "health_potion": 0,
            "confusion_scroll": 0,
            "lightning_scroll": 0,
            "fireball_scroll": 0,
            "berserker_scroll": 0,
            "genocide_scroll": 0,
            "lamp_of_iris_scroll": 0,
        }

        # --- Items Used ---
        self.items_used: dict[str, int] = {
            "health_potion": 0,
            "confusion_scroll": 0,
            "lightning_scroll": 0,
            "fireball_scroll": 0,
            "berserker_scroll": 0,
            "genocide_scroll": 0,
            "lamp_of_iris_scroll": 0,
        }

        # --- Equipment Found ---
        self.equipment_found: dict[str, int] = {
            "amulet": 0,
            "ring": 0,
        }

    # ---------------------------------------------------
    # Helper methods (clean and safe increments)
    # ---------------------------------------------------

    def monster_killed(self) -> None:
        self.total_monsters_killed += 1

    def move_used(self) -> None:
        self.moves_used += 1

    def item_found(self, item_name: str) -> None:
        if item_name in self.items_found:
            self.items_found[item_name] += 1

    def item_used(self, item_name: str) -> None:
        if item_name in self.items_used:
            self.items_used[item_name] += 1

    def equipment_found_item(self, equipment_name: str) -> None:
        if equipment_name in self.equipment_found:
            self.equipment_found[equipment_name] += 1