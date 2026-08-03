# SPDX-FileCopyrightText: 2026 Thomas Ascher <thomas.ascher@gmx.at>
#
# SPDX-License-Identifier: MIT

"""Tests for the color conversion functions."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

import pytest

import olfarve
from olfarve._cie import CIE_SAMPLES, FIRST_WAVELENGTH_NM, WAVELENGTH_STEP_NM
from olfarve.color import (
    _SPECTRUM,
    SRGBColor,
    _absorption_ratio,
    _encode_gamma,
)

SRM_REFERENCE = {
    1: "#fae8b6",
    2: "#f4d180",
    4: "#e7aa31",
    10: "#ba5b00",
    20: "#7d1900",
    30: "#540000",
    40: "#390000",
    50: "#270000",
}


def test_spectrum_table_matches_the_model() -> None:
    """The precomputed table must equal evaluating the model per wavelength.

    The conversion reads _SPECTRUM instead of recomputing the wavelength
    dependent terms, so a drift here would silently change every result.
    """
    assert len(_SPECTRUM) == len(CIE_SAMPLES)
    wavelength_nm = FIRST_WAVELENGTH_NM
    for entry, sample in zip(_SPECTRUM, CIE_SAMPLES, strict=True):
        absorption_ratio, s_d65, x_bar, y_bar, z_bar = entry
        assert absorption_ratio == _absorption_ratio(wavelength_nm)
        assert (s_d65, x_bar, y_bar, z_bar) == (
            sample.s_d65,
            sample.x_bar,
            sample.y_bar,
            sample.z_bar,
        )
        wavelength_nm += WAVELENGTH_STEP_NM


def test_cie_table_shape() -> None:
    assert len(CIE_SAMPLES) == 81
    for sample in CIE_SAMPLES:
        assert len(sample) == 4
        assert all(value >= 0.0 for value in sample)


def test_normalization_factor_scales_white_to_one() -> None:
    """An unabsorbing sample renders as white."""
    r, g, b = olfarve.absorption_to_srgb(0.0)
    assert r == pytest.approx(1.0, abs=1e-4)
    assert g == pytest.approx(1.0, abs=1e-4)
    assert b == pytest.approx(1.0, abs=1e-4)
    assert olfarve.absorption_to_srgb(0.0).to_hex() == "#ffffff"


@pytest.mark.parametrize(("srm", "expected"), sorted(SRM_REFERENCE.items()))
def test_srm_reference_colors(srm: int, expected: str) -> None:
    assert olfarve.srm_to_srgb(srm).to_hex() == expected


@pytest.mark.parametrize("srm", [1, 5, 10, 25, 40])
def test_ebc_matches_equivalent_srm(srm: int) -> None:
    """EBC and SRM are the same scale up to the 25.0 / 12.7 factor."""
    ebc = srm * 25.0 / 12.7
    assert olfarve.ebc_to_srgb(ebc) == pytest.approx(olfarve.srm_to_srgb(srm))


def test_components_are_within_unit_range() -> None:
    for srm in range(0, 61):
        for component in olfarve.srm_to_srgb(srm):
            assert 0.0 <= component <= 1.0


def test_color_darkens_monotonically_with_color_value() -> None:
    previous = math.inf
    for srm in range(0, 41):
        luminance = sum(olfarve.srm_to_srgb(srm))
        assert luminance < previous
        previous = luminance


def test_longer_path_length_darkens_color() -> None:
    short = sum(olfarve.srm_to_srgb(10, path_length_cm=1.0))
    long = sum(olfarve.srm_to_srgb(10, path_length_cm=10.0))
    assert long < short


def test_zero_path_length_is_white() -> None:
    assert olfarve.srm_to_srgb(20, path_length_cm=0.0).to_hex() == "#ffffff"


def test_default_path_length_matches_bjcp_glass_width() -> None:
    assert olfarve.DEFAULT_PATH_LENGTH_CM == 5.0
    assert olfarve.srm_to_srgb(10) == olfarve.srm_to_srgb(
        10, olfarve.DEFAULT_PATH_LENGTH_CM
    )


def test_path_length_is_positional() -> None:
    assert olfarve.ebc_to_srgb(20, 1.0) == olfarve.ebc_to_srgb(20, path_length_cm=1.0)


@pytest.mark.parametrize(
    ("func", "args"),
    [
        (olfarve.absorption_to_srgb, (-0.1,)),
        (olfarve.absorption_to_srgb, (1.0, -1.0)),
        (olfarve.srm_to_srgb, (-1,)),
        (olfarve.srm_to_srgb, (1, -1.0)),
        (olfarve.ebc_to_srgb, (-1,)),
        (olfarve.ebc_to_srgb, (1, -1.0)),
    ],
)
def test_negative_input_raises(
    func: Callable[..., olfarve.SRGBColor], args: Sequence[float]
) -> None:
    with pytest.raises(ValueError):
        func(*args)


class TestSRGBColor:
    def test_is_a_tuple(self) -> None:
        color = olfarve.srm_to_srgb(10)
        assert isinstance(color, tuple)
        assert list(color) == [color[0], color[1], color[2]]
        assert (color.r, color.g, color.b) == tuple(color)

    def test_to_hex(self) -> None:
        assert SRGBColor(1.0, 0.5, 0.0).to_hex() == "#ff8000"
        assert SRGBColor(0.0, 0.0, 0.0).to_hex() == "#000000"

    def test_to_rgb8(self) -> None:
        assert SRGBColor(1.0, 0.5, 0.0).to_rgb8() == (255, 128, 0)


class TestHexOutput:
    def test_endpoints(self) -> None:
        assert SRGBColor(1.0, 1.0, 1.0).to_hex() == "#ffffff"
        assert SRGBColor(0.0, 0.0, 0.0).to_hex() == "#000000"
        assert SRGBColor(1.0, 0.0, 0.0).to_hex() == "#ff0000"

    def test_output_is_lowercase_and_padded(self) -> None:
        text = SRGBColor(0.04, 0.04, 0.04).to_hex()
        assert text == text.lower()
        assert len(text) == 7

    def test_agrees_with_to_rgb8(self) -> None:
        """to_hex is derived from to_rgb8, so the two must never disagree."""
        for srm in range(0, 61):
            color = olfarve.srm_to_srgb(srm)
            expected = "#" + "".join(f"{c:02x}" for c in color.to_rgb8())
            assert color.to_hex() == expected

    @pytest.mark.parametrize(
        ("component", "expected"),
        [(2.0, "#ff0000"), (-1.0, "#000000"), (1.5, "#ff0000")],
    )
    def test_out_of_gamut_components_are_clamped(
        self, component: float, expected: str
    ) -> None:
        """A hand built out of range color must still yield 7 characters."""
        color = (
            SRGBColor(component, 0.0, 0.0)
            if component > 0
            else SRGBColor(component, component, component)
        )
        assert len(color.to_hex()) == 7
        assert all(0 <= c <= 255 for c in color.to_rgb8())
        assert color.to_hex() == expected


class TestGammaEncoding:
    def test_clamps_out_of_range_input(self) -> None:
        assert _encode_gamma(-1.0) == 0.0
        assert _encode_gamma(2.0) == pytest.approx(1.0)

    def test_is_continuous_at_the_knee(self) -> None:
        """The two branches meet, up to the rounding of the sRGB constants."""
        knee = 0.0031308
        below = _encode_gamma(knee)
        above = _encode_gamma(knee + 1e-12)
        assert below == pytest.approx(above, abs=1e-7)

    def test_endpoints(self) -> None:
        assert _encode_gamma(0.0) == 0.0
        assert _encode_gamma(1.0) == pytest.approx(1.0)
