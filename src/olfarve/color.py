# SPDX-FileCopyrightText: 2026 Thomas Ascher <thomas.ascher@gmx.at>
#
# SPDX-License-Identifier: MIT

"""sRGB rendering of SRM and EBC beer color values.

The spectral model is A. J. de Lange, "Color," in *Brewing Materials and
Processes*, Elsevier, 2016, pp. 199-249: beer's transmittance across the
visible range is approximated from its absorption at 430 nm. Integrating that
against the CIE 1931 color matching functions under illuminant D65 gives XYZ
tristimulus values, which are then transformed to sRGB.

The sRGB primaries, white point and gamma encoding follow
https://www.w3.org/Graphics/Color/srgb. The colorimetric data is documented in
:mod:`olfarve._cie`.
"""

from __future__ import annotations

import math
from typing import Final, NamedTuple

from ._cie import CIE_SAMPLES, FIRST_WAVELENGTH_NM, WAVELENGTH_STEP_NM

__all__ = [
    "DEFAULT_PATH_LENGTH_CM",
    "SRGBColor",
    "absorption_to_srgb",
    "ebc_to_srgb",
    "srm_to_srgb",
]

#: Default optical path length in cm, set to the typical sample glass width
#: specified by the BJCP color guide.
#: https://www.bjcp.org/education-training/education-resources/color-guide
DEFAULT_PATH_LENGTH_CM: Final = 5.0

# Both scales are defined as a multiple of the absorbance at 430 nm measured
# over a 1 cm path: SRM = 12.7 * A430 and EBC = 25.0 * A430.
_SRM_PER_ABSORBANCE: Final = 12.7
_EBC_PER_ABSORBANCE: Final = 25.0

# The de Lange approximation sums two exponentials decaying away from 430 nm,
# giving absorption at any wavelength relative to the absorption there.
_REFERENCE_WAVELENGTH_NM: Final = 430.0
_SHORT_DECAY_WEIGHT: Final = 0.02465
_SHORT_DECAY_NM: Final = 17.591
_LONG_DECAY_WEIGHT: Final = 0.97535
_LONG_DECAY_NM: Final = 82.122

# Piecewise sRGB gamma encoding: linear below the threshold, a power law
# above it.
_GAMMA_THRESHOLD: Final = 0.0031308
_GAMMA_SLOPE: Final = 12.92
_GAMMA_SCALE: Final = 1.055
_GAMMA_OFFSET: Final = 0.055
_GAMMA_EXPONENT: Final = 1.0 / 2.4


def _calculate_k() -> float:
    """Return the normalizing constant for illuminant D65.

    CIE defines ``k = 100 / sum(S(lambda) * y_bar(lambda))``, putting the
    luminance of a perfectly transmitting sample at 100. Dropping the factor
    of 100 puts it at 1.0 instead, which is the range sRGB expects.
    """
    luminance = 0.0
    for sample in CIE_SAMPLES:
        luminance += sample.s_d65 * sample.y_bar
    return 1.0 / luminance


def _absorption_ratio(wavelength_nm: float) -> float:
    """Return absorption at ``wavelength_nm`` relative to that at 430 nm."""
    offset_nm = wavelength_nm - _REFERENCE_WAVELENGTH_NM
    return _SHORT_DECAY_WEIGHT * math.exp(
        -offset_nm / _SHORT_DECAY_NM
    ) + _LONG_DECAY_WEIGHT * math.exp(-offset_nm / _LONG_DECAY_NM)


def _build_spectrum() -> tuple[tuple[float, float, float, float, float], ...]:
    """Precompute the wavelength dependent terms of the integration.

    Only the absorbance varies between conversions. The absorption ratios and
    the colorimetric weights depend solely on wavelength, so they are
    evaluated once at import rather than on every call.
    """
    spectrum = []
    wavelength_nm = FIRST_WAVELENGTH_NM
    for sample in CIE_SAMPLES:
        spectrum.append(
            (
                _absorption_ratio(wavelength_nm),
                sample.s_d65,
                sample.x_bar,
                sample.y_bar,
                sample.z_bar,
            )
        )
        wavelength_nm += WAVELENGTH_STEP_NM
    return tuple(spectrum)


_K: Final = _calculate_k()
_SPECTRUM: Final = _build_spectrum()


def _to_8bit(component: float) -> int:
    """Quantize one gamma encoded component to an integer in ``[0, 255]``."""
    return min(255, max(0, round(component * 255.0)))


def _encode_gamma(linear: float) -> float:
    """Gamma encode one linear component, clamping it to ``[0, 1]`` first.

    This is the inverse of the sRGB EOTF: it maps a linear tristimulus
    component to the non-linear signal a display decodes.
    """
    linear = max(0.0, min(1.0, linear))
    if linear <= _GAMMA_THRESHOLD:
        return linear * _GAMMA_SLOPE
    return _GAMMA_SCALE * math.pow(linear, _GAMMA_EXPONENT) - _GAMMA_OFFSET


class SRGBColor(NamedTuple):
    """An sRGB color, gamma encoded, with components in ``[0, 1]``.

    A :class:`tuple` subclass, so it unpacks and indexes like a plain triplet
    and can be handed straight to any API expecting one::

        >>> red, green, blue = srm_to_srgb(10)
    """

    r: float
    g: float
    b: float

    def to_rgb8(self) -> tuple[int, int, int]:
        """Return the color quantized to 8 bits per channel.

        Components are clamped into gamut first, so the result is a valid 8
        bit triplet even for an instance built by hand out of range.

        >>> SRGBColor(1.0, 0.5, 0.0).to_rgb8()
        (255, 128, 0)
        >>> SRGBColor(2.0, -1.0, 0.0).to_rgb8()
        (255, 0, 0)
        """
        return (_to_8bit(self.r), _to_8bit(self.g), _to_8bit(self.b))

    def to_hex(self) -> str:
        """Return the color as a ``#rrggbb`` string.

        >>> SRGBColor(1.0, 0.5, 0.0).to_hex()
        '#ff8000'
        >>> SRGBColor(2.0, -1.0, 0.0).to_hex()
        '#ff0000'
        """
        r, g, b = self.to_rgb8()
        return f"#{r:02x}{g:02x}{b:02x}"


def absorption_to_srgb(
    absorption_430: float, path_length_cm: float = DEFAULT_PATH_LENGTH_CM
) -> SRGBColor:
    """Convert a beer's absorption at 430 nm into an sRGB color.

    Prefer :func:`srm_to_srgb` or :func:`ebc_to_srgb` when you have a color
    value, which is what brewing software reports. This function is for a
    photometer reading taken directly, where the absorbance is the
    measurement and the SRM or EBC value is derived from it.

    :param absorption_430: Linear decadic absorption coefficient at 430 nm,
        in cm^-1. Numerically this is the ASBC/EBC absorbance A430, which is
        defined for a 1 cm path length.
    :param path_length_cm: Optical path length in cm, e.g. the glass width.
    :returns: The gamma encoded color, with components in ``[0, 1]``.
    :raises ValueError: If either argument is negative.

    >>> absorption_to_srgb(10.0 / 12.7).to_hex()
    '#ba5b00'
    """
    if absorption_430 < 0.0:
        raise ValueError(f"absorption_430 must not be negative, got {absorption_430!r}")
    if path_length_cm < 0.0:
        raise ValueError(f"path_length_cm must not be negative, got {path_length_cm!r}")

    # Beer-Lambert law: absorbance A = a * l, and transmittance T = 10 ** -A.
    absorbance_430 = absorption_430 * path_length_cm

    tristimulus_x = 0.0
    tristimulus_y = 0.0
    tristimulus_z = 0.0
    for absorption_ratio, s_d65, x_bar, y_bar, z_bar in _SPECTRUM:
        transmitted_power = s_d65 * 10.0 ** (-absorbance_430 * absorption_ratio)
        tristimulus_x += transmitted_power * x_bar
        tristimulus_y += transmitted_power * y_bar
        tristimulus_z += transmitted_power * z_bar

    tristimulus_x *= _K
    tristimulus_y *= _K
    tristimulus_z *= _K

    # XYZ to linear sRGB, D65 white point.
    return SRGBColor(
        _encode_gamma(
            tristimulus_x * 3.2406255
            + tristimulus_y * -1.537208
            + tristimulus_z * -0.4986286
        ),
        _encode_gamma(
            tristimulus_x * -0.9689307
            + tristimulus_y * 1.8757561
            + tristimulus_z * 0.0415175
        ),
        _encode_gamma(
            tristimulus_x * 0.0557101
            + tristimulus_y * -0.2040211
            + tristimulus_z * 1.0569959
        ),
    )


def srm_to_srgb(
    srm: float, path_length_cm: float = DEFAULT_PATH_LENGTH_CM
) -> SRGBColor:
    """Convert a Standard Reference Method color value into an sRGB color.

    :param srm: The SRM color value.
    :param path_length_cm: Optical path length in cm, e.g. the glass width.
    :returns: The gamma encoded color, with components in ``[0, 1]``.
    :raises ValueError: If either argument is negative.

    >>> srm_to_srgb(10).to_hex()
    '#ba5b00'
    """
    return absorption_to_srgb(srm / _SRM_PER_ABSORBANCE, path_length_cm)


def ebc_to_srgb(
    ebc: float, path_length_cm: float = DEFAULT_PATH_LENGTH_CM
) -> SRGBColor:
    """Convert a European Brewery Convention color value into an sRGB color.

    :param ebc: The EBC color value.
    :param path_length_cm: Optical path length in cm, e.g. the glass width.
    :returns: The gamma encoded color, with components in ``[0, 1]``.
    :raises ValueError: If either argument is negative.

    >>> ebc_to_srgb(20).to_hex()
    '#b95900'
    """
    return absorption_to_srgb(ebc / _EBC_PER_ABSORBANCE, path_length_cm)
