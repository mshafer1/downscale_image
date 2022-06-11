"""Test the downscale functionality."""
import io
import pathlib
import shutil
from typing import Callable
from typing import List
from typing import NamedTuple

import click.testing
import pytest
from pytest_snapshot.plugin import Snapshot

import tests


class _ResultInfo(NamedTuple):
    output: pathlib.Path
    max_mb: int


@pytest.fixture(params=[1, 2, 3], ids=lambda v: f"{v}MB")
def test_result(
    request, test_image: pathlib.Path, runner: Callable[[List[str]], click.testing.Result]
):
    """Get the output of the cli."""
    max_mb: int = request.param
    if max_mb == 2:
        runner_result = runner([str(test_image)])
    else:
        runner_result = runner([f"--max-size={max_mb}", str(test_image)])
    assert runner_result.exception is None

    output = test_image.parent / (test_image.stem + "_smaller" + ".".join(test_image.suffixes))
    if output.is_file():
        yield _ResultInfo(output, max_mb)
    else:
        yield _ResultInfo(test_image, max_mb)


def test___image___downscale___outputs_expected_file(test_result: _ResultInfo, snapshot: Snapshot):
    """Given an image, assert that downscaling produces the expected output."""
    snapshot.assert_match(
        test_result.output.read_bytes(), "out" + ".".join(test_result.output.suffixes)
    )


def test___image___downscale___output_is_request_size(test_result: _ResultInfo):
    """Given an image, assert that downscaling is effectctive."""
    out_file_size = len(test_result.output.read_bytes()) / 1024 / 1024
    assert out_file_size < test_result.max_mb


def test___invalid_path___downscale___errors(
    runner: Callable[[List[str]], click.testing.Result],
    tmp_path: pathlib.Path,
    monkeypatch,
):
    """Given an invalid path, assert that useful information is printed and errored out."""
    monkeypatch.setattr("sys.stdin", io.StringIO("\n" * 5))
    result = runner([str(tmp_path)])

    assert result.exception is not None
    assert "Invalid value for 'IN_FILE': File" in result.output


def test___ffmpeg_not_found___downscale___prints_message(
    runner: Callable[[List[str]], click.testing.Result],
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Given a missing ffmpeg, assert that useful information is printed and errored out."""
    monkeypatch.setenv("PATH", "")
    file = tmp_path / "image.png"
    shutil.copy2(tests.TEST_FOLDER / "test.png", file)

    result = runner([str(file)])

    assert result.exception is not None
    assert "Could not find ffmpeg" in str(result.output)
