# SPDX-FileCopyrightText: 2026 Thomas Ascher <thomas.ascher@gmx.at>
#
# SPDX-License-Identifier: MIT

"""Command line interface for :mod:`olfarve`."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__
from .color import DEFAULT_PATH_LENGTH_CM, ebc_to_srgb, srm_to_srgb

__all__ = ["main"]


def _non_negative_float(text: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number") from None
    if value < 0.0:
        raise argparse.ArgumentTypeError(f"{text!r} must not be negative")
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="olfarve",
        description="Render SRM/EBC beer color values as sRGB colors.",
    )
    parser.add_argument(
        "color_values",
        metavar="VALUE",
        nargs="+",
        type=_non_negative_float,
        help="one or more color values to convert",
    )
    parser.add_argument(
        "-s",
        "--scale",
        choices=("srm", "ebc"),
        default="srm",
        help="color scale of the values (default: %(default)s)",
    )
    parser.add_argument(
        "-p",
        "--path-length",
        metavar="CM",
        type=_non_negative_float,
        default=DEFAULT_PATH_LENGTH_CM,
        help="optical path length in cm (default: %(default)s)",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line interface.

    :param argv: Arguments to parse; defaults to :data:`sys.argv` when ``None``.
    :returns: The process exit status.
    """
    args = _build_parser().parse_args(argv)

    convert = ebc_to_srgb if args.scale == "ebc" else srm_to_srgb
    color_values: Sequence[float] = args.color_values

    for color_value in color_values:
        color = convert(color_value, args.path_length)
        print(f"{color_value:g},{color.to_hex()}")
    return 0
