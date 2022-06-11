"""Downscale an image to desired file size."""
import pathlib
import sys
import platform

import click

import downscale_image

_ON_WINDOWS = platform.system().lower() == "windows"

if _ON_WINDOWS:
    from downscale_image import _registry_utils


@click.command()
@click.option(
    "--max-size",
    default=2,
    help="Max output size (in MB)",
    type=click.IntRange(min=0, min_open=True),
    show_default=True,
)
@click.option(
    "--add-to-right-click-menu",
    help="(Windows only) Register this program in right click menu for supported file types.",
    is_flag=True,
    default=False,
)
@click.argument("in_file", type=click.Path(exists=True, dir_okay=False))
def main(max_size, in_file, add_to_right_click_menu: bool):
    """Downscale in_file to desired max-size."""
    if add_to_right_click_menu:
        if not _ON_WINDOWS:
            raise Exception("Error, registry right click menus are only support on Windows.")
        exe = pathlib.Path(sys.argv[0])
        args = ['"%*"']
        _registry_utils.register_downscale_commands(str(exe), args)

    in_file = pathlib.Path(in_file)

    print(f"Downscaling {in_file}...")
    try:
        downscale_image.downscale(in_file, max_mega_bytes=max_size)
        print(f"Finished")
    except Exception as e:
        print("An error occured", file=sys.stderr)
        print(e, file=sys.stderr)
        print("")
        print("")
        input("Press enter to continue...")
        click.Abort(e)


if __name__ == "__main__":  # pragma: no cover
    main()
