"""EAN/UPC shared standards: character tables, guard patterns, parity tables,
check digit algorithm, ISO height constants, and UPC-E zero suppression.

Single source of truth for EAN-13, UPC-A, and UPC-E encoding constants and
pure helper functions. This module must remain free of imports from parsers,
encoders, renderers, options, or registry code.

References: ISO/IEC 15420:2009 (identical to ГОСТ ISO/IEC 15420-2010), §§4.2.2,
4.2.3, 4.3, Appendix A.1.
"""

from __future__ import annotations

from typing import Final, Literal

# ---------------------------------------------------------------------------
# Number sets (character tables)
# ---------------------------------------------------------------------------

# Number Set A — odd parity, starts with a space module.
# Each entry is (space1, bar1, space2, bar2) widths in modules for digits 0–9.
# Source: ISO 15420:2009 §4.2.2.1, Table 1.
SET_A: Final[tuple[tuple[int, int, int, int], ...]] = (
    (3, 2, 1, 1),  # 0
    (2, 2, 2, 1),  # 1
    (2, 1, 2, 2),  # 2
    (1, 4, 1, 1),  # 3
    (1, 1, 3, 2),  # 4
    (1, 2, 3, 1),  # 5
    (1, 1, 1, 4),  # 6
    (1, 3, 1, 2),  # 7
    (1, 2, 1, 3),  # 8
    (3, 1, 1, 2),  # 9
)

# Number Set B — even parity, starts with a space module.
# Each entry is (space1, bar1, space2, bar2) widths in modules for digits 0–9.
# Source: ISO 15420:2009 §4.2.2.1, Table 1.
SET_B: Final[tuple[tuple[int, int, int, int], ...]] = (
    (1, 1, 2, 3),  # 0
    (1, 2, 2, 2),  # 1
    (2, 2, 1, 2),  # 2
    (1, 1, 4, 1),  # 3
    (2, 3, 1, 1),  # 4
    (1, 3, 2, 1),  # 5
    (4, 1, 1, 1),  # 6
    (2, 1, 3, 1),  # 7
    (3, 1, 2, 1),  # 8
    (2, 1, 1, 3),  # 9
)

# Number Set C — even parity, starts with a bar module.
# Width values are identical to Set A; polarity is inverted (bar-space-bar-space).
# encode_digit() handles the polarity inversion; SET_C is an alias for SET_A.
# Source: ISO 15420:2009 §4.2.2.1, Table 1.
SET_C: Final[tuple[tuple[int, int, int, int], ...]] = SET_A

# ---------------------------------------------------------------------------
# Guard patterns (flat 0/1 module sequences: 0=space, 1=bar)
# ---------------------------------------------------------------------------

# Normal guard — left guard and right guard for EAN-13, UPC-A, EAN-8, UPC-E.
# Source: ISO 15420:2009 §4.2.2.2, Table 2 ("Normal guard pattern").
NORMAL_GUARD: Final[tuple[int, ...]] = (1, 0, 1)

# Centre guard — separates left and right halves in EAN-13, UPC-A, EAN-8.
# Source: ISO 15420:2009 §4.2.2.2, Table 2 ("Centre guard pattern").
CENTRE_GUARD: Final[tuple[int, ...]] = (0, 1, 0, 1, 0)

# Special guard — right guard for UPC-E (6 modules instead of 3).
# Source: ISO 15420:2009 §4.2.2.2, Table 2 ("Special guard pattern").
SPECIAL_GUARD: Final[tuple[int, ...]] = (0, 1, 0, 1, 0, 1)

# ---------------------------------------------------------------------------
# Parity tables
# ---------------------------------------------------------------------------

# EAN-13 left-half parity: indexed by the first (implied) digit.
# Each entry is a 6-tuple of "A" or "B" selecting the number set for left-half
# characters (positions 2–7 of the 13-digit GTIN-13).
# Row 0 (first digit = 0) is identical to UPC-A left-half encoding (all Set A).
# Source: ISO 15420:2009 §4.2.3.1, Table 3.
EAN13_PARITY: Final[tuple[tuple[str, ...], ...]] = (
    ("A", "A", "A", "A", "A", "A"),  # 0 — equivalent to UPC-A
    ("A", "A", "B", "A", "B", "B"),  # 1
    ("A", "A", "B", "B", "A", "B"),  # 2
    ("A", "A", "B", "B", "B", "A"),  # 3
    ("A", "B", "A", "A", "B", "B"),  # 4
    ("A", "B", "B", "A", "A", "B"),  # 5
    ("A", "B", "B", "B", "A", "A"),  # 6
    ("A", "B", "A", "B", "A", "B"),  # 7
    ("A", "B", "A", "B", "B", "A"),  # 8
    ("A", "B", "B", "A", "B", "A"),  # 9
)

# UPC-E parity: indexed by the UPC-A check digit (D12).
# Each entry is a 6-tuple of "A" or "B" selecting the number set for the 6
# UPC-E explicit data characters (X1–X6).
# Source: ISO 15420:2009 §4.2.3.4.2, Table 4.
UPCE_PARITY: Final[tuple[tuple[str, ...], ...]] = (
    ("B", "B", "B", "A", "A", "A"),  # 0
    ("B", "B", "A", "B", "A", "A"),  # 1
    ("B", "B", "A", "A", "B", "A"),  # 2
    ("B", "B", "A", "A", "A", "B"),  # 3
    ("B", "A", "B", "B", "A", "A"),  # 4
    ("B", "A", "A", "B", "B", "A"),  # 5
    ("B", "A", "A", "A", "B", "B"),  # 6
    ("B", "A", "B", "A", "B", "A"),  # 7
    ("B", "A", "B", "A", "A", "B"),  # 8
    ("B", "A", "A", "B", "A", "B"),  # 9
)

# ---------------------------------------------------------------------------
# ISO 15420 dimensional constants (in X-module units)
# ---------------------------------------------------------------------------

# Nominal bar height for EAN-13, UPC-A, and UPC-E: 22.85 mm / 0.330 mm ≈ 69.242X.
# Source: ISO 15420:2009 §4.3.3.
EAN_BAR_HEIGHT_X: Final[float] = 22.85 / 0.330

# Nominal bar height for EAN-8: 18.23 mm / 0.330 mm ≈ 55.242X.
# Distinct from EAN_BAR_HEIGHT_X (22.85 mm) used by EAN-13/UPC-A/UPC-E.
# Source: ISO 15420:2009 §4.3.3.
EAN8_BAR_HEIGHT_X: Final[float] = 18.23 / 0.330

# Guard bar extension below the data bars: 5X.
# Applies to normal guard, centre guard, and special guard patterns, and
# additionally to the first and last data character positions in UPC-A.
# Source: ISO 15420:2009 §4.3.3.
EAN_GUARD_EXTENSION_X: Final[float] = 5.0

# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------


def _is_ascii_digits(value: str) -> bool:
    """Return True when every character is an ASCII decimal digit."""
    return all("0" <= character <= "9" for character in value)


def encode_digit(digit: int, number_set: Literal["A", "B", "C"]) -> tuple[int, ...]:
    """Return the flat 0/1 module sequence for *digit* in *number_set*.

    Set A and Set B both start with a space module (0) and alternate space/bar.
    Set C starts with a bar module (1) and alternates bar/space. Set C uses
    the same width table as Set A but reads the tuple as (bar1, space1, bar2,
    space2) instead of (space1, bar1, space2, bar2).

    Returns a tuple of exactly 7 integers, each ``0`` (space) or ``1`` (bar).

    Raises:
        ValueError: if *digit* is not in the range 0–9 or *number_set* is not
            one of ``"A"``, ``"B"``, ``"C"``.
    """
    if not isinstance(digit, int) or isinstance(digit, bool) or not (0 <= digit <= 9):
        raise ValueError(f"digit must be an integer in 0–9, got {digit!r}")
    if number_set not in ("A", "B", "C"):
        raise ValueError(f"number_set must be 'A', 'B', or 'C', got {number_set!r}")

    if number_set == "A":
        s1, b1, s2, b2 = SET_A[digit]
        return (0,) * s1 + (1,) * b1 + (0,) * s2 + (1,) * b2
    if number_set == "B":
        s1, b1, s2, b2 = SET_B[digit]
        return (0,) * s1 + (1,) * b1 + (0,) * s2 + (1,) * b2
    # number_set == "C": same widths as Set A, but polarity is bar-space-bar-space
    b1, s1, b2, s2 = SET_C[digit]
    return (1,) * b1 + (0,) * s1 + (1,) * b2 + (0,) * s2


def compute_check_digit(digits: str, *, start_weight: int) -> int:
    """Compute the modulo-10 EAN/UPC check digit for a string of data digits.

    Weights alternate between *start_weight* and ``4 - start_weight`` from
    left to right. The check digit is ``(10 - (total % 10)) % 10``.

    Typical usage:
    - GTIN-13 (EAN-13): pass the 12 data digits with ``start_weight=1``.
      Weights are 1, 3, 1, 3, … from left to right.
    - GTIN-12 (UPC-A / UPC-E): pass the 11 data digits with ``start_weight=3``.
      Weights are 3, 1, 3, 1, … from left to right.

    Args:
        digits: Non-empty string of ASCII decimal characters ('0'–'9').
        start_weight: Must be ``1`` or ``3``.

    Returns:
        Integer in the range 0–9.

    Raises:
        ValueError: if *start_weight* is not ``1`` or ``3``, if *digits* is
            empty, or if *digits* contains any non-digit character.
    """
    if start_weight not in (1, 3):
        raise ValueError(f"start_weight must be 1 or 3, got {start_weight!r}")
    if not digits:
        raise ValueError("digits must be a non-empty string")
    if not _is_ascii_digits(digits):
        raise ValueError(f"digits must contain only ASCII decimal digits, got {digits!r}")

    other_weight = 4 - start_weight
    total = sum(int(digits[i]) * (start_weight if i % 2 == 0 else other_weight) for i in range(len(digits)))
    return (10 - (total % 10)) % 10


def upce_zero_suppress(gtin12: str) -> str | None:
    """Apply ISO 15420 zero-suppression to a 12-digit GTIN-12.

    Returns the 6-character UPC-E explicit data string (X1–X6) when the
    GTIN-12 is suppressible, or ``None`` when none of the rules match.

    This function does **not** validate that ``gtin12[0] == '0'``; the
    caller (parser) is responsible for that check.

    The input designations follow ISO 15420 §4.2.3.4.2 (1-based):
    D1=``gtin12[0]`` (number system), D2..D6=``gtin12[1:6]`` (manufacturer),
    D7..D11=``gtin12[6:11]`` (product), D12=``gtin12[11]`` (check).

    The last UPC-E digit (X6) is a *mode* digit that drives the inverse
    expansion. The four mutually exclusive rules (first match wins) are:

    - Mode 0/1/2: D4 ∈ {0,1,2} and D5=D6=D7=D8=0
      → X = D2 D3 D9 D10 D11 D4
    - Mode 3: D4 ∈ {3..9} and D5=D6=D7=D8=D9=0
      → X = D2 D3 D4 D10 D11 "3"
    - Mode 4: D5 ≠ 0 and D6=D7=D8=D9=D10=0
      → X = D2 D3 D4 D5 D11 "4"
    - Mode 5..9: D6 ≠ 0 and D7=D8=D9=D10=0 and D11 ∈ {5..9}
      → X = D2 D3 D4 D5 D6 D11

    Verified against the bwip-js / BWIPP UPC-E encoder (the independent
    oracle): non-suppressible GTIN-12 inputs return ``None`` exactly where
    BWIPP raises ``upcEupcAnotCompressible``.

    Args:
        gtin12: Exactly 12 ASCII decimal digits.

    Returns:
        A 6-character string (the UPC-E explicit data digits), or ``None``.

    Raises:
        ValueError: if *gtin12* is not a 12-digit string.
    """
    if not isinstance(gtin12, str) or len(gtin12) != 12 or not _is_ascii_digits(gtin12):
        raise ValueError(f"gtin12 must be a 12-digit string, got {gtin12!r}")

    # 0-based indexing: D1=g[0], D2=g[1], ..., D12=g[11].
    g = gtin12
    d4, d5, d6, d7, d8, d9, d10, d11 = g[3], g[4], g[5], g[6], g[7], g[8], g[9], g[10]

    # Mode 0/1/2: D4 ∈ {0,1,2}, D5=D6=D7=D8=0.
    if d4 in "012" and d5 == "0" and d6 == "0" and d7 == "0" and d8 == "0":
        return g[1] + g[2] + d9 + d10 + d11 + d4

    # Mode 3: D4 ∈ {3..9}, D5=D6=D7=D8=D9=0.
    if d4 in "3456789" and d5 == "0" and d6 == "0" and d7 == "0" and d8 == "0" and d9 == "0":
        return g[1] + g[2] + d4 + d10 + d11 + "3"

    # Mode 4: D5 ≠ 0, D6=D7=D8=D9=D10=0.
    if d5 != "0" and d6 == "0" and d7 == "0" and d8 == "0" and d9 == "0" and d10 == "0":
        return g[1] + g[2] + d4 + d5 + d11 + "4"

    # Mode 5..9: D6 ≠ 0, D7=D8=D9=D10=0, D11 ∈ {5..9}.
    if d6 != "0" and d7 == "0" and d8 == "0" and d9 == "0" and d10 == "0" and d11 in "56789":
        return g[1] + g[2] + d4 + d5 + d6 + d11

    return None


__all__ = [
    "CENTRE_GUARD",
    "EAN8_BAR_HEIGHT_X",
    "EAN13_PARITY",
    "EAN_BAR_HEIGHT_X",
    "EAN_GUARD_EXTENSION_X",
    "NORMAL_GUARD",
    "SET_A",
    "SET_B",
    "SET_C",
    "SPECIAL_GUARD",
    "UPCE_PARITY",
    "compute_check_digit",
    "encode_digit",
    "upce_zero_suppress",
]
