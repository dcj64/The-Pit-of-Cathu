from __future__ import annotations

from typing import TYPE_CHECKING
import random
import numpy as np

from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine


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
    tiles = dungeon.tiles

    # Create a boolean mask of walls
    wall_mask = (tiles == tile_types.wall)

    # Convert to int for counting
    walls = wall_mask.astype(np.int8)

    # Count neighbors using np.roll (8 directions + self)
    neighbor_count = (
        walls
        + np.roll(walls, 1, axis=0)
        + np.roll(walls, -1, axis=0)
        + np.roll(walls, 1, axis=1)
        + np.roll(walls, -1, axis=1)
        + np.roll(np.roll(walls, 1, axis=0), 1, axis=1)
        + np.roll(np.roll(walls, 1, axis=0), -1, axis=1)
        + np.roll(np.roll(walls, -1, axis=0), 1, axis=1)
        + np.roll(np.roll(walls, -1, axis=0), -1, axis=1)
    )

    new_tiles = tiles.copy()

    # Apply rule
    new_tiles[neighbor_count > 4] = tile_types.wall
    new_tiles[neighbor_count <= 4] = tile_types.floor

    dungeon.tiles = new_tiles

     # Re-apply solid borders (important because np.roll wraps edges)
    dungeon.tiles[0, :] = tile_types.wall
    dungeon.tiles[-1, :] = tile_types.wall
    dungeon.tiles[:, 0] = tile_types.wall
    dungeon.tiles[:, -1] = tile_types.wall

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

