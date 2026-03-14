import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity


class Trap:
    parent: "Entity"

    def __init__(self, damage_min, damage_max, reveal_chance=0.5, one_time=True):
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.reveal_chance = reveal_chance
        self.one_time = one_time
        self.revealed = False

    def trigger(self, target):
        damage = random.randint(self.damage_min, self.damage_max)

        engine = target.gamemap.engine

        engine.message_log.add_message(
            f"You trigger a {self.parent.name}! ({damage} damage)"
        )

        target.fighter.take_damage(damage)

        self.revealed = True

        if self.one_time:
            target.gamemap.entities.remove(self.parent)