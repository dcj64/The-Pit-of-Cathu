from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color
import config
from tcod import libtcodpy

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()


def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=5, y=65, width=20, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=5, y=65, width=bar_width, height=1, ch=1, bg=color.bar_filled
       )
        console.print(
            x=4, y=65, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
        )

    console.draw_frame(x=1, y=58, width=30, height=22)  # draw simple box around player info
    console.print_box(x=10, y=58, width=13, height=1, string="┤Character(c)├", alignment=libtcodpy.CENTER)
    console.draw_frame(x=83, y=58, width=35, height=22)
    console.print_box(x=95, y=58, width=13, height=1, string="┤Inventory(i)├", alignment=libtcodpy.CENTER)

    console.print(
        x=5, y=70, string=f"Monsters per level:{config.total_level_monsters}/"
                          f"{config.monsters_on_level_killed}", fg=color.bar_text
    )
    console.print(
        x=5, y=72, string=f"Total Monsters killed:{config.total_monsters_killed}", fg=(204, 0, 0)
    )

    console.print(
        x=5, y=76, string=f"Total Rooms: {config.number_of_rooms}", fg=color.bar_text
    )
    console.print(
        x=96, y=61, string=f"    Inventory/Used", fg=color.bar_text
    )
    console.print(
        x=88, y=62, string=f"Healing Potions :  {config.health_potion_total} / "
                           f"{config.health_potion_used}", fg=color.bar_text
    )
    console.print(
        x=88, y=63, string=f""
    )
    console.print(
        x=88, y=64, string=f" *** Scrolls ***", fg=color.bar_text3  # :  {config.scrolls_total} / "
                           # f"{config.scrolls_used}", fg=color.bar_text
    )
    console.print(
        x=88, y=65, string=f"Lighting Scroll :  {config.lightning_scroll_total} / "
                           f"{config.lightning_scroll_used}", fg=color.bar_text
    )
    console.print(
        x=88, y=66, string=f"Confusion Scroll:  {config.confusion_scroll_total} / "
                           f"{config.confusion_scroll_used}", fg=color.bar_text
    )
    console.print(
        x=88, y=67, string=f"Fireball Scroll :  {config.fireball_scroll_total} / "
                           f"{config.fireball_scroll_used}", fg=color.bar_text
    )
    console.print(
        x=88, y=68, string=f"Berserker Scroll:  {config.berserker_scroll_total} / "
                           f"{config.berserker_scroll_used}", fg=color.bar_text
    )
    console.print(
        x=88, y=69, string=f"Genocide Scroll :  {config.genocide_scroll_total} / "
                           f"{config.genocide_scroll_used}", fg=color.bar_text2
    )
    console.print(  # testing how to print char to screen
        x=88, y=71, string=f" ** Equipment ** ", fg=color.bar_text3
    )
    console.print(
        x=88, y=72, string=f"Amulets :  {config.amulets_total} ", fg=color.bar_text
    )
    console.print(
        x=88, y=73, string=f"Rings   :  {config.rings_total} ", fg=color.bar_text
    )

    console.print(  # testing how to print char to screen
        x=85, y=76, string=f"Player Moves: {config.moves_used} "
    )


def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=5, y=62, string=f"Dungeon level: {dungeon_level}")


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)
