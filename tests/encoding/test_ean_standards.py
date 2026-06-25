"""Contract tests for the shared EAN/UPC standards module."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.standards.ean import (
    EAN13_PARITY,
    EAN_BAR_HEIGHT_X,
    EAN_GUARD_EXTENSION_X,
    UPCE_PARITY,
    compute_check_digit,
    encode_digit,
    upce_zero_suppress,
)


# ---------------------------------------------------------------------------
# compute_check_digit — GTIN-13 (start_weight=1)
# ---------------------------------------------------------------------------


def test_compute_check_digit_gtin13_known_value() -> None:
    assert compute_check_digit("400638133393", start_weight=1) == 1


# ---------------------------------------------------------------------------
# compute_check_digit — GTIN-12 (start_weight=3)
# ---------------------------------------------------------------------------


def test_compute_check_digit_gtin12_known_value() -> None:
    # UPC-A "012345678905": check digit of 11-digit stem "01234567890" is 5
    assert compute_check_digit("01234567890", start_weight=3) == 5


# ---------------------------------------------------------------------------
# compute_check_digit — invalid inputs raise ValueError
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("digits", "start_weight", "description"),
    [
        ("400638133393", 2, "start_weight=2 is not 1 or 3"),
        ("400638133393", 0, "start_weight=0 is not 1 or 3"),
        ("400638133393", 4, "start_weight=4 is not 1 or 3"),
        ("", 1, "empty digits string"),
        ("40063X133393", 1, "non-digit character in input"),
        ("4006 8133393", 1, "space character in input"),
        ("40063813339\u0663", 1, "non-ASCII digit in input"),
    ],
)
def test_compute_check_digit_raises_value_error_on_invalid_input(
    digits: str,
    start_weight: int,
    description: str,
) -> None:
    with pytest.raises(ValueError):
        compute_check_digit(digits, start_weight=start_weight)


# ---------------------------------------------------------------------------
# encode_digit — spot-check known module sequences
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("digit", "number_set", "expected"),
    [
        # Set A: starts with space (0), pattern = (0,)*s1 + (1,)*b1 + (0,)*s2 + (1,)*b2
        # SET_A[0] = (3,2,1,1) → 000 11 0 1
        (0, "A", (0, 0, 0, 1, 1, 0, 1)),
        # SET_A[9] = (3,1,1,2) → 000 1 0 11
        (9, "A", (0, 0, 0, 1, 0, 1, 1)),
        # Set B: starts with space (0), pattern = (0,)*s1 + (1,)*b1 + (0,)*s2 + (1,)*b2
        # SET_B[0] = (1,1,2,3) → 0 1 00 111
        (0, "B", (0, 1, 0, 0, 1, 1, 1)),
        # SET_B[9] = (2,1,1,3) → 00 1 0 111
        (9, "B", (0, 0, 1, 0, 1, 1, 1)),
        # Set C: starts with bar (1), same widths as Set A read as (b1,s1,b2,s2)
        # SET_C[0] uses SET_A[0]=(3,2,1,1) → 111 00 1 0
        (0, "C", (1, 1, 1, 0, 0, 1, 0)),
        # SET_C[9] uses SET_A[9]=(3,1,1,2) → 111 0 1 00
        (9, "C", (1, 1, 1, 0, 1, 0, 0)),
    ],
)
def test_encode_digit_known_module_sequence(
    digit: int,
    number_set: str,
    expected: tuple[int, ...],
) -> None:
    assert encode_digit(digit, number_set) == expected  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# encode_digit — structural invariants for all digits in all sets
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("number_set", ["A", "B", "C"])
@pytest.mark.parametrize("digit", range(10))
def test_encode_digit_has_length_7_and_binary_values(digit: int, number_set: str) -> None:
    result = encode_digit(digit, number_set)  # type: ignore[arg-type]
    assert len(result) == 7
    assert set(result) <= {0, 1}


# ---------------------------------------------------------------------------
# Parity table dimensions
# ---------------------------------------------------------------------------


def test_ean13_parity_has_10_entries_of_6_values_each() -> None:
    assert len(EAN13_PARITY) == 10
    for entry in EAN13_PARITY:
        assert len(entry) == 6


def test_upce_parity_has_10_entries_of_6_values_each() -> None:
    assert len(UPCE_PARITY) == 10
    for entry in UPCE_PARITY:
        assert len(entry) == 6


# ---------------------------------------------------------------------------
# EAN height constants are positive
# ---------------------------------------------------------------------------


def test_ean_bar_height_x_is_positive() -> None:
    assert EAN_BAR_HEIGHT_X > 0


def test_ean_guard_extension_x_is_positive() -> None:
    assert EAN_GUARD_EXTENSION_X > 0


# ---------------------------------------------------------------------------
# upce_zero_suppress — mode digit X6 drives the suppression branch.
# Rules (1-based D positions; D1=number system, D2..D6=manufacturer,
# D7..D11=product) verified against the bwip-js / BWIPP oracle. The four
# GTIN-12 inputs that also appear in the golden vectors are oracle-confirmed
# encodable; the extra inputs here only exercise the branch logic (the
# function ignores the check digit D12).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("gtin12", "expected", "mode"),
    [
        # Mode 0/1/2: D4 ∈ {0,1,2}, D5=D6=D7=D8=0 → X = D2 D3 D9 D10 D11 D4
        ("012000003455", "123450", "mode 0 (oracle vector)"),
        ("012100006789", "126781", "mode 1"),
        ("012200000992", "120992", "mode 2"),
        # Mode 3: D4 ∈ {3..9}, D5=D6=D7=D8=D9=0 → X = D2 D3 D4 D10 D11 "3"
        ("012300000451", "123453", "mode 3 (oracle vector)"),
        ("019900000673", "199673", "mode 3"),
        # Mode 4: D5 ≠ 0, D6=D7=D8=D9=D10=0 → X = D2 D3 D4 D5 D11 "4"
        ("012340000077", "123474", "mode 4 (oracle vector)"),
        ("012340000054", "123454", "mode 4"),
        # Mode 5..9: D6 ≠ 0, D7=D8=D9=D10=0, D11 ∈ {5..9} → X = D2 D3 D4 D5 D6 D11
        ("012345000058", "123455", "mode 5-9 (oracle vector)"),
        ("012348000079", "123487", "mode 5-9"),
    ],
)
def test_upce_zero_suppress_per_mode(gtin12: str, expected: str, mode: str) -> None:
    assert upce_zero_suppress(gtin12) == expected, mode


# ---------------------------------------------------------------------------
# upce_zero_suppress — non-suppressible inputs return None.
# bwip-js / BWIPP rejects each of these with `upcEupcAnotCompressible`; the
# first three previously produced bogus output under the old (wrong) rules.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "gtin12",
    [
        "012345000003",  # D6≠0 but D11=0 (no mode 5-9), not mode 4 (D6≠0)
        "012345600005",  # D7=6≠0 → no leading-zeros product run
        "012345800009",  # D7=8≠0 → no leading-zeros product run
        "012345678901",  # arbitrary product, matches no rule
        "012345300000",  # D6=5, D7=3≠0 → matches no rule
    ],
)
def test_upce_zero_suppress_returns_none_for_non_suppressible_input(gtin12: str) -> None:
    assert upce_zero_suppress(gtin12) is None


def test_upce_zero_suppress_rejects_non_ascii_digits() -> None:
    """UPC-E zero suppression requires ASCII digits, not Unicode decimal characters."""
    with pytest.raises(ValueError):
        upce_zero_suppress("01234500000\u0663")
