"""EAN-13 golden vectors used by encoding tests.

Each vector contains a 13-digit input string (including the check digit) and the
expected row-0 module string (95 characters of '0' and '1').

PROVENANCE: the expected module strings are verified against the independent
bwip-js / BWIPP ``ean13`` encoder, NOT this project's encoder.

One vector is provided for each possible first digit (0–9), ensuring that every
EAN-13 parity row in ISO 15420 Table 3 is exercised.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Ean13Vector:
    """One known-good EAN-13 fixture."""

    input_data: str
    """13-digit GTIN-13 string (12 data digits + 1 check digit)."""

    expected_row0: str
    """Expected 95-character module string for barcode row 0 ('0'=space, '1'=bar)."""


# ---------------------------------------------------------------------------
# Vectors — one per first digit (D1 = 0 through 9)
# ---------------------------------------------------------------------------
# Module strings computed from ISO 15420:2009 character tables using:
# SET_A, SET_B, EAN13_PARITY, NORMAL_GUARD=(1,0,1), CENTRE_GUARD=(0,1,0,1,0)
# Structure: NORMAL_GUARD(3) + left_half(42) + CENTRE_GUARD(5) + right_half(42) + NORMAL_GUARD(3) = 95 modules

EAN13_D1_0 = Ean13Vector(
    input_data="0123456789012",
    expected_row0=("10100110010010011011110101000110110001010111101010100010010010001110100111001011001101101100101"),
)

EAN13_D1_1 = Ean13Vector(
    input_data="1234567890128",
    expected_row0=("10100100110111101001110101100010000101001000101010100100011101001110010110011011011001001000101"),
)

EAN13_D1_2 = Ean13Vector(
    input_data="2345678901234",
    expected_row0=("10101111010100011011100100001010111011000100101010111010011100101100110110110010000101011100101"),
)

EAN13_D1_3 = Ean13Vector(
    input_data="3456789012340",
    expected_row0=("10101000110110001000010100100010001001000101101010111001011001101101100100001010111001110010101"),
)

EAN13_D1_4 = Ean13Vector(
    input_data="4006381333931",
    expected_row0=("10100011010100111010111101111010001001011001101010100001010000101000010111010010000101100110101"),
)

EAN13_D1_5 = Ean13Vector(
    input_data="5678901234562",
    expected_row0=("10101011110010001000100100010110001101011001101010110110010000101011100100111010100001101100101"),
)

EAN13_D1_6 = Ean13Vector(
    input_data="6789012345678",
    expected_row0=("10101110110001001001011101001110011001001001101010100001010111001001110101000010001001001000101"),
)

EAN13_D1_7 = Ean13Vector(
    input_data="7890123456784",
    expected_row0=("10101101110010111000110101100110010011010000101010101110010011101010000100010010010001011100101"),
)

EAN13_D1_8 = Ean13Vector(
    input_data="8901234567890",
    expected_row0=("10100010110100111001100100110110100001010001101010100111010100001000100100100011101001110010101"),
)

EAN13_D1_9 = Ean13Vector(
    input_data="9012345678906",
    expected_row0=("10100011010110011001101101111010011101011000101010101000010001001001000111010011100101010000101"),
)

# ---------------------------------------------------------------------------
# Aggregate collection — parametrize over this tuple in tests
# ---------------------------------------------------------------------------

EAN13_GOLDEN_VECTORS: tuple[Ean13Vector, ...] = (
    EAN13_D1_0,
    EAN13_D1_1,
    EAN13_D1_2,
    EAN13_D1_3,
    EAN13_D1_4,
    EAN13_D1_5,
    EAN13_D1_6,
    EAN13_D1_7,
    EAN13_D1_8,
    EAN13_D1_9,
)

__all__ = [
    "EAN13_GOLDEN_VECTORS",
    "EAN13_D1_0",
    "EAN13_D1_1",
    "EAN13_D1_2",
    "EAN13_D1_3",
    "EAN13_D1_4",
    "EAN13_D1_5",
    "EAN13_D1_6",
    "EAN13_D1_7",
    "EAN13_D1_8",
    "EAN13_D1_9",
    "Ean13Vector",
]
