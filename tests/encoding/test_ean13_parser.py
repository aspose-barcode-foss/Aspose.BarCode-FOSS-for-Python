"""Contract tests for EAN-13 parser validation and normalization."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import Ean13Options, EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.ean13 import Ean13InputParser


def test_ean13_parser_computes_check_digit_from_12_digit_input() -> None:
    """12-digit input should have its check digit computed and appended automatically."""
    payload = Ean13InputParser().parse("400638133393")

    assert payload == NormalizedPayload(symbology="ean13", data="4006381333931", input_kind="text")


def test_ean13_parser_accepts_second_known_12_digit_value() -> None:
    """A second known barcode verifies that check digit computation is not hard-coded."""
    payload = Ean13InputParser().parse("590123412345")

    assert payload == NormalizedPayload(symbology="ean13", data="5901234123457", input_kind="text")


def test_ean13_parser_accepts_13_digit_input_when_flag_is_set() -> None:
    """13-digit input with a correct check digit should succeed when the flag is enabled."""
    payload = Ean13InputParser().parse(
        "4006381333931",
        options=Ean13Options(allow_check_digit_input=True),
    )

    assert payload == NormalizedPayload(symbology="ean13", data="4006381333931", input_kind="text")


def test_ean13_parser_accepts_encode_options_base_type() -> None:
    """EncodeOptions (base type) should be accepted and coerced to Ean13Options defaults."""
    payload = Ean13InputParser().parse("400638133393", options=EncodeOptions())

    assert payload.data == "4006381333931"


def test_ean13_parser_rejects_bytes_input() -> None:
    """EAN-13 is a digit-only symbology and must not silently coerce bytes."""
    with pytest.raises(UnsupportedCapabilityError, match="bytes"):
        Ean13InputParser().parse(b"400638133393")  # type: ignore[arg-type]


def test_ean13_parser_rejects_non_string_input() -> None:
    """Only text strings are valid; other types must be rejected with a clear error."""
    with pytest.raises(InvalidInputError, match="text string"):
        Ean13InputParser().parse(400638133393)  # type: ignore[arg-type]


def test_ean13_parser_rejects_empty_string() -> None:
    """An empty (or whitespace-only) string must not reach digit validation."""
    with pytest.raises(InvalidInputError, match="empty"):
        Ean13InputParser().parse("")


def test_ean13_parser_rejects_whitespace_only_string() -> None:
    """Whitespace stripped to nothing is indistinguishable from an empty payload."""
    with pytest.raises(InvalidInputError, match="empty"):
        Ean13InputParser().parse(" ")


def test_ean13_parser_rejects_non_digit_characters_and_reports_position() -> None:
    """Non-digit characters must be caught and the 1-based position must appear in the message."""
    with pytest.raises(InvalidInputError, match="position 4"):
        Ean13InputParser().parse("400A38133393")


def test_ean13_parser_rejects_non_digit_characters_at_first_position() -> None:
    """A non-digit at position 1 should be reported correctly."""
    with pytest.raises(InvalidInputError, match="position 1"):
        Ean13InputParser().parse("X00638133393")


def test_ean13_parser_rejects_non_ascii_digits() -> None:
    """Unicode decimal digits are not valid EAN-13 input characters."""
    with pytest.raises(InvalidInputError, match="position 12"):
        Ean13InputParser().parse("40063813339\u0663")


def test_ean13_parser_rejects_wrong_length() -> None:
    """10-digit input is neither the 12-digit nor the 13-digit accepted form."""
    with pytest.raises(InvalidInputError, match="12 or 13 digits"):
        Ean13InputParser().parse("4006381333")


@pytest.mark.parametrize("length", [1, 11, 14, 20])
def test_ean13_parser_rejects_various_wrong_lengths(length: int) -> None:
    """Any digit-only string that is neither 12 nor 13 characters must be rejected."""
    data = "1" * length
    with pytest.raises(InvalidInputError, match="12 or 13 digits"):
        Ean13InputParser().parse(data)


def test_ean13_parser_rejects_13_digit_input_without_flag() -> None:
    """13-digit input is rejected by default; the message must name the enabling flag."""
    with pytest.raises(InvalidInputError, match="allow_check_digit_input"):
        Ean13InputParser().parse("4006381333931")


def test_ean13_parser_rejects_wrong_check_digit_when_flag_is_set() -> None:
    """A 13-digit string with an incorrect check digit must fail even with the flag enabled."""
    with pytest.raises(InvalidInputError, match="mismatch"):
        Ean13InputParser().parse(
            "4006381333939",
            options=Ean13Options(allow_check_digit_input=True),
        )


@pytest.mark.parametrize(
    ("options", "message_fragment"),
    [
        (Ean13Options(gs1_enabled=True), "GS1"),
        (EncodeOptions(eci_assignment_number=26), "ECI"),
    ],
)
def test_ean13_parser_rejects_unsupported_capabilities(
    options: Ean13Options | EncodeOptions,
    message_fragment: str,
) -> None:
    """Requesting unsupported capabilities should raise a typed capability error."""
    with pytest.raises(UnsupportedCapabilityError, match=message_fragment):
        Ean13InputParser().parse("400638133393", options=options)


@pytest.mark.parametrize("options", [object(), [], {}])
def test_ean13_parser_rejects_unsupported_option_containers(options: object) -> None:
    """Only the documented option container types should be accepted."""
    with pytest.raises(InvalidInputError, match="encode options"):
        Ean13InputParser().parse("400638133393", options=options)  # type: ignore[arg-type]
