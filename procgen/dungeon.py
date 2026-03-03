from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, List, Tuple
import random
import tcod
import config

from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine



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


