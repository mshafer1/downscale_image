"""Downscale an image to desired file size."""
import pathlib
import platform
import sys
import typing

import click
import pathspec

import downscale_image

_ON_WINDOWS = platform.system().lower() == "windows"

if _ON_WINDOWS:
    from downscale_image import _registry_utils

_DEFAULT_MATCHES = (
    ["!.venv/", "!.git/", "!objects/"]
    + [f"*{ext}" for ext in downscale_image.SUPPORTED_FILE_EXTENSIONS]
    + [f"*{ext}".upper() for ext in downscale_image.SUPPORTED_FILE_EXTENSIONS]
)
_CWD = pathlib.Path.cwd()


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
@click.argument(
    "in_file",
    nargs=-1,
    metavar="FILE_OR_DIRECTORY",
    type=click.Path(exists=True, dir_okay=True, path_type=pathlib.Path),
)
def main(max_size, in_file: typing.Tuple[pathlib.Path], add_to_right_click_menu: bool):
    """Downscale file_or_directory to desired max-size."""
    if add_to_right_click_menu:
        if not _ON_WINDOWS:
            raise Exception("Error, registry right click menus are only support on Windows.")
        exe = pathlib.Path(sys.argv[0])
        args = []
        _registry_utils.register_downscale_commands(str(exe), args)

    files_to_prcoess: typing.List[pathlib.Path] = []

    for path in in_file:
        if path.is_dir():
            spec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, _DEFAULT_MATCHES
            )
            files_to_prcoess.extend([path / p for p in spec.match_tree(path)])
        else:
            files_to_prcoess.append(path)

    fail_count = 0
    last_error = None
    if not files_to_prcoess:
        print("Nothing to process.")
    for file in files_to_prcoess:
        try:
            file = file.resolve().relative_to(_CWD)
        except ValueError:
            file = file.resolve()
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
            last_error = e
            print("")
            print("")
    if last_error:
        print("See above for errors")
        input("Press enter to continue...")
        click.Abort(last_error)


if __name__ == "__main__":  # pragma: no cover
    main()
