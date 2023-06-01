"""Utility to downscale an image to the desired file size using ffmpeg."""
import os
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

def _decrements():
    """
    >>> t = _decrements(); list([next(t) for _ in range(15)])
    [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05]

    >>> t = _decrements(); _ = [next(t) for _ in range(15)]; list([next(t) for _ in range(10)])
    [0.04, 0.03, 0.02, 0.01, 0.009, 0.008, 0.007, 0.006, 0.005, 0.004]
    """
    step_size = 1
    current_value = 1.0
    yield current_value
    while True: # iterate forever
        step = 10**(-step_size)
        if current_value - step <= 0:
            step_size += 1
            step = 10**(-step_size)
        current_value = round(current_value- step, step_size)
        yield round(current_value, 3)

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
    scales = _decrements()
    current_scale = next(scales)

    if current_size <= max_mega_bytes:
        print("Not changing")
        return img

    out_suffix = f".{override_output_format}" if override_output_format else ".".join(img.suffixes)
    working_img = img.parent / (output_prefix + img.stem + output_suffix + out_suffix)
    working_img.parent.mkdir(exist_ok=True, parents=True)
    try:
        shutil.copyfile(img, working_img)
    except:
        os.chmod(working_img, 0o777) # read and write by everyone
        shutil.copyfile(img, working_img)

    while current_size > max_mega_bytes:
        if working_img.is_file():
            working_img.unlink()

        working_img = _scale(img, out_img=working_img, scale=current_scale)

        current_size = _get_file_size_in_mega(working_img)
        current_scale = next(scales)

    return working_img
