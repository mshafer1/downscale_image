import pathlib
from typing import Callable, List, NamedTuple
import io

import pytest
from pytest_snapshot.plugin import Snapshot
import click.testing


class _ResultInfo(NamedTuple):
    output: pathlib.Path
    max_mb: int


@pytest.fixture(params=[1, 2, 3], ids=lambda v: f"{v}MB")
def test_result(
    request, test_image: pathlib.Path, runner: Callable[[List[str]], click.testing.Result]
):
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
    snapshot.assert_match(
        test_result.output.read_bytes(), "out" + ".".join(test_result.output.suffixes)
    )


def test___image___downscale___output_is_request_size(test_result: _ResultInfo):
    out_file_size = len(test_result.output.read_bytes()) / 1024 / 1024
    assert out_file_size < test_result.max_mb


def test___invalid_path___downscale___prints_message(
    runner: Callable[[List[str]], click.testing.Result],
    tmp_path: pathlib.Path,
    monkeypatch,
):
    monkeypatch.setattr('sys.stdin', io.StringIO('\n'*5))
    result = runner([str(tmp_path), "--max-size=-1"])

    assert result.exception is not None
    assert "An error occured" in str(result.output)


def test___target_already_exists___downscale___prints_message(
    runner: Callable[[List[str]], click.testing.Result],
    tmp_path: pathlib.Path,
):
    file = tmp_path / "image.png"
    file.touch()
    out_file = tmp_path / "image_smaller.png"
    out_file.touch()

    result = runner([str(file)])

    assert result.exception is not None
    assert "An error occured" in str(result.output)
