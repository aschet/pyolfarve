# SPDX-FileCopyrightText: 2026 Thomas Ascher <thomas.ascher@gmx.at>
#
# SPDX-License-Identifier: MIT

"""Tests for the package metadata and public surface."""

from __future__ import annotations

import pathlib
import subprocess
import sys
from importlib import metadata

import olfarve


def test_version_matches_distribution_metadata() -> None:
    assert olfarve.__version__ == metadata.version("olfarve")


def test_public_api_is_exported() -> None:
    for name in olfarve.__all__:
        assert hasattr(olfarve, name), name


def test_package_is_typed() -> None:
    """The PEP 561 marker ships next to the package sources."""
    assert (pathlib.Path(olfarve.__file__).parent / "py.typed").is_file()


def test_module_is_executable() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "olfarve", "1"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.splitlines() == ["1,#fae8b6"]
