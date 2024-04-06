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
    fighter=Fighter(hp=30, base_defense=1, base_power=2, base_light=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
)

orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, base_defense=2, base_power=3, base_light=0),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)
larva = Actor (
    char="w",
    color=(60, 105, 50),
    name="larva",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=1, base_defense=1, base_power=2, base_light=0),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=8),
)
troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=1, base_power=4, base_light=0),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)
shambler = Actor(
    char="S",
    color=(99, 57, 57),
    name="Shambler",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=15, base_defense=1, base_power=6, base_light=0),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=125),
)
cathu = Actor(
    char="C",
    color=(245, 50, 0),
    name="Cathu",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=20, base_defense=2, base_power=10, base_light=0),
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
    color=(204, 0, 204),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)
berserker_scroll = Item(
    char="~",
    color=(204, 0, 204),
    name="Berserker Scroll",
    consumable=consumable.BerserkerDamageConsumable(number_of_turns=5, damage=12),
)
genocide_scroll = Item(
    char="~",
    color=(204, 0, 0),
    name="Genocide Scroll",
    consumable=consumable.GenocideDamageConsumable(damage=40, radius=1),
)
health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
lightning_scroll = Item(
    char="~",
    color=(76, 153, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=15, maximum_range=5),
)
amulet_of_sol = Item(
    # char="l",'☼'
    char=chr(0x263C),
    color=(127, 5, 255),
    name="Amulet of Sol",
    equippable=equippable.Amulets(),
)
ring_of_strength = Item(
    # char="l",'☼'
    char=chr(0x263C),
    color=(127, 5, 255),
    name="Ring of Strength",
    equippable=equippable.Rings(),
)

dagger = Item(
    char="-",
    color=(0, 191, 255),
    name="Dagger",
    equippable=equippable.Dagger()
)

sword = Item(
    char="/",
    color=(0, 191, 255),
    name="Sword",
    equippable=equippable.Sword())

leather_armor = Item(
    # char="'['
    char=chr(0x5B),
    color=(160, 160, 160),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    # char= '¥'
    char=chr(0xA5),
    color=(96, 96, 96),
    name="Chain Mail",
    equippable=equippable.ChainMail()
)
plate_mail = Item(
    # char='≡'
    char=chr(0x2261),
    color=(64, 64, 64),
    name="Plate Mail",
    equippable=equippable.PlateMail()
)


