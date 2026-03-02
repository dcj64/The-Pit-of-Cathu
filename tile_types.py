from typing import Tuple

import numpy as np  # type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),  # True if this tile can be walked over.
        ("transparent", bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (31, 44, 51)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("."), (80, 80, 120), (0, 0, 0)),
    light=(ord("."), (140, 140, 200), (0, 0, 0)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (255, 255, 255), (0, 0, 100)),
    light=(ord("#"), (255, 255, 255), (130, 110, 50)),
)

ruin_wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("▓"), (60, 60, 60), (0, 0, 0)),
    light=(ord("▓"), (170, 170, 170), (40, 40, 40)),
)

down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (141, 182, 0)),
    light=(ord(">"), (255, 255, 255), (141, 182, 0)),
)

door_closed = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("+"), (120, 90, 40), (0, 0, 0)),
    light=(ord("+"), (200, 170, 80), (0, 0, 0)),
)

door_open = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("/"), (120, 90, 40), (0, 0, 0)),
    light=(ord("/"), (200, 170, 80), (0, 0, 0)),
)

water = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord("≈"), (0, 0, 100), (0, 0, 40)),
    light=(ord("≈"), (0, 100, 255), (0, 0, 80)),
)

lava = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord("^"), (120, 0, 0), (40, 0, 0)),
    light=(ord("^"), (255, 140, 0), (120, 20, 0)),
)

