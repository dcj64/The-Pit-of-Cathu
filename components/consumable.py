from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai

from typing import cast
from components.inventory import Inventory
from stats_keys import ItemStat

from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

from entity import Item

if TYPE_CHECKING:
    from entity import Actor


class Consumable(BaseComponent[Item]):
    stat_key: str | None = None

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity

        # Run the item's effect
        self.apply_effect(consumer)

        # Update stats
        if self.stat_key:
            self.engine.stats.items_used[self.stat_key] += 1

        # Remove the item
        self.consume()

    def apply_effect(self, consumer: Actor) -> None:
        raise NotImplementedError()

    def consume(self) -> None:
        item = self.parent
        container = item.parent

        if isinstance(container, Inventory) and item in container.items:
            container.items.remove(item)
        

# ---------------------------------------------------------------------
# SELF TARGET ITEMS (potions etc)
# ---------------------------------------------------------------------

class HealingConsumable(Consumable):

    stat_key = ItemStat.HEALTH_POTION

    def __init__(self, amount: int):
        self.amount = amount

    def apply_effect(self, consumer: Actor) -> None:
        recovered = consumer.fighter.heal(self.amount)

        if recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name} and recover {recovered} HP!",
                color.health_recovered,
            )
        else:
            raise Impossible("Your health is already full.")


class BerserkerDamageConsumable(Consumable):

    stat_key = "berserker_scroll"

    def __init__(self, turns: int, damage: int):
        self.turns = turns
        self.damage = damage

    def apply_effect(self, consumer: Actor) -> None:
        for actor in self.engine.game_map.actors:
            if actor.fighter.base_power > 1:
                actor.fighter.base_power += self.damage

            if self.stat_key:
                self.engine.stats.items_used[self.stat_key] += 1              

        self.engine.message_log.add_message(
            f"You become a Berserker for {self.turns} turns, gaining {self.damage} extra damage!",
            color.red,
        )


# ---------------------------------------------------------------------
# SINGLE TARGET ITEMS
# ---------------------------------------------------------------------

class TargetConsumable(Consumable):

    stat_key: str | None = None

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target.", color.needs_target
        )

        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )


class ConfusionConsumable(TargetConsumable):

    stat_key = "confusion_scroll"

    def __init__(self, turns: int):
        self.turns = turns

    def activate(self, action: actions.ItemAction) -> None:

        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target something you cannot see.")

        if not target:
            raise Impossible("You must select an enemy.")

        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        target.ai = components.ai.ConfusedEnemy(
            entity=target,
            previous_ai=target.ai,
            turns_remaining=self.turns,
        )

        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant as it starts to stumble!",
            color.status_effect_applied,
        )

        if self.stat_key:
            self.engine.stats.items_used[self.stat_key] += 1

class LightningDamageConsumable(Consumable):

    stat_key = "lightning_scroll"

    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:

        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:

            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:

                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:

            self.engine.message_log.add_message(
                f"A lightning bolt strikes the {target.name} for {self.damage} damage!"
            )

            target.fighter.take_damage(self.damage)

            if self.stat_key:
                self.engine.stats.items_used[self.stat_key] += 1

        else:
            raise Impossible("No enemy is close enough to strike.")


# ---------------------------------------------------------------------
# AREA EFFECT ITEMS
# ---------------------------------------------------------------------

class AreaConsumable(Consumable):

    stat_key: str | None = None
    radius: int

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:

        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )

        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )


class FireballDamageConsumable(AreaConsumable):

    stat_key = "fireball_scroll"

    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def activate(self, action: actions.ItemAction) -> None:

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an unseen area.")

        targets_hit = False

        for actor in self.engine.game_map.actors:

            if actor.distance(*action.target_xy) <= self.radius:

                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in flames, taking {self.damage} damage!"
                )

                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")

        if self.stat_key:
            self.engine.stats.items_used[self.stat_key] += 1

class GenocideDamageConsumable(AreaConsumable):

    stat_key = "genocide_scroll"

    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def activate(self, action: actions.ItemAction) -> None:

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot genocide something you cannot see!")

        targets_hit = False

        for actor in self.engine.game_map.actors:

            if actor.distance(*action.target_xy) <= self.radius:

                self.engine.message_log.add_message(
                    f"The {actor.name} has been annihilated!"
                )
                
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")

        if self.stat_key:
            self.engine.stats.items_used[self.stat_key] += 1
        