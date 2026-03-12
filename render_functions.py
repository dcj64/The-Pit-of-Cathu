from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color
from tcod import libtcodpy

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap


# -------------------------------------------------
# UI Helpers
# -------------------------------------------------

def clamp_text(text: str, max_width: int) -> str:
    if len(text) <= max_width:
        return text
    return text[: max_width - 3] + "..."


def panel_print(console, x, y, text, width=30, align="left", fg=None):

    text = clamp_text(text, width)

    if align == "center":
        text = text.center(width)
    elif align == "right":
        text = text.rjust(width)
    else:
        text = text.ljust(width)

    console.print(x=x, y=y, string=text, fg=fg)


def format_equipment(item) -> str:

    if not item or not item.equippable:
        return "Empty"

    bonuses = []

    if item.equippable.power_bonus:
        bonuses.append(f"+{item.equippable.power_bonus} power")

    if item.equippable.defense_bonus:
        bonuses.append(f"+{item.equippable.defense_bonus} defense")

    if item.equippable.light_bonus:
        bonuses.append(f"+{item.equippable.light_bonus} light")

    if bonuses:
        return f"{item.name} ({', '.join(bonuses)})"

    return item.name


# -------------------------------------------------
# Map Name Display
# -------------------------------------------------

def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:

    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name
        for entity in game_map.entities
        if entity.x == x and entity.y == y
    )

    return names.capitalize()


# -------------------------------------------------
# Consumables Panel
# -------------------------------------------------

def render_consumables_panel(console: Console, engine: Engine, x: int, y: int) -> int:

    panel_print(console, x, y, "*** Consumables ***", align="center", fg=color.bar_text3)
    y += 1

    for key in engine.stats.items_used:

        carried = engine.player.inventory.count_items(key)
        used = engine.stats.items_used[key]

        if carried == 0 and used == 0:
            continue

        name = key.replace("_", " ").title()

        text = f"{name:<18}: {carried} / {used}"
        panel_print(console, x, y, text, fg=color.bar_text)

        y += 1

    return y


# -------------------------------------------------
# Equipment Panel
# -------------------------------------------------

def render_equipment_panel(console, engine, x, y):

    panel_print(console, x, y, "*** Equipment ***", align="center", fg=color.bar_text3)
    y += 1

    equipment = engine.player.equipment

    panel_print(console, x, y, f"Weapon : {format_equipment(equipment.weapon)}", fg=color.bar_text)
    y += 1

    panel_print(console, x, y, f"Armor  : {format_equipment(equipment.armor)}", fg=color.bar_text)
    y += 1

    panel_print(console, x, y, f"Amulet : {format_equipment(equipment.amulet)}", fg=color.bar_text)
    y += 1

    panel_print(console, x, y, f"Ring 1 : {format_equipment(equipment.ring1)}", fg=color.bar_text)
    y += 1

    panel_print(console, x, y, f"Ring 2 : {format_equipment(equipment.ring2)}", fg=color.bar_text)
    y += 2

    panel_print(console, x, y, f"Power Bonus   : +{equipment.power_bonus}", fg=color.bar_text)
    y += 1

    panel_print(console, x, y, f"Defense Bonus : +{equipment.defense_bonus}", fg=color.bar_text)
    y += 1

    panel_print(console, x, y, f"Light Bonus   : +{equipment.light_bonus}", fg=color.bar_text)

    return y


# -------------------------------------------------
# Character / Inventory Panels
# -------------------------------------------------

def render_bar(console: Console, engine: Engine, current_value: int, maximum_value: int, total_width: int) -> None:

    # Character panel
    console.draw_frame(x=1, y=58, width=33, height=22)

    console.print_box(
        x=10,
        y=58,
        width=16,
        height=1,
        string="┤Character(c)├",
        alignment=libtcodpy.CENTER,
    )

    render_character_stats(console, engine, 3, 60)

    # Inventory panel
    console.draw_frame(x=79, y=58, width=39, height=22)

    console.print_box(
        x=83,
        y=58,
        width=35,
        height=1,
        string="┤Inventory(i)├",
        alignment=libtcodpy.CENTER,
    )

    panel_x = 83
    y = 60

    y = render_consumables_panel(console, engine, panel_x, y)
    y += 1
    render_equipment_panel(console, engine, panel_x, y)

    console.print(
    x=4,
    y=72,
    text=f"Gold: {engine.player.gold}",
    fg=(255, 215, 0),
)
    
    console.print(x=5, y=77,
                  string=f"Total Monsters killed:{engine.stats.total_monsters_killed}",
                  fg=(204, 0, 0))

    console.print(x=85, y=76,
                  string=f"Player Moves: {engine.stats.moves_used}")

    # -------------------------------------------------
    # HP BAR (DRAW LAST)
    # -------------------------------------------------

    bar_x = 7
    bar_y = 65
    bar_width_total = 20

    bar_width = int(float(current_value) / maximum_value * bar_width_total)

    # HP label
    console.print(x=4, y=bar_y, string="HP:", fg=color.bar_text)

    # Draw border
    console.print(x=bar_x - 1, y=bar_y, string="[", fg=color.bar_text)
    console.print(x=bar_x + bar_width_total, y=bar_y, string="]", fg=color.bar_text)

    # Empty bar
    console.draw_rect(
        x=bar_x,
        y=bar_y,
        width=bar_width_total,
        height=1,
        ch=ord(" "),
        bg=color.bar_empty,
    )

    # Health percentage
    hp_percent = current_value / maximum_value

    if hp_percent > 0.6:
        bar_color = (0, 200, 0)
    elif hp_percent > 0.3:
        bar_color = (255, 180, 0)
    else:
        bar_color = (200, 0, 0)

    # Filled section
    if bar_width > 0:
        console.draw_rect(
            x=bar_x,
            y=bar_y,
            width=bar_width,
            height=1,
            ch=ord(" "),
            bg=bar_color,
        )

    # HP numbers
    hp_text = f"{current_value}/{maximum_value}"

    console.print(
        x=bar_x + (bar_width_total - len(hp_text)) // 2,
        y=bar_y,
        string=hp_text,
        fg=color.bar_text,
    )

# -------------------------------------------------
# Character Stats
# -------------------------------------------------

def render_character_stats(console, engine, x, y):

    fighter = engine.player.fighter
    equipment = engine.player.equipment

    power_total = fighter.base_power + equipment.power_bonus
    defense_total = fighter.base_defense + equipment.defense_bonus
    light_total = equipment.light_bonus

    panel_print(console, x, y, f"Power   : {power_total}", fg=color.player_atk)
    y += 1

    panel_print(console, x, y, f"Defense : {defense_total}", fg=color.player_def)
    y += 1

    panel_print(console, x, y, f"Light   : {light_total}", fg=color.bar_text)

    return y

# -------------------------------------------------
# Dungeon Level
# -------------------------------------------------

def render_dungeon_level(console: Console, dungeon_level: int, location: Tuple[int, int]) -> None:

    x, y = location
    console.print(x=5, y=75, string=f"Dungeon level: {dungeon_level}")


# -------------------------------------------------
# Mouse Tooltip
# -------------------------------------------------

def render_names_at_mouse_location(
    console: Console,
    engine: Engine,
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names = get_names_at_location(
        x=mouse_x,
        y=mouse_y,
        game_map=engine.game_map,
    )

    if not names:
        return

    # Split names for potential multi-line support
    lines = names.split(", ")
    text_width = max(len(line) for line in lines)

    box_width = text_width + 2
    box_height = len(lines) + 2

    # Position tooltip left or right of hovered tile
    if mouse_x < console.width // 2:
        box_x = mouse_x + 1
    else:
        box_x = mouse_x - box_width - 1

    box_y = mouse_y

    # Clamp horizontally
    if box_x < 0:
        box_x = 0
    if box_x + box_width > console.width:
        box_x = console.width - box_width

    # Clamp vertically
    if box_y + box_height > console.height:
        box_y = console.height - box_height
    if box_y < 0:
        box_y = 0

    # 1 Fill background
    console.draw_rect(
        box_x,
        box_y,
        box_width,
        box_height,
        ch=ord(" "),
        bg=(20, 20, 20),  # Dark tooltip background
    )

    # 2 Draw frame
    console.draw_frame(
        box_x,
        box_y,
        box_width,
        box_height,
        fg=(200, 200, 200),
        bg=None,
    )

    # 3 Print text
    for i, line in enumerate(lines):
        console.print(
            box_x + 1,
            box_y + 1 + i,
            line,
            fg=(255, 255, 255),
        )