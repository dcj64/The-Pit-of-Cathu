import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity
    
class Trap:
    parent: "Entity"

    def __init__(
        self,
        damage_min,
        damage_max,
        reveal_chance=0.5,
        one_time=True,
        
    ):
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.reveal_chance = reveal_chance
        self.one_time = one_time
        self.revealed = False

    def trigger(self, target):

        damage = random.randint(self.damage_min, self.damage_max)

        engine = target.gamemap.engine

        self.revealed = True

        if target is engine.player:
            engine.message_log.add_message(
                f"You trigger the {self.parent.name}! ({damage} damage)"
            )
        else:
            engine.message_log.add_message(
                f"The {target.name} triggers the {self.parent.name}! ({damage} damage)"
            )
            
        # New flavour message if enemy dies on trap
        if not target.is_alive and target is not engine.player:
            engine.message_log.add_message(
                f"The {target.name} is impaled by a spike trap!"
            )

        target.fighter.take_damage(damage)

        if self.one_time:
            self.parent.char = "-"
            self.parent.color = (120,120,120)
            self.parent.name = "Triggered Trap"
            self.parent.trap = None