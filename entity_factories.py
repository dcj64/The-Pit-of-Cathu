from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
)
orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)
troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=12, defense=1, power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)
shambler = Actor(
    char="S",
    color=(99, 57, 57),
    name="Shambler",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=15, defense=1, power=6),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=125),
)
cathu = Actor(
    char="C",
    color=(245, 50, 0),
    name="Cathu",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=20, defense=2, power=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=150),
)
confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
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
lamp_strength = Item(
    char="l",
    color=(127, 5, 255),
    name="Lamp of Iris",
    consumable=consumable.LampStrength(amount=1),
)
