"""Contract tests for UPC-E parser validation and normalization."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import EncodeOptions, UpceOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.upce import UpceInputParser


def test_upce_parser_accepts_11_digit_rule_2a_input() -> None:
    """11-digit input satisfying rule 2a (D6∈{0,1,2}, D7–D10='0000') should have check digit appended."""
    # D1=0,D2=1,D3=2,D4=0,D5=0,D6=0,D7-D10=0000,D11=1 → check=0
    payload = UpceInputParser().parse("01200000001")

    assert payload == NormalizedPayload(symbology="upce", data="012000000010", input_kind="text")


def test_upce_parser_accepts_11_digit_mode_3_input() -> None:
    """11-digit mode-3 input (D4∈{3..9}, D5=D6=D7=D8=D9=0) should have check digit appended."""
    # D1=0,D2=1,D3=2,D4=3,D5-D9=0,D10=4,D11=5 → check=1 (oracle-confirmed suppressible)
    payload = UpceInputParser().parse("01230000045")

    assert payload == NormalizedPayload(symbology="upce", data="012300000451", input_kind="text")


def test_upce_parser_accepts_11_digit_mode_4_input() -> None:
    """11-digit mode-4 input (D5≠0, D6=D7=D8=D9=D10=0) should have check digit appended."""
    # D1=0,D2=1,D3=2,D4=3,D5=4,D6-D10=0,D11=7 → check=7 (oracle-confirmed suppressible)
    payload = UpceInputParser().parse("01234000007")

    assert payload == NormalizedPayload(symbology="upce", data="012340000077", input_kind="text")


def test_upce_parser_accepts_12_digit_input_with_flag() -> None:
    """12-digit input with a correct check digit should succeed when allow_check_digit_input is set."""
    # Mode 5-9 (oracle-confirmed suppressible): 0 12345 00005 → check 8.
    payload = UpceInputParser().parse(
        "012345000058",
        options=UpceOptions(allow_check_digit_input=True),
    )

    assert payload == NormalizedPayload(symbology="upce", data="012345000058", input_kind="text")


def test_upce_parser_rejects_number_system_option_1() -> None:
    """number_system='1' must be rejected because UPC-E only supports number system '0'."""
    with pytest.raises(InvalidInputError, match="number system"):
        UpceInputParser().parse("01234500000", options=UpceOptions(number_system="1"))


def test_upce_parser_rejects_non_zero_first_digit() -> None:
    """A GTIN-12 whose first digit is not '0' must be rejected after check digit resolution."""
    # "11234500000" → D1='1', check=compute_check_digit("11234500000")
    with pytest.raises(InvalidInputError, match="number system digit 0"):
        UpceInputParser().parse("11234500000")


def test_upce_parser_rejects_non_suppressible_gtin12() -> None:
    """A GTIN-12 that cannot be zero-suppressed must be rejected with a clear message."""
    # "01234567890" with check=5 → "012345678905": D7=6 but D8-D11="7890" ≠ "0000"
    with pytest.raises(InvalidInputError, match="zero-suppressed"):
        UpceInputParser().parse(
            "012345678905",
            options=UpceOptions(allow_check_digit_input=True),
        )


def test_upce_parser_rejects_wrong_length() -> None:
    """Input that is neither 11 nor 12 digits must be rejected with a length error."""
    with pytest.raises(InvalidInputError, match="11 or 12 digits"):
        UpceInputParser().parse("012345")


def test_upce_parser_rejects_non_ascii_digits() -> None:
    """Unicode decimal digits are not valid UPC-E input characters."""
    with pytest.raises(InvalidInputError, match="position 11"):
        UpceInputParser().parse("0123450000\u0660")


@pytest.mark.parametrize("length", [1, 7, 10, 13, 20])
def test_upce_parser_rejects_various_wrong_lengths(length: int) -> None:
    """Any digit-only string that is neither 11 nor 12 characters must be rejected."""
    data = "0" * length
    with pytest.raises(InvalidInputError, match="11 or 12 digits"):
        UpceInputParser().parse(data)


def test_upce_parser_rejects_wrong_check_digit_with_flag() -> None:
    """A 12-digit string with an incorrect check digit must fail even with the flag enabled."""
    # "012345000003" is correct; changing the check to "9" makes it wrong
    with pytest.raises(InvalidInputError, match="mismatch"):
        UpceInputParser().parse(
            "012345000009",
            options=UpceOptions(allow_check_digit_input=True),
        )


def test_upce_parser_rejects_bytes_input() -> None:
    """UPC-E is a digit-only symbology and must not silently coerce bytes."""
    with pytest.raises(UnsupportedCapabilityError, match="bytes"):
        UpceInputParser().parse(b"01234500000")  # type: ignore[arg-type]


def test_upce_parser_rejects_gs1_enabled() -> None:
    """Requesting GS1 mode must raise an UnsupportedCapabilityError."""
    with pytest.raises(UnsupportedCapabilityError, match="GS1"):
        UpceInputParser().parse("01234500000", options=UpceOptions(gs1_enabled=True))


def test_upce_parser_rejects_eci_assignment_number() -> None:
    """Requesting an ECI assignment must raise an UnsupportedCapabilityError."""
    with pytest.raises(UnsupportedCapabilityError, match="ECI"):
        UpceInputParser().parse("01234500000", options=EncodeOptions(eci_assignment_number=26))
