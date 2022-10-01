"""Downscale an image to desired file size."""
import pathlib
import sys
import platform

import click
import pathspec

import downscale_image

_ON_WINDOWS = platform.system().lower() == "windows"

if _ON_WINDOWS:
    from downscale_image import _registry_utils

_DEFAULT_MATCHES = ["!.venv/", "!.git/", "!objects/"] + [f"*{ext}" for ext in downscale_image.SUPPORTED_FILE_EXTENSIONS]

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
@click.argument("in_file", metavar="FILE_OR_DIRECTORY", type=click.Path(exists=True, dir_okay=True))
def main(max_size, in_file, add_to_right_click_menu: bool):
    """Downscale file_or_directory to desired max-size."""
    if add_to_right_click_menu:
        if not _ON_WINDOWS:
            raise Exception("Error, registry right click menus are only support on Windows.")
        exe = pathlib.Path(sys.argv[0])
        args = ['"%1"']
        _registry_utils.register_downscale_commands(str(exe), args)

    in_file = pathlib.Path(in_file)

    files_to_prcoess = []

    if in_file.is_dir():
        spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, _DEFAULT_MATCHES)
        files_to_prcoess = [pathlib.Path(p) for p in spec.match_tree(in_file)]
    else:
        files_to_prcoess = [in_file]

    fail_count = 0
    for file in files_to_prcoess:
        print(f"Downscaling {file}...")
        try:
            downscale_image.downscale(file, max_mega_bytes=max_size)
            print(f"Finished")
        except Exception as e:
            fail_count += 1
            if fail_count > 5:
                print("Several errors have occured, stopping")
                break
            print("An error occured", file=sys.stderr)
            print(e, file=sys.stderr)
            print("")
            print("")
    if fail_count > 0:
        print("See above for errors")
        input("Press enter to continue...")
        click.Abort(e)


if __name__ == "__main__":  # pragma: no cover
    main()
