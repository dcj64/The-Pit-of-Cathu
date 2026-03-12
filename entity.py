from __future__ import annotations

import math
import random
import copy

from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder


if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.equippable import Equippable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from components.level import Level
    from game_map import GameMap
    
T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # If gamemap isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Entity x set to non-int: {value}")
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Entity y set to non-int: {value}")
        self._y = value

class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory,
        level: Level,       
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self
        
        self.gold:int = 0

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Optional[Consumable] = None,
        equippable: Optional[Equippable] = None,
        gold_value: int = 0,
        spawn_min: int = 0,
        spawn_max: int = 999,
        spawn_weight: int = 1,
        spawn_rooms: Optional[list] = None,  # A list of room types this item can spawn in
        
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )
        
        self.consumable = consumable
        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self
            
        self.gold_value = gold_value
        # Add the spawn attributes
        self.spawn_min = spawn_min
        self.spawn_max = spawn_max
        self.spawn_weight = spawn_weight
        self.spawn_rooms = spawn_rooms or []  # Default to an empty list if not provided
        
def spawn_treasure(engine, x, y):

    from procgen.entities import get_items_for_floor

    floor = engine.game_world.current_floor
    items = get_items_for_floor(floor, 3, "treasure")

    for item in items:

        for _ in range(20):  # try 20 positions
            spawn_x = x + random.randint(-2, 2)
            spawn_y = y + random.randint(-2, 2)

            # Must be inside map
            if not engine.game_map.in_bounds(spawn_x, spawn_y):
                continue

            # Must be walkable
            if not engine.game_map.tiles["walkable"][spawn_x, spawn_y]:
                continue
            
            # Must not be inside the chest
            if spawn_x == x and spawn_y == y:
                continue

            # Must not already contain entity
            if any(e.x == spawn_x and e.y == spawn_y for e in engine.game_map.entities):
                continue

            spawn_item = copy.deepcopy(item)
            spawn_item.spawn(engine.game_map, spawn_x, spawn_y)
            break
                 
class Chest(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(
            x=x,
            y=y,
            char="C",
            color=(184, 134, 11),
            name="Treasure Chest",
            blocks_movement=True,
            render_order=RenderOrder.ITEM,   # ← ADD THIS
        )
        self.opened = False

    def open(self, engine):

        if self.opened:
            engine.message_log.add_message("The chest is empty. It has already been looted.")
            return

        engine.message_log.add_message("You open the treasure chest!")

        spawn_treasure(engine, self.x, self.y)

        self.opened = True
        self.char = "o"
        