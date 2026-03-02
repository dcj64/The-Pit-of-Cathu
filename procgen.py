from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterator, List, Tuple
import random

import tcod
import config

from game_map import GameMap
import entity_factories
import tile_types

if TYPE_CHECKING:
    from engine import Engine
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


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int) -> None:
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

# Add doors to dungeon rooms. This is a very simple implementation that just adds doors 
# to any walkable tile that has exactly two walkable neighbors, and isn't a diagonal connection.
def add_simple_doors(dungeon: GameMap) -> None:
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

# Add tunnels to connect rooms that aren't already connected. This is a simple implementation that just 
# checks if there's a path between the center of each room, and if not, digs a tunnel.
def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y

# Generate the dungeon map. This is the main function that puts everything together.
# It creates rooms, connects them with tunnels, adds doors, and places entities.
def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""

    # --- Safety validation ---
    if room_min_size > room_max_size:
        raise ValueError(
            f"room_min_size ({room_min_size}) "
            f"cannot be greater than room_max_size ({room_max_size})"
        )

    if room_min_size <= 0:
        raise ValueError("room_min_size must be > 0")

    if room_max_size >= map_width or room_max_size >= map_height:
        raise ValueError("room_max_size is too large for the map dimensions")
    # --- End safety validation ---

    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor

            center_of_last_room = new_room.center

        if len(rooms) != 0:
            place_entities(new_room, dungeon, engine.game_world.current_floor)

            dungeon.tiles[center_of_last_room] = tile_types.down_stairs
            dungeon.downstairs_location = center_of_last_room

        # Finally, append the new room to the list.
        rooms.append(new_room)
        (len(rooms)) #count number of rooms
        config.number_of_rooms = len(rooms)

    add_simple_doors(dungeon)

    return dungeon

def generate_cave(
    map_width: int,
    map_height: int,
    engine: Engine,
    floor_number: int,
    fill_percent: float =0.45
    ) -> GameMap:

    dungeon = GameMap(engine, map_width, map_height, entities=[engine.player])

    # --- Fill with random walls ---
    for x in range(map_width):
        for y in range(map_height):

            # Force solid border
            if x == 0 or y == 0 or x == map_width - 1 or y == map_height - 1:
                dungeon.tiles[x, y] = tile_types.wall
            else:
                dungeon.tiles[x, y] = (
                    tile_types.wall
                    if random.random() < fill_percent
                    else tile_types.floor
                )

    # --- Smooth 3 times ---
    for _ in range(3):
        smooth_map(dungeon)

    # Carve some random square "ruins" into the cave to add some structure and interesting features to break up the randomness of the caves.
    # The number of ruins decreases as you go deeper, since the later caves are more tightly packed and have less room for large open areas.

    carve_ruins(dungeon, ruin_count=2 + floor_number // 2)

    # --- Choose liquid type based on depth ---
    """ for _ in range(random.randint(2, 5)):

    # Depth-based lava chance
    lava_chance = min(0.15 + (floor_number * 0.08), 0.75)

    if random.random() < lava_chance:
        liquid_tile = tile_types.lava
    else:
        liquid_tile = tile_types.water """

    # Add some random water blobs to the cave for variety. The blobs get larger and more common as you go deeper,
    # since the later caves are more tightly packed and have less room for narrow corridors.

    for _ in range(random.randint(3, 6)):

        # Lava chance increases with depth
        lava_chance = min(0.15 + (floor_number * 0.07), 0.7)

        if random.random() < lava_chance:
            tile = tile_types.lava
        else:
            tile = tile_types.water

        x = random.randint(1, dungeon.width - 2)
        y = random.randint(1, dungeon.height - 2)

        if dungeon.tiles["walkable"][x, y] and dungeon.tiles[x, y] == tile_types.floor:
            grow_blob(dungeon, x, y, tile=tile, size=120)

    # Add pillars to the cave for variety. The pillars get more common as you go deeper,
    # since the later caves are more tightly packed and have less room for large open areas.
    add_cave_pillars(dungeon, density=0.015)
    
    # Place player in a random walkable location
    while True:
        px = random.randint(1, map_width - 2)
        py = random.randint(1, map_height - 2)

        if dungeon.tiles[px, py] == tile_types.floor:
            engine.player.place(px, py, dungeon)
            break

    px, py = engine.player.x, engine.player.y

    reachable_tiles = get_reachable_tiles(dungeon, px, py)

    # Place stairs far from player in a reachable location. We compute the distance from the player to each reachable tile,
    # filter to only keep those that are at least 60% of the max distance, and then randomly choose among those far tiles to place the stairs.
    # This ensures that the stairs are always in a location that the player can reach, but encourages them to explore
    # the map rather than placing the stairs right next to them.

    distances = []
    max_distance = 0

    for (x, y) in reachable_tiles:
        distance = abs(x - px) + abs(y - py)
        distances.append(((x, y), distance))
        max_distance = max(max_distance, distance)

    # Only keep tiles at least 60% of max distance
    threshold = max_distance * 0.6

    far_tiles = [pos for pos, dist in distances if dist >= threshold]

    # Randomly choose among far tiles
    sx, sy = random.choice(far_tiles)

    dungeon.tiles[sx, sy] = tile_types.down_stairs
    dungeon.downstairs_location = (sx, sy)

    return dungeon

# Smooth the cave map using cellular automata rules. This is a simple implementation that counts the number of wall neighbors
# and decides whether to turn a tile into a wall or floor based on that count.

def smooth_map(dungeon: GameMap) -> None:
    width, height = dungeon.width, dungeon.height
    new_tiles = dungeon.tiles.copy()

    for x in range(1, width - 1):
        for y in range(1, height - 1):

            wall_count = 0

            for nx in range(x - 1, x + 2):
                for ny in range(y - 1, y + 2):
                    if dungeon.tiles[nx, ny] == tile_types.wall:
                        wall_count += 1

            if wall_count > 4:
                new_tiles[x, y] = tile_types.wall
            else:
                new_tiles[x, y] = tile_types.floor

    dungeon.tiles = new_tiles

# Grow a blob of water starting from a given location. This is used to create small pools of water in the caves.
# The blob grows by randomly adding adjacent tiles to the blob, with a certain chance to continue growing at each step.
# The size parameter controls how large the blob can grow, and the function stops growing once it reaches that size or runs out of adjacent tiles to grow into.

def grow_blob(dungeon: GameMap, start_x: int, start_y: int, tile, size: int = 60):
    stack = [(start_x, start_y)]

    for _ in range(size):
        if not stack:
            break

        x, y = stack.pop()

        if dungeon.tiles["walkable"][x, y]:
            dungeon.tiles[x, y] = tile

            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                if random.random() < 0.7:
                    stack.append((x+dx, y+dy))

# Create square "ruins" in the dungeon. This is a simple implementation that randomly chooses locations
# for the ruins and carves out a square area of floor, surrounded by walls.

def carve_ruins(dungeon: GameMap, ruin_count: int = 3):
    width, height = dungeon.width, dungeon.height

    for _ in range(ruin_count):
        w = random.randint(6, 12)
        h = random.randint(6, 12)

        x = random.randint(2, width - w - 3)
        y = random.randint(2, height - h - 3)

        # --- Carve interior floor ---
        for i in range(x + 1, x + w - 1):
            for j in range(y + 1, y + h - 1):
                dungeon.tiles[i, j] = tile_types.floor

        # --- Build outer walls ---
        for i in range(x, x + w):
            dungeon.tiles[i, y] = tile_types.ruin_wall
            dungeon.tiles[i, y + h - 1] = tile_types.wall

        for j in range(y, y + h):
            dungeon.tiles[x, j] = tile_types.ruin_wall
            dungeon.tiles[x + w - 1, j] = tile_types.wall

        # --- Collapse parts of the walls ---
        collapse_chance = 0.2 # + (ruin_count * 0.05)
        # Increase collapse chance for later ruins, since the later caves 
        # are more tightly packed and have less room for large open areas.

        for i in range(x, x + w):
            if random.random() < collapse_chance:
                dungeon.tiles[i, y] = tile_types.floor
            if random.random() < collapse_chance:
                dungeon.tiles[i, y + h - 1] = tile_types.floor

        for j in range(y, y + h):
            if random.random() < collapse_chance:
                dungeon.tiles[x, j] = tile_types.floor
            if random.random() < collapse_chance:
                dungeon.tiles[x + w - 1, j] = tile_types.floor

        # --- Add interior rubble patches ---
        rubble_patches = random.randint(1, 3)

        for _ in range(rubble_patches):
            rx = random.randint(x + 1, x + w - 2)
            ry = random.randint(y + 1, y + h - 2)

            if random.random() < 0.5:
                dungeon.tiles[rx, ry] = tile_types.wall

# Add pillars to the cave for variety. The pillars get more common as you go deeper, 
# since the later caves are more tightly packed and have less room for large open areas.

def add_cave_pillars(dungeon: GameMap, density: float = 0.015):
        width, height = dungeon.width, dungeon.height

        for x in range(2, width - 2):
            for y in range(2, height - 2):

                # Only consider floor tiles
                if not dungeon.tiles["walkable"][x, y]:
                    continue

                # Check surrounding area to avoid clutter
                neighbors = 0
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if not dungeon.tiles["walkable"][x + dx, y + dy]:
                            neighbors += 1

                # Only place pillar in open spaces
                if neighbors < 2 and random.random() < density:
                    dungeon.tiles[x, y] = tile_types.wall

# Check for reachable tiles from a starting point. This is used to ensure that the stairs
# are placed in a location that the player can actually reach.

def get_reachable_tiles(dungeon: GameMap, start_x: int, start_y: int):
    width, height = dungeon.width, dungeon.height

    visited = set()
    stack = [(start_x, start_y)]

    while stack:
        x, y = stack.pop()

        if (x, y) in visited:
            continue

        visited.add((x, y))

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy

            if (
                0 <= nx < width
                and 0 <= ny < height
                and dungeon.tiles["walkable"][nx, ny]
                and (nx, ny) not in visited
            ):
                stack.append((nx, ny))

    return visited