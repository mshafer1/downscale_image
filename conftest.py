import pathlib
import shutil

import pytest

import downscale_image

TEST_FOLDER = pathlib.Path(__file__).parent / "tests" / "test_files"
TEST_IMAGES = [file for file in TEST_FOLDER.iterdir() if file.is_file()]


@pytest.fixture(params=TEST_IMAGES, ids=lambda v:v.name)
def test_image(request, tmp_path: pathlib.Path):
    in_file: pathlib.Path = request.param
    shutil.copy2(request.param, tmp_path)
    yield tmp_path / in_file.name
