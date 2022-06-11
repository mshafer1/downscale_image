import pathlib
import click

import downscale_image


@click.command()
@click.option("--max-size", default=2, help="Max output size (in MB)")
@click.argument("in_file", type=click.Path())
def main(max_size, in_file):
    in_file = pathlib.Path(in_file)

    print(f"Downscaling {in_file}...")
    downscale_image.downscale(in_file, max_mega_bytes=max_size)
    print(f"Finished")


if __name__ == "__main__":
    main()
