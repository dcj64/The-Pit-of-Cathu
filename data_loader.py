import json
import os

from components.consumable import (
    HealingConsumable,
    FireballDamageConsumable,
    LightningDamageConsumable,
    ConfusionConsumable,
    BerserkerDamageConsumable,
    GenocideDamageConsumable,
)

from components.equipment import Equipment
from components.inventory import Inventory
from components.fighter import Fighter
from components.ai import HostileEnemy

from components.equippable import Equippable
from equipment_types import EquipmentType

from components.level import Level
from components.trap import Trap

from entity import Actor, Item, Entity
from render_order import RenderOrder


DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")


# ---------------------------------------------------
# Generic JSON Loader
# ---------------------------------------------------

def load_json(filename):
    path = os.path.join(DATA_FOLDER, filename)

    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------
# ITEM LOADING
# ---------------------------------------------------

def load_items():
    raw_items = load_json("items.json")

    items = {}

    for data in raw_items:
        items[data["name"]] = build_item(data)

    return items


def build_item(data):

    consumable = None
    equippable = None

    item_type = data["type"]

    # Consumables
    if item_type == "healing":
        consumable = HealingConsumable(data["amount"])

    elif item_type == "fireball":
        consumable = FireballDamageConsumable(
            damage=data["damage"],
            radius=data["radius"],
        )

    elif item_type == "lightning":
        consumable = LightningDamageConsumable(
            damage=data["damage"],
            maximum_range=data["range"],
        )

    elif item_type == "confusion":
        consumable = ConfusionConsumable(
            turns=data["turns"],
        )
    elif item_type == "berserker":
        consumable = BerserkerDamageConsumable(
            turns=data["turns"],
            damage=data["damage"],
        )

    elif item_type == "genocide":
        consumable = GenocideDamageConsumable(
            radius=data["radius"],
            damage=data["damage"],
        )
        
    # Equipment
    elif item_type == "weapon":
        equippable = Equippable(
            equipment_type=EquipmentType.WEAPON,
            power_bonus=data.get("power_bonus", 0),
        )

    elif item_type == "armor":
        equippable = Equippable(
            equipment_type=EquipmentType.ARMOR,
            defense_bonus=data.get("defense_bonus", 0),
        )

    elif item_type == "ring":
        equippable = Equippable(
            equipment_type=EquipmentType.RING,
            power_bonus=data.get("power_bonus", 0),
        )

    elif item_type == "amulet":
        equippable = Equippable(
            equipment_type=EquipmentType.AMULET,
            light_bonus=data.get("light_bonus", 0),
        )

    elif item_type == "gold":
        # Gold is not consumable or equippable
        pass

    else:
        raise ValueError(f"Unknown item type: {item_type}")

    item = Item(
        char=data["char"],
        color=tuple(data["color"]),
        name=data["name"],
        stats=data.get("stats", {}),
        consumable=consumable,
        equippable=equippable,
        gold_value=int(data.get("value", 0)),
        spawn_min = data.get("spawn_min", 0),
        spawn_max = data.get("spawn_max", 999),
        spawn_weight = data.get("spawn_weight", 1),
        spawn_rooms = data.get("spawn_rooms", [])
    )    
    return item


# ---------------------------------------------------
# MONSTER LOADING
# ---------------------------------------------------

def load_monsters():
    raw_monsters = load_json("monsters.json")

    monsters = {}

    for data in raw_monsters:
        monsters[data["name"]] = build_monster(data)

    return monsters


def build_monster(data):

    fighter = Fighter(
        hp=data["hp"],
        base_defense=data["defense"],
        base_power=data["power"],
        base_light=data.get("light", 0),
    )

    monster = Actor(
        char=data["char"],
        color=tuple(data["color"]),
        name=data["name"],
        ai_cls=HostileEnemy,
        fighter=fighter,
        inventory=Inventory(capacity=0),
        equipment=Equipment(),
        level=Level(xp_given=data.get("xp", 0)),
    )

    monster.spawn_min = data.get("spawn_min", 1)
    monster.spawn_max = data.get("spawn_max", 999)
    monster.rarity = data.get("rarity", 50)

    monster.group_min = data.get("group_min", 1)
    monster.group_max = data.get("group_max", 1)

    return monster

# ---------------------------------------------------
# TRAP LOADING
# ---------------------------------------------------

def load_traps():
    raw_traps = load_json("traps.json")
    

    traps = {}

    for data in raw_traps:
        traps[data["name"]] = build_trap(data)

    return traps


def build_trap(data):

    trap_component = Trap(
        damage_min=data["damage_min"],
        damage_max=data["damage_max"],
        reveal_chance=data.get("reveal_chance", 0.5),
        one_time=data.get("one_time", True),
    )

    trap = Entity(
        char=data["char"],
        color=tuple(data["color"]),
        name=data["name"],
        blocks_movement=False,
        render_order=RenderOrder.TRAP,
        trap=trap_component,
        xp=data.get("xp, 5")
    )

    trap.spawn_min = data.get("spawn_min", 1)
    trap.spawn_max = data.get("spawn_max", 999)
    trap.rarity = data.get("rarity", 50)
    
    # XP reward for disarming
    trap.xp = data.get("xp", 5)

    return trap


def load_biomes():
    path = os.path.join(os.path.dirname(__file__), "data/biomes.json")

    with open(path) as f:
        return json.load(f)
    

ITEMS = load_items()
MONSTERS = load_monsters()
TRAPS = load_traps()
BIOMES = load_biomes()