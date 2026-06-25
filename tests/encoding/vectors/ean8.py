"""EAN-8 golden vectors used by encoding tests.

Each vector contains an 8-digit input string (the full8, including the check
digit) and the expected row-0 module string (67 characters of '0' and '1').

PROVENANCE: the expected module strings are verified against the independent
bwip-js / BWIPP ``ean8`` encoder, NOT this project's encoder.

The seven vectors are the canonical bwip-js/BWIPP ``ean8`` reference outputs and
exercise a spread of digit values across both halves of the symbol.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Ean8Vector:
    """One known-good EAN-8 fixture."""

    input_data: str
    """8-digit GTIN-8 string (7 data digits + 1 check digit)."""

    expected_row0: str
    """Expected 67-character module string for barcode row 0 ('0'=space, '1'=bar)."""


# ---------------------------------------------------------------------------
# Vectors — oracle-sourced (bwip-js / BWIPP bcid ``ean8``)
# ---------------------------------------------------------------------------
# Structure: NORMAL_GUARD(3) + left_half(28) + CENTRE_GUARD(5) + right_half(28) + NORMAL_GUARD(3) = 67 modules

EAN8_00000000 = Ean8Vector(
    input_data="00000000",
    expected_row0="1010001101000110100011010001101010101110010111001011100101110010101",
)

EAN8_12345670 = Ean8Vector(
    input_data="12345670",
    expected_row0="1010011001001001101111010100011010101001110101000010001001110010101",
)

EAN8_55123457 = Ean8Vector(
    input_data="55123457",
    expected_row0="1010110001011000100110010010011010101000010101110010011101000100101",
)

EAN8_96385074 = Ean8Vector(
    input_data="96385074",
    expected_row0="1010001011010111101111010110111010101001110111001010001001011100101",
)

EAN8_04210009 = Ean8Vector(
    input_data="04210009",
    expected_row0="1010001101010001100100110011001010101110010111001011100101110100101",
)

EAN8_20000004 = Ean8Vector(
    input_data="20000004",
    expected_row0="1010010011000110100011010001101010101110010111001011100101011100101",
)

EAN8_40063812 = Ean8Vector(
    input_data="40063812",
    expected_row0="1010100011000110100011010101111010101000010100100011001101101100101",
)

# ---------------------------------------------------------------------------
# Aggregate collection — parametrize over this tuple in tests
# ---------------------------------------------------------------------------

EAN8_GOLDEN_VECTORS: tuple[Ean8Vector, ...] = (
    EAN8_00000000,
    EAN8_12345670,
    EAN8_55123457,
    EAN8_96385074,
    EAN8_04210009,
    EAN8_20000004,
    EAN8_40063812,
)

__all__ = [
    "EAN8_GOLDEN_VECTORS",
    "EAN8_00000000",
    "EAN8_12345670",
    "EAN8_55123457",
    "EAN8_96385074",
    "EAN8_04210009",
    "EAN8_20000004",
    "EAN8_40063812",
    "Ean8Vector",
]
