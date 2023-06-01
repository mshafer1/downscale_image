"""Downscale an image to desired file size."""
import logging
import pathlib
import platform
import sys
import typing

import click
import pathspec
import tqdm
import tqdm.contrib.logging

import downscale_image

_ON_WINDOWS = platform.system().lower() == "windows"
_MODULE_LOGGER = logging.getLogger(__name__)

if _ON_WINDOWS:
    from downscale_image import _registry_utils

_DEFAULT_MATCHES = (
    ["!.venv/", "!.git/", "!objects/", "!.ts/*"]
    + [f"*{ext}" for ext in downscale_image.SUPPORTED_FILE_EXTENSIONS]
    + [f"*{ext}".upper() for ext in downscale_image.SUPPORTED_FILE_EXTENSIONS]
)
_CWD = pathlib.Path.cwd()


@click.command()
@click.version_option()
@click.option(
    "--max-size",
    default=2,
    help="Max output size (in MB)",
    type=click.FloatRange(min=0, min_open=True),
    show_default=True,
)
@click.option(
    "--prefix",
    default="",
    help="Additional part of name to add start of new file name. (include a '/' to denote a folder)",
)
@click.option(
    "--suffix", default="_smaller", help="Additional name to add when generating new file name.", show_default=True
)
@click.option(
    "--override-output-format", help="Change output file extensions (useful for wanting to switch from png to jpg or vice verse)"
)
@click.option(
    "--add-to-right-click-menu",
    help="(Windows only) Register this program in right click menu for supported file types.",
    is_flag=True,
    default=False,
)
@click.option(
    "--continue-on-errors",
    help="Even if multiple errors are encountered keep going through all images",
    is_flag=True,
    default=False
)
@click.argument(
    "in_file",
    nargs=-1,
    metavar="FILE_OR_DIRECTORY",
    type=click.Path(exists=True, dir_okay=True, path_type=pathlib.Path),
)
def main(
    max_size,
    in_file: typing.Tuple[pathlib.Path],
    add_to_right_click_menu: bool,
    suffix: str,
    prefix: str,
    override_output_format: typing.Optional[str],
    continue_on_errors: bool,
):
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
                pathspec.patterns.GitWildMatchPattern, _DEFAULT_MATCHES + [f"!*{suffix}.*"]
            )
            files_to_prcoess.extend([path / p for p in spec.match_tree(path)])
        else:
            files_to_prcoess.append(path)

    fail_count = 0
    last_error = None
    if not files_to_prcoess:
        _MODULE_LOGGER.warning("Nothing to process.")
    file: pathlib.Path
    with tqdm.contrib.logging.logging_redirect_tqdm():
        for file in tqdm.tqdm(files_to_prcoess, desc="Downscaling: "):
            try:
                file = file.resolve().relative_to(_CWD)
            except ValueError:
                file = file.resolve()
            print(f"Downscaling {file}...")
            try:
                output = downscale_image.downscale(
                    file, max_mega_bytes=max_size, output_prefix=prefix, outtput_suffix=suffix, override_output_format=override_output_format
                )
                print(f"Finished. Output stored in {output}\n")
            except Exception as e:
                _MODULE_LOGGER.warning("Failed to downscale (%s), error:\n%s\n\n", file, e)
                fail_count += 1
                if not continue_on_errors and fail_count > 5:
                    print("Several errors have occured, stopping")
                    break
                last_error = e
                print("")
                print("")
    if last_error:
        print("See above for errors")
        input("Press enter to continue...")
        click.Abort(last_error)


if __name__ == "__main__":  # pragma: no cover
    main()
