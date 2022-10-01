"""Utility to downscale an image to the desired file size using ffmpeg."""
import os.path
import pathlib
import shutil
import subprocess
import sys

SUPPORTED_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp"]

def _bytes_to_mega_bytes(bytes: int) -> float:
    return bytes / 1024 / 1024


def _get_file_size_in_mega(file: pathlib.Path) -> float:
    file_size = os.path.getsize(file)
    return _bytes_to_mega_bytes(file_size)


def _scale(img: pathlib.Path, scale: float) -> pathlib.Path:
    """Use ffmpeg to scale the image by the desired amount."""
    as_divisor = 1 / scale
    out_name = img.stem + "_smaller" + ".".join(img.suffixes)
    result = img.parent / out_name
    try:
        output = subprocess.check_output(
            f'ffmpeg -i "{img}" -vf scale="iw/{as_divisor:.2f}:-1" "{result}"'
        )
    except subprocess.CalledProcessError:
        print(output, file=sys.stderr)
        raise
    except FileNotFoundError:
        print(
            "Error, Could not find ffmpeg to execute. Make sure it is on the PATH variable.",
            file=sys.stderr,
        )
        raise
    return result


def downscale(img: pathlib.Path, max_mega_bytes: int) -> pathlib.Path:
    """Incrementally downscale img until it is <= max_mega_bytes in size."""
    current_size = _get_file_size_in_mega(img)
    working_img = img
    current_scale = 1.0

    if current_size <= max_mega_bytes:
        return img

    working_img = img.parent / (img.stem + "_smaller" + ".".join(img.suffixes))
    shutil.copyfile(img, working_img)

    while current_size > max_mega_bytes:
        if working_img.is_file():
            working_img.unlink()

        working_img = _scale(img, scale=current_scale)

        current_size = _get_file_size_in_mega(working_img)
        current_scale -= 0.1
    return working_img
