from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterator, List, Tuple
import random

from game_map import GameMap
from entity import Entity
import entity_factories
import tile_types
import config


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
    0: [(entity_factories.health_potion, 35), (entity_factories.berserker_scroll, 30),
        (entity_factories.ring_of_strength, 35), (entity_factories.amulet_of_sol, 35)],
    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25), (entity_factories.sword, 5)],
    6: [(entity_factories.fireball_scroll, 25), (entity_factories.chain_mail, 15)],
    8: [(entity_factories.amulet_of_sol, 30)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30), (entity_factories.shambler, 15)],
    7: [(entity_factories.troll, 60), (entity_factories.shambler, 30)],
    10: [(entity_factories.cathu, 30)],
}



def place_entities(room: "RectangularRoom", dungeon: GameMap, floor_number: int) -> None:
    number_of_monsters = random.randint(0, get_max_value_for_floor(max_monsters_by_floor, floor_number))
    number_of_items = random.randint(0, get_max_value_for_floor(max_items_by_floor, floor_number))

    monsters: List[Entity] = get_entities_at_random(enemy_chances, number_of_monsters, floor_number)
    items: List[Entity] = get_entities_at_random(item_chances, number_of_items, floor_number)

    # total_monsters = len(monsters)
    # print(total_monsters)
    config.total_level_monsters = config.total_level_monsters + len(monsters)

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)

    for x in range(1, dungeon.width - 1):
        for y in range(1, dungeon.height - 1):

            if not dungeon.tiles["walkable"][x, y]:
                continue

            # Neighbours
            left  = dungeon.tiles["walkable"][x - 1, y]
            right = dungeon.tiles["walkable"][x + 1, y]
            up    = dungeon.tiles["walkable"][x, y - 1]
            down  = dungeon.tiles["walkable"][x, y + 1]

            walkable_count = sum([left, right, up, down])

            if walkable_count != 2:
                continue

            # Must be straight corridor
            horizontal = left and right and not up and not down
            vertical   = up and down and not left and not right

            if not (horizontal or vertical):
                continue

            # NEW RULE:
            # At least one adjacent tile must have 3+ walkable neighbours
            # (meaning it's part of a room interior)
            adjacent_positions = [
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1),
            ]

            touches_room = False

            for ax, ay in adjacent_positions:
                if not dungeon.tiles["walkable"][ax, ay]:
                    continue

                neighbors_of_neighbor = sum([
                    dungeon.tiles["walkable"][ax - 1, ay],
                    dungeon.tiles["walkable"][ax + 1, ay],
                    dungeon.tiles["walkable"][ax, ay - 1],
                    dungeon.tiles["walkable"][ax, ay + 1],
                ])

                if neighbors_of_neighbor >= 3:
                    touches_room = True
                    break

            if touches_room and random.random() < 0.3:  # 30% chance to place a door
                dungeon.tiles[x, y] = tile_types.door_closed



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