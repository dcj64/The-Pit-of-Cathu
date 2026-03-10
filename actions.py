from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from room_data import ROOM_DESCRIPTIONS
from entity import Chest

import color
import exceptions
import time

import numpy as np

import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item, Chest


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)
                
                self.engine.message_log.add_message(
                    f"You picked up the {item.name}.",
                    (255, 255, 0),
                )

                # Track consumables
                key = getattr(item.consumable, "stat_key", None)
                if key:
                    self.engine.stats.item_found(key)

                # Track equipment
                eq_key = getattr(item.equippable, "stat_key", None)
                if eq_key:
                    self.engine.stats.equipment_found_item(eq_key)

                # Track equipment
                elif item.equippable:
                    if "Amulet" in item.name:
                        self.engine.stats.equipment_found_item("amulet")
                    elif "Ring" in item.name:
                        self.engine.stats.equipment_found_item("ring")

                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
            self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the item's ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_map.monsters_killed = 0
            self.engine.message_log.add_message(
                "You cautiously descend the staircase.", color.descend
            )
            self.engine.game_world.generate_floor()
            time.sleep(1.5)
        #  if ((self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location) \
            #  and (config.total_monsters != config.monsters_killed):
            #  raise exceptions.Impossible("The stairs are locked. There are still monsters to kill!")
        else:
            raise exceptions.Impossible("There are no stairs here.")


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this action's destination."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
        game_map = self.engine.game_map

        if not game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")

        tile = game_map.tiles[dest_x, dest_y]

        # If it's a closed door, open it instead of blocking
        if np.array_equal(tile, tile_types.door_closed):
            game_map.tiles[dest_x, dest_y] = tile_types.door_open
            self.engine.message_log.add_message("You open the door.")
            return  # Opening door takes a turn
        
        # Open chest
        for entity in game_map.entities:
            if entity.x == dest_x and entity.y == dest_y:
                if isinstance(entity, Chest):
                    entity.open(self.engine)
                    return

        # Blocked by tile
        if not game_map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.Impossible("That way is blocked.")

        # Blocked by entity
        if game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")
        
        """ # Open chest
        for entity in game_map.entities:
            if entity.x == dest_x and entity.y == dest_y:
                if isinstance(entity, Chest):
                    entity.open(self.engine)
                    return """
        """ target = game_map.get_blocking_entity_at_location(dest_x, dest_y)
        if isinstance(target, Chest):
            target.open(self.engine)
            return """

        self.entity.move(self.dx, self.dy)
        
        player = self.entity
        
        for room in self.engine.game_map.rooms:

            if room.x1 <= player.x <= room.x2 and room.y1 <= player.y <= room.y2:

                if not room.visited:

                    room.visited = True

                    if room.room_type in ROOM_DESCRIPTIONS:

                        self.engine.message_log.add_message(
                            ROOM_DESCRIPTIONS[room.room_type]
                        )
class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
