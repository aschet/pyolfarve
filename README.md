# pyolfarve

*Øl farve* ("beer color") renders SRM and EBC beer color values as sRGB
colors, following the spectral model described by A. J. de Lange, "Color," in
*Brewing Materials and Processes*, Elsevier, 2016, pp. 199-249.

Given a color value and an optical path length (the width of the glass the
beer is viewed through), the sample's spectral transmittance is derived from
its absorption coefficient at 430 nm via the Beer-Lambert law, integrated
against the CIE 1931 color matching functions of the 2 degree standard
colorimetric observer under illuminant D65, and the resulting XYZ tristimulus
values are transformed to sRGB.

## Installation

```bash
pip install olfarve
```

The package requires Python 3.10 or newer and has no runtime dependencies.

## Usage

```python
import olfarve

olfarve.srm_to_srgb(10).to_hex()
olfarve.ebc_to_srgb(20).to_hex()

# The default path length is 5 cm, the width of a typical sample glass
olfarve.srm_to_srgb(10, path_length_cm=1.0).to_hex()

# Results are SRGBColor named tuples of gamma encoded components in [0, 1]
color = olfarve.srm_to_srgb(10)
color.r, color.g, color.b
color.to_rgb8()

# Or start from an absorbance measured at 430 nm
olfarve.absorption_to_srgb(0.7874)
```

## Command line

Installing the package provides an `olfarve` command. It takes one or more
color values and prints them as CSV:

```bash
olfarve 1 2 10
```

```
1,#fae8b6
2,#f4d180
10,#ba5b00
```

Pick a scale and a path length:

```bash
olfarve --scale ebc --path-length 1.0 8 20 40
```

Run `olfarve --help` for the full list of options. The module is also
executable via `python -m olfarve`.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e . --group dev
pytest
ruff check .
mypy
```
