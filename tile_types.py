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
        ("name", "U20"),  # up to 20 character string
        ("bump_text", "U200"), # up to 200 character string
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    name: str,
    bump_text: str,
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light, name, bump_text), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (31, 44, 51)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("."), (80, 80, 120), (0, 0, 0)),
    light=(ord("."), (140, 140, 200), (0, 0, 0)),
    name="floor",
    bump_text="",
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (255, 255, 255), (0, 0, 100)),
    light=(ord("#"), (255, 255, 255), (130, 110, 50)),
    name="stone wall",
    bump_text="You bump into a solid stone wall.|"
    "You bump into unforgiving stone.|"
    "The stone wall feels cold to the touch."
)

ruin_wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("▓"), (60, 60, 60), (0, 0, 0)),
    light=(ord("▓"), (170, 170, 170), (40, 40, 40)),
    name="ruined wall",
    bump_text="The wall feels aged and broken.|"
    "There is no way through this ruined wall."
)

wall_cracked = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (70, 70, 70), (0, 0, 0)),
    light=(ord("#"), (110, 110, 110), (0, 0, 0)),
    name="cracked wall",
    bump_text="The cracked wall crumbles slightly under your touch."
)

wall_mossy = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (40, 80, 40), (0, 0, 0)),
    light=(ord("#"), (60, 120, 60), (0, 0, 0)),
    name="mossy wall",
    bump_text="Your hand brushes against damp moss.|"
    "The mossy wall feels cold.|"
    "Moisture drips from the mossy stone." 
)

wall_broken = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (90, 90, 90), (0, 0, 0)),
    light=(ord("#"), (140, 140, 140), (0, 0, 0)),
    name="broken wall",
    bump_text="Loose stones rattle in the broken wall."
)

down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (141, 182, 0)),
    light=(ord(">"), (255, 255, 255), (141, 182, 0)),
    name="stairs",
    bump_text="You step onto the stairs."
)

door_closed = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("+"), (120, 90, 40), (0, 0, 0)),
    light=(ord("+"), (200, 170, 80), (0, 0, 0)),
    name="closed door",
    bump_text="The door opens easily."
)

door_open = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("/"), (120, 90, 40), (0, 0, 0)),
    light=(ord("/"), (200, 170, 80), (0, 0, 0)),
    name="opened door.",
    bump_text=""
)

water = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord("≈"), (0, 0, 100), (0, 0, 40)),
    light=(ord("≈"), (0, 100, 255), (0, 0, 80)),
    name="water",
    bump_text="The water is to deep to cross."
)

lava = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord("^"), (120, 0, 0), (40, 0, 0)),
    light=(ord("^"), (255, 140, 0), (120, 20, 0)),
    name="lava",
    bump_text="The lava burns you!|"
    "You can feel the heat from the lava!"
)

hole = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord("░"), (0, 0, 0), (36, 36, 36)),
    light=(ord("░"), (0, 0, 0), (36, 36, 36)),
    name="hole",
    bump_text="You nervously peer into the hole."
)

tree = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("♣"), (49, 85, 23), (0, 0, 0)),
    light=(ord("♣"), (60, 120, 60), (0, 0, 0)),
    name="tree",
    bump_text="You bump into the tree."
)

