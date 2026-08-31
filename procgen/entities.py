from __future__ import annotations

import copy
import random
from typing import TYPE_CHECKING, List, Tuple

from data_loader import ITEMS, MONSTERS, TRAPS
if TYPE_CHECKING:
    from game_map import GameMap
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
        if not (item.spawn_min <= floor <= item.spawn_max):
            continue

        if item.spawn_rooms and room_type not in item.spawn_rooms:
            continue

        candidates.append((item, item.spawn_weight))

    if not candidates:
        return []

    items = [item for item, _ in candidates]
    weights = [weight for _, weight in candidates]
    return random.choices(items, weights=weights, k=count)


def get_monster_candidates(monsters, floor: int, monster_tags=None):
    """Return floor-eligible monster prototypes and their selection weights."""
    monster_tags = [tag.lower() for tag in (monster_tags or [])]
    candidates = []

    for monster in monsters.values():
        if not (monster.spawn_min <= floor <= monster.spawn_max):
            continue

        if monster_tags and not any(
            tag in monster.name.lower() for tag in monster_tags
        ):
            continue

        candidates.append((monster, monster.rarity))

    return candidates


def get_monsters_for_floor(
    monsters,
    floor: int,
    count: int,
    monster_tags=None,
    additional_monsters=None,
):
    """Select monster prototypes for a floor, including optional extra pools."""
    candidates = get_monster_candidates(monsters, floor, monster_tags)

    if additional_monsters:
        candidates.extend(get_monster_candidates(additional_monsters, floor))

    if not candidates:
        return []

    monster_types = [monster for monster, _ in candidates]
    weights = [weight for _, weight in candidates]

    chosen = random.choices(monster_types, weights=weights, k=count)

    result = []
    for monster in chosen:
        pack_size = random.randint(monster.group_min, monster.group_max)
        result.extend([monster] * pack_size)

    return result


# -------------------------------------------------
# ENTITY PLACEMENT HELPERS
# -------------------------------------------------

def can_spawn_at(dungeon: GameMap, x: int, y: int) -> bool:
    """Return True when an entity can safely occupy the tile."""
    return (
        dungeon.in_bounds(x, y)
        and dungeon.tiles["walkable"][x, y]
        and (x, y) != dungeon.downstairs_location
        and not any(entity.x == x and entity.y == y for entity in dungeon.entities)
    )


def spawn_entity_at(dungeon: GameMap, entity, x: int, y: int) -> bool:
    """Spawn a copy of an entity prototype at a valid location."""
    if not can_spawn_at(dungeon, x, y):
        return False

    spawn_entity = copy.deepcopy(entity)
    spawn_entity.spawn(dungeon, x, y)
    return True


def place_monsters_on_map(
    dungeon: GameMap,
    floor_number: int,
    monster_tags=None,
    monsters=None,
    additional_monsters=None,
    count=None,
) -> None:
    """Select and spawn monsters anywhere on the map."""
    if monsters is None:
        monsters = MONSTERS

    if count is None:
        count = random.randint(
            0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
        )

    monster_prototypes = get_monsters_for_floor(
        monsters,
        floor_number,
        count,
        monster_tags=monster_tags,
        additional_monsters=additional_monsters,
    )

    for monster in monster_prototypes:
        for _ in range(20):
            x = random.randint(1, dungeon.width - 2)
            y = random.randint(1, dungeon.height - 2)

            if spawn_entity_at(dungeon, monster, x, y):
                break


def spawn_items_in_room(
    room: "RectangularRoom",
    dungeon: GameMap,
    floor_number: int,
    count: int,
) -> None:
    """Select and spawn items inside a room."""
    items = get_items_for_floor(floor_number, count, room.room_type)

    for item in items:
        base_x = random.randint(room.x1 + 1, room.x2 - 1)
        base_y = random.randint(room.y1 + 1, room.y2 - 1)

        for _ in range(10):
            x = base_x + random.randint(-2, 2)
            y = base_y + random.randint(-2, 2)

            if room.room_type == "treasure" and (x, y) == room.center:
                continue

            if spawn_entity_at(dungeon, item, x, y):
                break


def spawn_monsters_in_room(
    room: "RectangularRoom",
    dungeon: GameMap,
    floor_number: int,
    count: int,
    monster_tags=None,
) -> None:
    """Select and spawn monsters inside a room, with pack clustering."""
    monsters = get_monsters_for_floor(
        MONSTERS,
        floor_number,
        count,
        monster_tags=monster_tags,
    )

    for monster in monsters:
        base_x = random.randint(room.x1 + 1, room.x2 - 1)
        base_y = random.randint(room.y1 + 1, room.y2 - 1)

        for _ in range(10):
            x = base_x + random.randint(-2, 2)
            y = base_y + random.randint(-2, 2)

            if spawn_entity_at(dungeon, monster, x, y):
                break


# -------------------------------------------------
# ROOM ENTITY PLACEMENT
# -------------------------------------------------

def place_entities(
    room: "RectangularRoom",
    dungeon: GameMap,
    floor_number: int,
    monster_tags=None,
) -> None:
    """Spawn a room's traps, monsters, and items."""
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    place_traps(room, dungeon, floor_number)

    if room.room_type == "treasure":
        number_of_items = 0
        number_of_monsters = max(0, number_of_monsters - 1)
    elif room.room_type == "nest":
        number_of_monsters += 2
    elif room.room_type == "collapsed":
        number_of_monsters = max(0, number_of_monsters - 1)

    spawn_items_in_room(room, dungeon, floor_number, number_of_items)
    spawn_monsters_in_room(
        room,
        dungeon,
        floor_number,
        number_of_monsters,
        monster_tags=monster_tags,
    )


# -------------------------------------------------
# TRAPS
# -------------------------------------------------

def get_traps_for_floor(floor: int):
    return [
        trap
        for trap in TRAPS.values()
        if trap.spawn_min <= floor <= trap.spawn_max
        for _ in range(trap.rarity)
    ]


def place_traps(room: "RectangularRoom", dungeon: GameMap, floor: int) -> None:
    traps = get_traps_for_floor(floor)

    if not traps:
        return

    player = dungeon.engine.player

    for _ in range(random.randint(0, 2)):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not can_spawn_at(dungeon, x, y):
            continue

        if abs(x - player.x) <= 2 and abs(y - player.y) <= 2:
            continue

        trap = random.choice(traps)
        spawn_entity_at(dungeon, trap, x, y)
