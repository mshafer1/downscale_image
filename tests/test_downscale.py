import pathlib
import downscale_image
from typing import NamedTuple

import pytest
from pytest_snapshot.plugin import Snapshot


class _ResultInfo(NamedTuple):
    output: pathlib.Path
    max_mb: int


@pytest.fixture(params=[1, 2, 3], ids=lambda v: f"{v}MB")
def test_result(request, test_image):
    max_mb: int = request.param
    output = downscale_image.downscale(img=test_image, max_mega_bytes=max_mb)
    yield _ResultInfo(output, max_mb)


def test___image___downscale___outputs_expected_file(test_result: _ResultInfo, snapshot: Snapshot):
    snapshot.assert_match(
        test_result.output.read_bytes(), "out" + ".".join(test_result.output.suffixes)
    )


def test___image___downscale___output_is_request_size(test_result: _ResultInfo):
    out_file_size = len(test_result.output.read_bytes()) / 1024 / 1024
    assert out_file_size < test_result.max_mb
