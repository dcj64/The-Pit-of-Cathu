from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    inventory=Inventory(capacity=26),
)

orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
    inventory=Inventory(capacity=0),
)

troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=12, defense=1, power=4),
    inventory=Inventory(capacity=0),
)
shambler = Actor(
    char="S",
    color=(99, 57, 57),
    name="Shambler",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=15, defense=1, power=6),
    inventory=Inventory(capacity=0),
)
cathu = Actor(
    char="C",
    color=(245, 50, 0),
    name="Cathu",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=20, defense=2, power=10),
    inventory=Inventory(capacity=0),
)

health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
lightning_scroll = Item(
    char="~",
    color=(127, 5, 255),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)


