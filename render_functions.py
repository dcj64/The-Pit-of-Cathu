from __future__ import annotations

from typing import TYPE_CHECKING

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
        x=1, y=57, string=f"Total monsters: {config.total_monsters}/"
                          f"{config.total_monsters - config.monsters_killed}", fg=color.bar_text
    )
    console.print(
        x=1, y=58, string=f"Monsters killed: {config.monsters_killed}", fg=(204, 0, 0)
    )

    console.draw_rect(x=1, y=54, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=1, y=54, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )
        console.print(
            x=1, y=54, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
        )


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)
