"""UPC-A golden vectors used by encoding tests.

Each vector contains a 12-digit input string (including the check digit) and the
expected row-0 module string (95 characters of '0' and '1').

PROVENANCE: the ``expected_row0`` module strings are verified against the
independent bwip-js / BWIPP ``upca`` encoder, NOT this project's encoder.

UPC-A structure:
    NORMAL_GUARD(3) + 6×Set_A_digits(42) + CENTRE_GUARD(5) + 6×Set_C_digits(42) + NORMAL_GUARD(3) = 95 modules

Five vectors are provided covering first digits 0, 1, 3, 4, and 9, and last digits
5, 2, 6, 2, and 2 — ensuring the first and last data character extension ranges
(modules 3–9 and 85–91) are exercised with varied patterns.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UpcaVector:
    """One known-good UPC-A fixture."""

    input_data: str
    """12-digit GTIN-12 string (11 data digits + 1 check digit)."""

    expected_row0: str
    """Expected 95-character module string for barcode row 0 ('0'=space, '1'=bar)."""


# ---------------------------------------------------------------------------
# Vectors — varied first digits (D1) and last digits (D12)
# ---------------------------------------------------------------------------
# Module strings computed from ISO 15420:2009 character tables using:
# SET_A (space-bar-space-bar), SET_C (bar-space-bar-space, same widths as SET_A),
# NORMAL_GUARD=(1,0,1), CENTRE_GUARD=(0,1,0,1,0)
# Structure: NORMAL_GUARD(3) + left_half(42) + CENTRE_GUARD(5) + right_half(42) + NORMAL_GUARD(3) = 95 modules

UPCA_D1_0 = UpcaVector(
    input_data="012345678905",
    expected_row0="10100011010011001001001101111010100011011000101010101000010001001001000111010011100101001110101",
)

UPCA_D1_1 = UpcaVector(
    input_data="123456789012",
    expected_row0="10100110010010011011110101000110110001010111101010100010010010001110100111001011001101101100101",
)

UPCA_D1_3 = UpcaVector(
    input_data="312345678906",
    expected_row0="10101111010011001001001101111010100011011000101010101000010001001001000111010011100101010000101",
)

UPCA_D1_4 = UpcaVector(
    input_data="400638133932",
    expected_row0="10101000110001101000110101011110111101011011101010110011010000101000010111010010000101101100101",
)

UPCA_D1_9 = UpcaVector(
    input_data="978020137962",
    expected_row0="10100010110111011011011100011010010011000110101010110011010000101000100111010010100001101100101",
)

# ---------------------------------------------------------------------------
# Aggregate collection — parametrize over this tuple in tests
# ---------------------------------------------------------------------------

UPCA_GOLDEN_VECTORS: tuple[UpcaVector, ...] = (
    UPCA_D1_0,
    UPCA_D1_1,
    UPCA_D1_3,
    UPCA_D1_4,
    UPCA_D1_9,
)

__all__ = [
    "UPCA_GOLDEN_VECTORS",
    "UPCA_D1_0",
    "UPCA_D1_1",
    "UPCA_D1_3",
    "UPCA_D1_4",
    "UPCA_D1_9",
    "UpcaVector",
]
