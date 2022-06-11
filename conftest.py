import pathlib
import functools
import shutil

import pytest
from click.testing import CliRunner

import downscale_image.__main__

TEST_FOLDER = pathlib.Path(__file__).parent / "tests" / "test_files"
TEST_IMAGES = [file for file in TEST_FOLDER.iterdir() if file.is_file()]


@pytest.fixture(params=TEST_IMAGES, ids=lambda v:v.name)
def test_image(request, tmp_path: pathlib.Path):
    in_file: pathlib.Path = request.param
    shutil.copy2(request.param, tmp_path)
    yield tmp_path / in_file.name


@pytest.fixture()
def runner():
    _runner = CliRunner()
    yield functools.partial(_runner.invoke, downscale_image.__main__.main)