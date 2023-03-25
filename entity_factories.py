from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
)
orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)
troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=12, base_defense=1, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)
shambler = Actor(
    char="S",
    color=(99, 57, 57),
    name="Shambler",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=15, base_defense=1, base_power=6),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=125),
)
cathu = Actor(
    char="C",
    color=(245, 50, 0),
    name="Cathu",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=20, base_defense=2, base_power=10),
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
berserker_scroll = Item(
    char="~",
    color=(127, 5, 255),
    name="Berserker Scroll",
    consumable=consumable.BerserkerDamageConsumable(damage=30)
)
lamp_strength = Item(
    char="l",
    color=(127, 5, 255),
    name="Lamp of Iris",
    consumable=consumable.LampStrength(amount=1),
)

dagger = Item(
    char="/",
    color=(0, 191, 255),
    name="Dagger",
    equippable=equippable.Dagger()
)

sword = Item(char="/",
             color=(0, 191, 255),
             name="Sword",
             equippable=equippable.Sword())

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[",
    color=(139, 69, 19),
    name="Chain Mail",
    equippable=equippable.ChainMail()
)

plate_mail = Item(
    char="[",
    color=(139, 69, 19),
    name="Plate Mail",
    equippable=equippable.PlateMail()
)
