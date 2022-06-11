"""Downscale an image to desired file size."""
import pathlib
import sys

import click

import downscale_image


@click.command()
@click.option(
    "--max-size",
    default=2,
    help="Max output size (in MB)",
    type=click.IntRange(min=0, min_open=True),
)
@click.argument("in_file", type=click.Path(exists=True, dir_okay=False))
def main(max_size, in_file):
    """Downscale in_file to desired max-size."""
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
