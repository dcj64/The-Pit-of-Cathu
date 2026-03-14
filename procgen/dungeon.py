from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, List, Tuple
import random
import tcod
from entity import Chest
from game_map import GameMap
from data_loader import TRAPS
import tile_types

if TYPE_CHECKING:
    from engine import Engine

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int, room_type: str = "normal"):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height
        self.room_type = room_type
        self.visited = False

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
        return (
                self.x1 <= other.x2
                and self.x2 >= other.x1
                and self.y1 <= other.y2
                and self.y2 >= other.y1
        )

def choose_room_type():

    room_types = [
        ("normal", 60),
        ("treasure", 10),
        ("nest", 10),
        ("collapsed", 10),
        ("shrine", 10),
    ]

    types = [t for t, w in room_types]
    weights = [w for t, w in room_types]

    return random.choices(types, weights=weights, k=1)[0]

def decorate_room(room_type, room, dungeon):

    if room_type == "treasure":
        import random
        # Find a random valid tile inside the room
        while True:
            cx = random.randint(room.x1 + 1, room.x2 - 1)
            cy = random.randint(room.y1 + 1, room.y2 - 1)

            if not dungeon.tiles["walkable"][cx, cy]:
                continue

            # Don't place on another entity
            if any(e.x == cx and e.y == cy for e in dungeon.entities):
                continue

            break

        # Ensure tile is floor
        dungeon.tiles["walkable"][cx, cy] = True
        dungeon.tiles["transparent"][cx, cy] = True
        dungeon.tiles["dark"][cx, cy] = tile_types.floor["dark"]
        dungeon.tiles["light"][cx, cy] = tile_types.floor["light"]

        chest = Chest(cx, cy)
        chest.spawn(dungeon, cx, cy)

    elif room_type == "nest":
        import random
        # Add some dirt / organic patches
        for _ in range(random.randint(3, 6)):
            rx = random.randint(room.x1 + 1, room.x2 - 1)
            ry = random.randint(room.y1 + 1, room.y2 - 1)

            dungeon.tiles[rx, ry] = tile_types.floor


    elif room_type == "collapsed":

        # Scatter rubble across the room
        import random
        for _ in range(random.randint(5, 12)):
            rx = random.randint(room.x1 + 1, room.x2 - 1)
            ry = random.randint(room.y1 + 1, room.y2 - 1)

            # Don't block the center so the room stays reachable
            if (rx, ry) == room.center:
                continue

            dungeon.tiles[rx, ry] = tile_types.wall

    elif room_type == "shrine":

        cx, cy = room.center
        dungeon.tiles[cx, cy] = tile_types.floor


def randomize_walls(dungeon: GameMap):

    wall_variants = [
        tile_types.wall,
        tile_types.wall_cracked,
        tile_types.wall_mossy,
        tile_types.wall_broken,
    ]

    weights = [80, 5, 10, 5]

    for x in range(1, dungeon.width - 1):
        for y in range(1, dungeon.height - 1):

            # Only affect wall tiles
            if dungeon.tiles["walkable"][x, y]:
                continue

            # Check if this wall touches a floor
            neighbors = [
                dungeon.tiles["walkable"][x - 1, y],
                dungeon.tiles["walkable"][x + 1, y],
                dungeon.tiles["walkable"][x, y - 1],
                dungeon.tiles["walkable"][x, y + 1],
            ]

            if any(neighbors):

                dungeon.tiles[x, y] = random.choices(
                    wall_variants,
                    weights=weights,
                    k=1
                )[0]

def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    from procgen.entities import place_entities

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

    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # Create room type
        # Temporary room for intersection check
        test_room = RectangularRoom(x, y, room_width, room_height)

        if any(test_room.intersects(other_room) for other_room in rooms):
            continue

        room_type = "normal" if len(rooms) == 0 else choose_room_type()

        new_room = RectangularRoom(x, y, room_width, room_height, room_type)

        dungeon.tiles[new_room.inner] = tile_types.floor

        # FIRST ROOM
        if len(rooms) == 0:
            player.place(*new_room.center, dungeon)

        # ALL OTHER ROOMS
        else:
            # Dig tunnels
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
            
            # NOW decorate the room
            decorate_room(room_type, new_room, dungeon)
            
            # Spawn monsters and items
            place_entities(new_room, dungeon, engine.game_world.current_floor)
                       
        # Add room to dungeon
        rooms.append(new_room)
    
    # After generation finishes
    if rooms:
        # Place stairs
        stairs_x, stairs_y = rooms[-1].center
        dungeon.tiles[stairs_x, stairs_y] = tile_types.down_stairs
        dungeon.downstairs_location = (stairs_x, stairs_y)
    
    # after generation is complete   
    dungeon.rooms = rooms
        
    randomize_walls(dungeon)

    add_simple_doors(dungeon)
    
    return dungeon

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

            if touches_room and random.random() < 0.1:  # 10% chance to place a door
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


