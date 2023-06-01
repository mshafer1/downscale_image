"""Utility to downscale an image to the desired file size using ffmpeg."""
import os.path
import pathlib
import shutil
import subprocess
import sys
import typing
import logging

SUPPORTED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp"]

_MODULE_LOGGER = logging.getLogger(__name__)
_MODULE_LOGGER.addHandler(logging.NullHandler())

def _bytes_to_mega_bytes(bytes: int) -> float:
    return bytes / 1024 / 1024


def _get_file_size_in_mega(file: pathlib.Path) -> float:
    file_size = os.path.getsize(file)
    return _bytes_to_mega_bytes(file_size)


def _scale(img: pathlib.Path, out_img: pathlib.Path, scale: float) -> pathlib.Path:
    """Use ffmpeg to scale the image by the desired amount."""
    as_divisor = 1 / scale
    try:
        output = subprocess.check_output(
            f'ffmpeg -i "{img}" -vf scale="iw/{as_divisor:.2f}:-1" "{out_img}"',
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        _MODULE_LOGGER.warning("Failed to process %s:\n %s", img, e.output)
        raise
    except FileNotFoundError:
        print(
            "Error, Could not find ffmpeg to execute. Make sure it is on the PATH variable.",
            file=sys.stderr,
        )
        raise
    return out_img


def downscale(
    img: pathlib.Path, max_mega_bytes: float, *_, output_prefix="", output_suffix="_smaller", override_output_format: typing.Optional[str]=None
) -> pathlib.Path:
    """Incrementally downscale img until it is <= max_mega_bytes in size."""
    current_size = _get_file_size_in_mega(img)
    working_img = img
    current_scale = 1.0
    current_multiplier = 10

    if current_size <= max_mega_bytes:
        print("Not changing")
        return img

    out_suffix = f".{override_output_format}" if override_output_format else ".".join(img.suffixes)
    working_img = img.parent / (output_prefix + img.stem + output_suffix + out_suffix)
    working_img.parent.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(img, working_img)

    while current_size > max_mega_bytes:
        if working_img.is_file():
            working_img.unlink()

        working_img = _scale(img, out_img=working_img, scale=current_scale)

        current_size = _get_file_size_in_mega(working_img)
        current_scale -= 1 / current_multiplier
        if current_scale < 0:
            current_scale = 1/current_multiplier
            current_multiplier += 10

    return working_img
