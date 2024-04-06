from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.ai
import components.inventory
import config
import random
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this item's ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",
            color.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
        )
        config.confusion_scroll_used = config.confusion_scroll_used + 1
        config.confusion_scroll_total = config.confusion_scroll_total - 1
        self.consume()


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            config.health_potion_used = config.health_potion_used + 1
            config.health_potion_total = config.health_potion_total - 1
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")


# class LampStrength(Consumable):
#     def __init__(self, amount: int):
#         self.amount = amount
#
#     def activate(self, action: actions.ItemAction) -> None:
#         if config.lamp_strength == 5:
#             self.engine.message_log.add_message(
#                 f"You are already using the {self.parent.name}!",
#                 color.health_recovered,
#             )
#         if config.lamp_strength < 5:
#             config.lamp_strength = 5
#             self.consume()
#         else:
#             raise Impossible(f"Your lamp is already full.")


class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                config.fireball_scroll_used = config.fireball_scroll_used + 1
                config.fireball_scroll_total = config.fireball_scroll_total - 1
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()


class LightningDamageConsumable(Consumable):
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
                f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            config.lightning_scroll_used = config.lightning_scroll_used + 1
            config.lightning_scroll_total = config.lightning_scroll_total - 1
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")

class GenocideDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target to Genocide!", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot genocide something you cannot see!")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} has been successfully 'genocided', taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                config.genocide_scroll_used = config.genocide_scroll_used + 1
                config.genocide_scroll_total = config.genocide_scroll_total - 1
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()

class BerserkerDamageConsumable(Consumable):
    def __init__(self, number_of_turns: int, damage: int):
        self.number_of_turns = number_of_turns
        self.damage = damage

    def activate(self, action: actions.ItemAction) -> None:
        for actor in self.engine.game_map.actors:
            if actor.fighter.base_power > 1:
                actor.fighter.base_power = actor.fighter.base_power + self.damage
        self.engine.message_log.add_message(
            f"You consume the {self.parent.name},and become a Berserker for the next 5 moves!\n"
            f"Capable of dealing extra damage!\n"
            f"You receive an extra, {self.damage} attack", color.red,
        )
        config.berserker_scroll_used = config.berserker_scroll_used + 1
        config.berserker_scroll_total = config.berserker_scroll_total - 1
        self.consume()
