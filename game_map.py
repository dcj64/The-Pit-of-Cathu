from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

from data_loader import BIOMES


if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
            self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width = width
        self.height = height
        self.entities = set(entities)
        # --- Level-specific runtime state ---
        self.number_of_rooms = 0
        self.total_monsters = 0
        self.monsters_killed = 0
        # --- End level-specific runtime state ---
        self.tiles = np.full((self.width, self.height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full((width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before
        self.rooms = []

        self.downstairs_location: tuple[int, int] = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over these maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                    entity.blocks_movement
                    and entity.x == location_x
                    and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb [0: self.width, 0: self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Hide traps until revealed
            if entity.trap and not entity.trap.revealed:
                continue
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x,
                    y=entity.y,
                    text=entity.char,
                    fg=entity.color
                )
    
    def get_room_at_location(self, x, y):
        for room in self.rooms:
            if room.x1 <= x <= room.x2 and room.y1 <= y <= room.y2:
                return room
        return None


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0
    ):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.current_floor = current_floor

    def get_biome_for_floor(self,floor):

        for name, biome in BIOMES.items():

            start, end = biome["floors"]

            if start <= floor <= end:
                return name, biome

        return "ruins", BIOMES["ruins"]

    def generate_floor(self) -> None:

        from procgen import generate_dungeon, generate_cave

        self.current_floor += 1

        biome_name, biome = self.get_biome_for_floor(self.current_floor)

        generator = biome["generator"]

        if generator == "dungeon":

            self.engine.game_map = generate_dungeon(
                max_rooms=self.max_rooms,
                room_min_size=self.room_min_size,
                room_max_size=self.room_max_size,
                map_width=self.map_width,
                map_height=self.map_height,
                engine=self.engine,
            )
            self.engine.message_log.add_message(
            f"You enter the {biome_name} system."
        )


        elif generator == "cave":

            self.engine.game_map = generate_cave(
                map_width=self.map_width,
                map_height=self.map_height,
                engine=self.engine,
                floor_number=self.current_floor,         
            )

            self.engine.message_log.add_message(
            f"You enter the subterranean {biome_name} system."
        )    
