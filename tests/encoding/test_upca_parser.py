"""Contract tests for UPC-A parser validation and normalization."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import EncodeOptions, UpcaOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.upca import UpcaInputParser


def test_upca_parser_computes_check_digit_from_11_digit_input() -> None:
    """11-digit input should have its check digit computed and appended automatically."""
    payload = UpcaInputParser().parse("03600029145")

    assert payload == NormalizedPayload(symbology="upca", data="036000291452", input_kind="text")


def test_upca_parser_accepts_second_known_11_digit_value() -> None:
    """A second known barcode verifies that check digit computation is not hard-coded."""
    payload = UpcaInputParser().parse("50000000000")

    assert payload == NormalizedPayload(symbology="upca", data="500000000005", input_kind="text")


def test_upca_parser_accepts_12_digit_input_when_flag_is_set() -> None:
    """12-digit input with a correct check digit should succeed when the flag is enabled."""
    payload = UpcaInputParser().parse(
        "036000291452",
        options=UpcaOptions(allow_check_digit_input=True),
    )

    assert payload == NormalizedPayload(symbology="upca", data="036000291452", input_kind="text")


def test_upca_parser_accepts_non_zero_first_digit() -> None:
    """UPC-A first digit values other than 0 must be accepted when the check digit is valid."""
    payload = UpcaInputParser().parse("50000000000")

    assert payload.data[0] == "5"
    assert payload.data == "500000000005"


def test_upca_parser_accepts_encode_options_base_type() -> None:
    """EncodeOptions (base type) should be accepted and coerced to UpcaOptions defaults."""
    payload = UpcaInputParser().parse("03600029145", options=EncodeOptions())

    assert payload.data == "036000291452"


def test_upca_parser_rejects_bytes_input() -> None:
    """UPC-A is a digit-only symbology and must not silently coerce bytes."""
    with pytest.raises(UnsupportedCapabilityError, match="bytes"):
        UpcaInputParser().parse(b"03600029145")  # type: ignore[arg-type]


def test_upca_parser_rejects_non_string_input() -> None:
    """Only text strings are valid; other types must be rejected with a clear error."""
    with pytest.raises(InvalidInputError, match="text string"):
        UpcaInputParser().parse(36000291452)  # type: ignore[arg-type]


def test_upca_parser_rejects_empty_string() -> None:
    """An empty string must not reach digit validation."""
    with pytest.raises(InvalidInputError, match="empty"):
        UpcaInputParser().parse("")


def test_upca_parser_rejects_whitespace_only_string() -> None:
    """Whitespace stripped to nothing is indistinguishable from an empty payload."""
    with pytest.raises(InvalidInputError, match="empty"):
        UpcaInputParser().parse(" ")


def test_upca_parser_rejects_non_digit_characters_and_reports_position() -> None:
    """Non-digit characters must be caught and the 1-based position must appear in the message."""
    with pytest.raises(InvalidInputError, match="position 4"):
        UpcaInputParser().parse("036A0029145")


def test_upca_parser_rejects_non_digit_characters_at_first_position() -> None:
    """A non-digit at position 1 should be reported correctly."""
    with pytest.raises(InvalidInputError, match="position 1"):
        UpcaInputParser().parse("X3600029145")


def test_upca_parser_rejects_non_ascii_digits() -> None:
    """Unicode decimal digits are not valid UPC-A input characters."""
    with pytest.raises(InvalidInputError, match="position 11"):
        UpcaInputParser().parse("0360002914\u0665")


def test_upca_parser_rejects_wrong_length() -> None:
    """10-digit input is neither the 11-digit nor the 12-digit accepted form."""
    with pytest.raises(InvalidInputError, match="11 or 12 digits"):
        UpcaInputParser().parse("0360002914")


@pytest.mark.parametrize("length", [1, 9, 10, 13, 20])
def test_upca_parser_rejects_various_wrong_lengths(length: int) -> None:
    """Any digit-only string that is neither 11 nor 12 characters must be rejected."""
    data = "1" * length
    with pytest.raises(InvalidInputError, match="11 or 12 digits"):
        UpcaInputParser().parse(data)


def test_upca_parser_rejects_12_digit_input_without_flag() -> None:
    """12-digit input is rejected by default; the message must name the enabling flag."""
    with pytest.raises(InvalidInputError, match="allow_check_digit_input"):
        UpcaInputParser().parse("036000291452")


def test_upca_parser_rejects_wrong_check_digit_when_flag_is_set() -> None:
    """A 12-digit string with an incorrect check digit must fail even with the flag enabled."""
    with pytest.raises(InvalidInputError, match="mismatch"):
        UpcaInputParser().parse(
            "036000291459",
            options=UpcaOptions(allow_check_digit_input=True),
        )


@pytest.mark.parametrize(
    ("options", "message_fragment"),
    [
        (UpcaOptions(gs1_enabled=True), "GS1"),
        (EncodeOptions(eci_assignment_number=26), "ECI"),
    ],
)
def test_upca_parser_rejects_unsupported_capabilities(
    options: UpcaOptions | EncodeOptions,
    message_fragment: str,
) -> None:
    """Requesting unsupported capabilities should raise a typed capability error."""
    with pytest.raises(UnsupportedCapabilityError, match=message_fragment):
        UpcaInputParser().parse("03600029145", options=options)


@pytest.mark.parametrize("options", [object(), [], {}])
def test_upca_parser_rejects_unsupported_option_containers(options: object) -> None:
    """Only the documented option container types should be accepted."""
    with pytest.raises(InvalidInputError, match="encode options"):
        UpcaInputParser().parse("03600029145", options=options)  # type: ignore[arg-type]
