from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple
import random

from game_map import GameMap
from entity import Entity

from setup_game import ITEMS, MONSTERS


if TYPE_CHECKING:
    from procgen.dungeon import RectangularRoom
    from entity import Entity


max_items_by_floor = [
    (1, 1),
    (4, 2),
]

max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(ITEMS["Health Potion"], 35), (ITEMS["Berserker Scroll"], 30),
        (ITEMS["Ring of Strength"], 35), (ITEMS["Amulet of Sol"], 35)],
    2: [(ITEMS["Confusion Scroll"], 10)],
    4: [(ITEMS["Lightning Scroll"], 25), (ITEMS["Sword"], 5)],
    6: [(ITEMS["Fireball Scroll"], 25), (ITEMS["Chain Mail"], 15)],
    8: [(ITEMS["Amulet of Sol"], 30)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(MONSTERS["Orc"], 80)],
    3: [(MONSTERS["Troll"], 15)],
    5: [(MONSTERS["Troll"], 30), (MONSTERS["Shambler"], 15)],
    7: [(MONSTERS["Troll"], 60), (MONSTERS["Shambler"], 30)],
    10: [(MONSTERS["Cathu"], 30)],
}


def get_max_value_for_floor(max_value_by_floor: List[Tuple[int, int]], floor: int) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value


def get_entities_at_random(
    weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]

                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(entities, weights=entity_weighted_chance_values, k=number_of_entities)

    return chosen_entities


def place_entities(room: "RectangularRoom", dungeon: GameMap, floor_number: int) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
        )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
        )

    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
        )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
        )

    
    dungeon.total_monsters = dungeon.total_monsters + len(monsters)

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)

