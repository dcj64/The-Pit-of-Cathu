from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple
import random
import copy
from game_map import GameMap
from data_loader import ITEMS, MONSTERS

if TYPE_CHECKING:
    from procgen.dungeon import RectangularRoom



# -------------------------------------------------
# FLOOR SCALING
# -------------------------------------------------

max_items_by_floor = [
    (1, 4),
    (4, 6),
]

max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

# -------------------------------------------------
# FLOOR VALUE HELPER
# -------------------------------------------------

def get_max_value_for_floor(
    max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:

    value = 0

    for floor_minimum, floor_value in max_value_by_floor:
        if floor >= floor_minimum:
            value = floor_value

    return value


# -------------------------------------------------
# RANDOM ENTITY SELECTION
# -------------------------------------------------
def get_items_for_floor(floor: int, count: int, room_type: str):
    candidates = []

    for item in ITEMS.values():
        print(f"Checking item: {item.name}")
        if getattr(item, "spawn_min", 0) > floor:
            continue

        if getattr(item, "spawn_rooms", None) and room_type not in getattr(item, "spawn_rooms"):
            continue

        weight = getattr(item, "spawn_weight", 1)
        candidates.append((item, weight))
        print(f"Items selected for floor {floor}: {[item.name for item, _ in candidates]}")
    if not candidates:
        return []

    items = [i for i, _ in candidates]
    weights = [w for _, w in candidates]
    
    print("Items to spawn:", [item.name for item in items])
    print("Items candidates:",[i.name for i, _ in candidates])
    return random.choices(items, weights=weights, k=count)

""" def get_items_for_floor(floor: int, count: int, room_type: str):

    candidates = []

    for item in ITEMS.values():

        if getattr(item, "spawn_min", 0) > floor:
            continue

        allowed_rooms = getattr(item, "spawn_rooms", None)

        if allowed_rooms and room_type not in allowed_rooms:
            continue

        weight = getattr(item, "spawn_weight", 1)

        candidates.append((item, weight))

    if not candidates:
        return []

    items = [i for i, _ in candidates]
    weights = [w for _, w in candidates]

    return random.choices(items, weights=weights, k=count) """

# -------------------------------------------------
# MONSTER SPAWN SYSTEM
# -------------------------------------------------

def get_monsters_for_floor(monsters, floor, count):

    candidates = [
        (monster, monster.rarity)
        for monster in monsters.values()
        if monster.spawn_min <= floor <= monster.spawn_max
    ]

    if not candidates:
        return []

    monster_types = [m for m, _ in candidates]
    weights = [w for _, w in candidates]

    chosen = random.choices(monster_types, weights=weights, k=count)

    result = []

    for monster in chosen:

        pack_size = random.randint(monster.group_min, monster.group_max)

        for _ in range(pack_size):
            result.append(monster)

    return result


# -------------------------------------------------
# ENTITY PLACEMENT
# -------------------------------------------------

def place_entities(room: "RectangularRoom", dungeon: GameMap, floor_number: int) -> None:

    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )

    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )
        
# ---------------------------------
# ROOM TYPE MODIFIERS
# ---------------------------------

    if room.room_type == "treasure":
        number_of_items = 0
        number_of_monsters = max(0, number_of_monsters - 1)
        
        print("Treasure room detected")

    elif room.room_type == "nest":
        number_of_monsters += 2

    elif room.room_type == "collapsed":
        number_of_monsters = max(0, number_of_monsters - 1)

    # ---------------------------------

    items = get_items_for_floor(
    floor_number,
    number_of_items,
    room.room_type
    )
    
    monsters = get_monsters_for_floor(
        MONSTERS,
        floor_number,
        number_of_monsters
    )
            
    for entity in monsters + items:
        
        # Choose a base spawn point
        while True:
            base_x = random.randint(room.x1 + 1, room.x2 - 1)
            base_y = random.randint(room.y1 + 1, room.y2 - 1)

            # Avoid chest tile in treasure rooms
            if room.room_type == "treasure" and (base_x, base_y) == room.center:
                continue

            break

        # Try nearby tiles first (pack clustering)
        for _ in range(10):

            x = base_x + random.randint(-2, 2)
            y = base_y + random.randint(-2, 2)

            if not dungeon.in_bounds(x, y):
                continue

            if not dungeon.tiles["walkable"][x, y]:
                continue

            if any(e.x == x and e.y == y for e in dungeon.entities):
                continue

            spawn_entity = copy.deepcopy(entity)
            spawn_entity.spawn(dungeon, x, y)
            break
        
