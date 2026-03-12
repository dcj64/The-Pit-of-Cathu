# wall_autotile.py

""" WALL_TILE_MAP = {
    0: ord("•"),
    1: ord("│"),
    2: ord("│"),
    3: ord("│"),
    4: ord("─"),
    5: ord("┘"),
    6: ord("┐"),
    7: ord("┤"),
    8: ord("─"),
    9: ord("└"),
    10: ord("┌"),
    11: ord("├"),
    12: ord("─"),
    13: ord("┴"),
    14: ord("┬"),
    15: ord("┼"),
} """

WALL_TILE_MAP = {
    0: 145,
    1: 145,
    2: 145,
    3: 145,
    4: 146,
    5: 150,
    6: 148,
    7: 145,
    8: 146,
    9: 149,
    10: 147,
    11: 145,
    12: 146,
    13: 146,
    14: 146,
    15: 151,
}


def get_wall_mask(game_map, x, y):
    mask = 0

    if y > 0 and not game_map.tiles[x, y - 1]["walkable"]:
        mask |= 1

    if y < game_map.height - 1 and not game_map.tiles[x, y + 1]["walkable"]:
        mask |= 2

    if x > 0 and not game_map.tiles[x - 1, y]["walkable"]:
        mask |= 4

    if x < game_map.width - 1 and not game_map.tiles[x + 1, y]["walkable"]:
        mask |= 8

    return mask


def autotile_walls(game_map):

    for x in range(game_map.width):
        for y in range(game_map.height):

            if not game_map.tiles[x, y]["walkable"]:

                mask = get_wall_mask(game_map, x, y)

                char = WALL_TILE_MAP.get(mask, ord("#"))

                game_map.tiles[x, y]["dark"]["ch"] = char
                game_map.tiles[x, y]["light"]["ch"] = char