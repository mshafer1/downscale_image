"""Configure pytest."""
import functools
import pathlib
import shutil

import pytest
from click.testing import CliRunner

import downscale_image.__main__
import tests

TEST_IMAGES = [file for file in tests.TEST_FOLDER.iterdir() if file.is_file()]


@pytest.fixture(params=TEST_IMAGES, ids=lambda v: v.name)
def test_image(request, tmp_path: pathlib.Path):
    """Provide test images to tests."""
    in_file: pathlib.Path = request.param
    shutil.copy2(request.param, tmp_path)
    yield tmp_path / in_file.name


@pytest.fixture()
def runner():
    """Provide helper to call the cli entry point."""
    _runner = CliRunner()
    yield functools.partial(_runner.invoke, downscale_image.__main__.main)
