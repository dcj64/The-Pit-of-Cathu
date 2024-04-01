#!/usr/bin/env python3
import os
import traceback

import tcod

import color
import exceptions
import input_handlers
import setup_game
import config


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


def main() -> None:
    screen_width = config.screen_width  # 80
    screen_height = config.screen_height  # 50

    # map_width = 100
    # map_height = 52

    tileset = tcod.tileset.load_tilesheet(
        "Cheepicus_16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="The Pit of Cathu",
        vsync=True,

    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        try:
            while True:
                context.present(root_console, keep_aspect=True, integer_scaling=True)
                os.environ["SDL_RENDER_SCALE_QUALITY"] = "best"
                os.environ["SDL_RENDER_SCALE_QUALITY"] = "linear"
                root_console.clear()
                handler.on_render(console=root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise


if __name__ == "__main__":
    main()
