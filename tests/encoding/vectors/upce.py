"""UPC-E golden vectors used by encoding tests.

Each vector contains a 12-digit GTIN-12 input (including the check digit), the
expected 6-character compressed UPC-E data string, and the expected
51-character row-0 module string ('0'=space, '1'=bar).

PROVENANCE — TRUSTWORTHY GROUND TRUTH:
The ``expected_row0`` module strings are produced by the independent bwip-js / BWIPP
UPC-E encoder, NOT by this project's encoder.

bwip-js is a completely independent implementation of the symbology
specifications; it also rejects every non-suppressible GTIN-12 exactly where
``upce_zero_suppress`` returns ``None`` (BWIPP error ``upcEupcAnotCompressible``).

One vector is provided for each UPC-E mode digit (X6), so all four
zero-suppression branches of ``upce_zero_suppress`` are exercised:

- Mode 0/1/2: D4 ∈ {0,1,2}, D5=D6=D7=D8=0 → X = D2 D3 D9 D10 D11 D4
- Mode 3: D4 ∈ {3..9}, D5=D6=D7=D8=D9=0 → X = D2 D3 D4 D10 D11 "3"
- Mode 4: D5 ≠ 0, D6=D7=D8=D9=D10=0 → X = D2 D3 D4 D5 D11 "4"
- Mode 5..9: D6 ≠ 0, D7=D8=D9=D10=0, D11 ∈ {5..9} → X = D2 D3 D4 D5 D6 D11

The four inputs also span distinct check digits (5, 1, 7, 8), exercising
multiple rows of ``UPCE_PARITY``.

UPC-E row 0 structure (51 modules):
  NORMAL_GUARD (3) + 6 data characters × 7 modules (42) + SPECIAL_GUARD (6)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class UpceVector:
    """One known-good UPC-E fixture."""

    input_data: str
    """12-digit GTIN-12 string (11 data digits + 1 check digit, D1 = '0')."""

    expected_compressed: str
    """6-character UPC-E explicit data string (X1–X6) after zero suppression."""

    expected_row0: str
    """Expected 51-character module string for barcode row 0 ('0'=space, '1'=bar)."""


# ---------------------------------------------------------------------------
# Vectors — one per UPC-E mode digit (oracle: bwip-js / BWIPP)
# ---------------------------------------------------------------------------

# Mode 0/1/2: GTIN-12 0 12000 00345 5 → compressed "123450" (X6 = D4 = 0), check 5.
UPCE_MODE_012 = UpceVector(
    input_data="012000003455",
    expected_compressed="123450",
    expected_row0="101011001100100110111101001110101110010001101010101",
)

# Mode 3: GTIN-12 0 12300 00045 1 → compressed "123453" (X6 = "3"), check 1.
UPCE_MODE_3 = UpceVector(
    input_data="012300000451",
    expected_compressed="123453",
    expected_row0="101011001100110110111101001110101100010111101010101",
)

# Mode 4: GTIN-12 0 12340 00007 7 → compressed "123474" (X6 = "4"), check 7.
UPCE_MODE_4 = UpceVector(
    input_data="012340000077",
    expected_compressed="123474",
    expected_row0="101011001100100110100001010001100100010100011010101",
)

# Mode 5..9: GTIN-12 0 12345 00005 8 → compressed "123455" (X6 = D11 = 5), check 8.
UPCE_MODE_5_9 = UpceVector(
    input_data="012345000058",
    expected_compressed="123455",
    expected_row0="101011001100100110100001010001101100010111001010101",
)

# ---------------------------------------------------------------------------
# Aggregate collection — parametrize over this tuple in tests
# ---------------------------------------------------------------------------

UPCE_GOLDEN_VECTORS: tuple[UpceVector, ...] = (
    UPCE_MODE_012,
    UPCE_MODE_3,
    UPCE_MODE_4,
    UPCE_MODE_5_9,
)

__all__ = [
    "UPCE_GOLDEN_VECTORS",
    "UPCE_MODE_012",
    "UPCE_MODE_3",
    "UPCE_MODE_4",
    "UPCE_MODE_5_9",
    "UpceVector",
]
