# SPDX-FileCopyrightText: 2026 Thomas Ascher <thomas.ascher@gmx.at>
#
# SPDX-License-Identifier: MIT

"""Øl farve: sRGB color rendering of SRM/EBC beer color values.

Basic usage::

    >>> import olfarve
    >>> olfarve.srm_to_srgb(10).to_hex()
    '#ba5b00'
    >>> olfarve.ebc_to_srgb(20, path_length_cm=1.0).to_hex()
    '#f4d17e'
"""

from __future__ import annotations

from .color import (
    DEFAULT_PATH_LENGTH_CM,
    SRGBColor,
    absorption_to_srgb,
    ebc_to_srgb,
    srm_to_srgb,
)

__all__ = [
    "DEFAULT_PATH_LENGTH_CM",
    "SRGBColor",
    "__version__",
    "absorption_to_srgb",
    "ebc_to_srgb",
    "srm_to_srgb",
]

__version__ = "1.0.0"
