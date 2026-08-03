# SPDX-FileCopyrightText: 2026 Thomas Ascher <thomas.ascher@gmx.at>
#
# SPDX-License-Identifier: MIT

"""Tests for the command line interface."""

from __future__ import annotations

import pytest
from _pytest.capture import CaptureFixture

import olfarve
from olfarve.cli import main


def run(capsys: CaptureFixture[str], *argv: str) -> list[str]:
    """Run the CLI and return its stdout lines."""
    assert main(list(argv)) == 0
    return capsys.readouterr().out.splitlines()


def test_no_color_values_is_a_usage_error(capsys: CaptureFixture[str]) -> None:
    """Without values there is nothing to convert, so argparse must object."""
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
    assert "required" in capsys.readouterr().err


def test_explicit_color_values(capsys: CaptureFixture[str]) -> None:
    lines = run(capsys, "4", "10")
    assert lines == ["4,#e7aa31", "10,#ba5b00"]


def test_ebc_scale(capsys: CaptureFixture[str]) -> None:
    lines = run(capsys, "--scale", "ebc", "20")
    assert lines == ["20," + olfarve.ebc_to_srgb(20).to_hex()]


def test_path_length_option(capsys: CaptureFixture[str]) -> None:
    lines = run(capsys, "--path-length", "1.0", "10")
    assert lines == ["10," + olfarve.srm_to_srgb(10, 1.0).to_hex()]


def test_fractional_values_are_formatted_compactly(
    capsys: CaptureFixture[str],
) -> None:
    lines = run(capsys, "3.5")
    assert lines[0].startswith("3.5,#")


def test_short_options(capsys: CaptureFixture[str]) -> None:
    assert run(capsys, "-s", "ebc", "-p", "1", "20") == run(
        capsys, "--scale", "ebc", "--path-length", "1", "20"
    )


@pytest.mark.parametrize("argv", [["-1"], ["--path-length", "-1", "10"], ["abc"], []])
def test_invalid_input_exits_with_error(
    capsys: CaptureFixture[str], argv: list[str]
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(argv)
    assert excinfo.value.code == 2


def test_version(capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert olfarve.__version__ in capsys.readouterr().out
