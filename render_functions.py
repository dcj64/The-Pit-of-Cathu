from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color
import config

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

    console.print(
        x=1, y=56, string=f"Total Rooms: {config.number_of_rooms}", fg=color.bar_text
    )
    console.print(
        x=1, y=58, string=f"Monsters per level:{config.total_level_monsters}/"
        f"{config.monsters_on_level_killed}", fg=color.bar_text
    )
    console.print(
        x=1, y=59, string=f"Total Monsters killed:{config.total_monsters_killed}", fg=(204, 0, 0)
    )
    console.print(
        x=65, y=53, string=f"*** To use items Press (i) ***", fg=color.bar_text
    )
    console.print(
        x=80, y=54, string=f"   Inventory/Used", fg=color.bar_text
    )
    console.print(
        x=70, y=55, string=f"Healing Potions:  {config.health_potion_total} / "
        f"{config.health_potion_used}", fg=color.bar_text
    )
    console.print(
        x=70, y=56, string=f"Scrolls        :  {config.scrolls_total} / "
        f"{config.scrolls_used}", fg=color.bar_text
    )
    console.print(
        x=65, y=58, string=f"Player moves so far:  {config.moves_used}", fg=color.bar_text
    )

    console.draw_rect(x=1, y=53, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=1, y=53, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )
        console.print(
            x=1, y=53, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
        )


def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)
