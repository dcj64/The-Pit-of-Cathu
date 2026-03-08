from __future__ import annotations

import lzma
import pickle
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov
from render_functions import get_names_at_location

from typing import Tuple
from game_stats import GameStats

import tcod

import config
import exceptions
from message_log import MessageLog
import render_functions

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location: Tuple[int, int] = (0, 0)
        self.player = player
        self.context: tcod.context.Context
        self.stats = GameStats()

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=config.lamp_strength + self.player.equipment.light_bonus,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        mx, my = self.mouse_location
        names = get_names_at_location(mx, my, self.game_map)
        
        if names:
            bg = console.rgb["bg"][mx, my]
            console.rgb["bg"][mx, my] = (bg + (30, 30, 30)).clip(0, 255)
        
        self.message_log.render(console=console, x=38, y=58, width=43, height=5)  # x=25 y=45

        render_functions.render_bar(
            console=console,
            engine=self,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(5, 62),
        )

        render_functions.render_names_at_mouse_location(
            console=console,
            engine=self
        )

    def __getstate__(self):
        state = self.__dict__.copy()

        # Remove unpickleable tcod context
        state["context"] = None

        return state

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)
