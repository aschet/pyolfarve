# SPDX-FileCopyrightText: 2026 Thomas Ascher <thomas.ascher@gmx.at>
#
# SPDX-License-Identifier: MIT

"""Reference colorimetric data used by :mod:`olfarve`.

Two CIE datasets tabulated together from 380 nm to 780 nm in 5 nm steps:

* Color matching functions of the CIE 1931 2 degree standard colorimetric
  observer, standardized as ISO/CIE 11664-1:2019. Values from
  https://cie.co.at/datatable/cie-1931-colour-matching-functions-2-degree-observer
* Relative spectral power distribution of CIE standard illuminant D65,
  standardized as ISO/CIE 11664-2:2022. Values from
  https://cie.co.at/datatable/cie-standard-illuminant-d65

This module is private; its contents may change without notice.
"""

from __future__ import annotations

from typing import Final, NamedTuple

__all__ = [
    "CIE_SAMPLES",
    "FIRST_WAVELENGTH_NM",
    "WAVELENGTH_STEP_NM",
    "CIESample",
]

#: Wavelength of the first sample in :data:`CIE_SAMPLES`, in nanometers.
FIRST_WAVELENGTH_NM: Final = 380.0

#: Distance between two consecutive samples in :data:`CIE_SAMPLES`, in nanometers.
WAVELENGTH_STEP_NM: Final = 5.0


class CIESample(NamedTuple):
    """One wavelength sample of the CIE 1931 observer and the D65 illuminant.

    Field names follow CIE notation: ``x_bar``, ``y_bar`` and ``z_bar`` are the
    color matching functions x(lambda), y(lambda) and z(lambda); ``s_d65`` is
    the relative spectral power distribution S(lambda) of illuminant D65.
    """

    x_bar: float
    y_bar: float
    z_bar: float
    s_d65: float


#: Colorimetric samples from 380 nm to 780 nm in 5 nm increments.
CIE_SAMPLES: Final[tuple[CIESample, ...]] = (
    CIESample(0.001368, 0.000039, 0.006450, 49.9755),
    CIESample(0.002236, 0.000064, 0.010550, 52.3118),
    CIESample(0.004243, 0.000120, 0.020050, 54.6482),
    CIESample(0.007650, 0.000217, 0.036210, 68.7015),
    CIESample(0.014310, 0.000396, 0.067850, 82.7549),
    CIESample(0.023190, 0.000640, 0.110200, 87.1204),
    CIESample(0.043510, 0.001210, 0.207400, 91.486),
    CIESample(0.077630, 0.002180, 0.371300, 92.4589),
    CIESample(0.134380, 0.004000, 0.645600, 93.4318),
    CIESample(0.214770, 0.007300, 1.039050, 90.057),
    CIESample(0.283900, 0.011600, 1.385600, 86.6823),
    CIESample(0.328500, 0.016840, 1.622960, 95.7736),
    CIESample(0.348280, 0.023000, 1.747060, 104.865),
    CIESample(0.348060, 0.029800, 1.782600, 110.936),
    CIESample(0.336200, 0.038000, 1.772110, 117.008),
    CIESample(0.318700, 0.048000, 1.744100, 117.41),
    CIESample(0.290800, 0.060000, 1.669200, 117.812),
    CIESample(0.251100, 0.073900, 1.528100, 116.336),
    CIESample(0.195360, 0.090980, 1.287640, 114.861),
    CIESample(0.142100, 0.112600, 1.041900, 115.392),
    CIESample(0.095640, 0.139020, 0.812950, 115.923),
    CIESample(0.057950, 0.169300, 0.616200, 112.367),
    CIESample(0.032010, 0.208020, 0.465180, 108.811),
    CIESample(0.014700, 0.258600, 0.353300, 109.082),
    CIESample(0.004900, 0.323000, 0.272000, 109.354),
    CIESample(0.002400, 0.407300, 0.212300, 108.578),
    CIESample(0.009300, 0.503000, 0.158200, 107.802),
    CIESample(0.029100, 0.608200, 0.111700, 106.296),
    CIESample(0.063270, 0.710000, 0.078250, 104.79),
    CIESample(0.109600, 0.793200, 0.057250, 106.239),
    CIESample(0.165500, 0.862000, 0.042160, 107.689),
    CIESample(0.225750, 0.914850, 0.029840, 106.047),
    CIESample(0.290400, 0.954000, 0.020300, 104.405),
    CIESample(0.359700, 0.980300, 0.013400, 104.225),
    CIESample(0.433450, 0.994950, 0.008750, 104.046),
    CIESample(0.512050, 1.000000, 0.005750, 102.023),
    CIESample(0.594500, 0.995000, 0.003900, 100.0),
    CIESample(0.678400, 0.978600, 0.002750, 98.1671),
    CIESample(0.762100, 0.952000, 0.002100, 96.3342),
    CIESample(0.842500, 0.915400, 0.001800, 96.0611),
    CIESample(0.916300, 0.870000, 0.001650, 95.788),
    CIESample(0.978600, 0.816300, 0.001400, 92.2368),
    CIESample(1.026300, 0.757000, 0.001100, 88.6856),
    CIESample(1.056700, 0.694900, 0.001000, 89.3459),
    CIESample(1.062200, 0.631000, 0.000800, 90.0062),
    CIESample(1.045600, 0.566800, 0.000600, 89.8026),
    CIESample(1.002600, 0.503000, 0.000340, 89.5991),
    CIESample(0.938400, 0.441200, 0.000240, 88.6489),
    CIESample(0.854450, 0.381000, 0.000190, 87.69871),
    CIESample(0.751400, 0.321000, 0.000100, 85.4936),
    CIESample(0.642400, 0.265000, 0.000050, 83.2886),
    CIESample(0.541900, 0.217000, 0.000030, 83.4939),
    CIESample(0.447900, 0.175000, 0.000020, 83.6992),
    CIESample(0.360800, 0.138200, 0.000010, 81.863),
    CIESample(0.283500, 0.107000, 0.000000, 80.0268),
    CIESample(0.218700, 0.081600, 0.000000, 80.1207),
    CIESample(0.164900, 0.061000, 0.000000, 80.2146),
    CIESample(0.121200, 0.044580, 0.000000, 81.2462),
    CIESample(0.087400, 0.032000, 0.000000, 82.2778),
    CIESample(0.063600, 0.023200, 0.000000, 80.281),
    CIESample(0.046770, 0.017000, 0.000000, 78.2842),
    CIESample(0.032900, 0.011920, 0.000000, 74.0027),
    CIESample(0.022700, 0.008210, 0.000000, 69.7213),
    CIESample(0.015840, 0.005723, 0.000000, 70.6652),
    CIESample(0.011359, 0.004102, 0.000000, 71.6091),
    CIESample(0.008111, 0.002929, 0.000000, 72.979),
    CIESample(0.005790, 0.002091, 0.000000, 74.349),
    CIESample(0.004109, 0.001484, 0.000000, 67.9765),
    CIESample(0.002899, 0.001047, 0.000000, 61.604),
    CIESample(0.002049, 0.000740, 0.000000, 65.7448),
    CIESample(0.001440, 0.000520, 0.000000, 69.8856),
    CIESample(0.001000, 0.000361, 0.000000, 72.4863),
    CIESample(0.000690, 0.000249, 0.000000, 75.087),
    CIESample(0.000476, 0.000172, 0.000000, 69.3398),
    CIESample(0.000332, 0.000120, 0.000000, 63.5927),
    CIESample(0.000235, 0.000085, 0.000000, 55.0054),
    CIESample(0.000166, 0.000060, 0.000000, 46.4182),
    CIESample(0.000117, 0.000042, 0.000000, 56.6118),
    CIESample(0.000083, 0.000030, 0.000000, 66.8054),
    CIESample(0.000059, 0.000021, 0.000000, 65.0941),
    CIESample(0.000042, 0.000015, 0.000000, 63.3828),
)
