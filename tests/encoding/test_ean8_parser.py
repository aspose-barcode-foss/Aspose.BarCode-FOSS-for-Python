"""Contract tests for EAN-8 parser validation and normalization."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import Ean8Options, EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.ean8 import Ean8InputParser


def test_ean8_parser_computes_check_digit_from_7_digit_input() -> None:
    """A 7-digit value gets its check digit computed and appended."""
    payload = Ean8InputParser().parse("5512345")
    assert payload == NormalizedPayload(symbology="ean8", data="55123457", input_kind="text")


def test_ean8_parser_computes_check_digit_for_second_value() -> None:
    """A second 7-digit value confirms the check digit is computed, not hard-coded."""
    payload = Ean8InputParser().parse("1234567")
    assert payload.data == "12345670"


def test_ean8_parser_accepts_8_digit_input_when_flag_is_set() -> None:
    """An 8-digit value with a valid check digit is accepted when the flag is set."""
    payload = Ean8InputParser().parse("55123457", options=Ean8Options(allow_check_digit_input=True))
    assert payload == NormalizedPayload(symbology="ean8", data="55123457", input_kind="text")


def test_ean8_parser_accepts_encode_options_base_type() -> None:
    """The base EncodeOptions type is accepted and coerced."""
    payload = Ean8InputParser().parse("5512345", options=EncodeOptions())
    assert payload.data == "55123457"


def test_ean8_parser_rejects_bytes_input() -> None:
    """Bytes input is unsupported for EAN-8."""
    with pytest.raises(UnsupportedCapabilityError, match="bytes"):
        Ean8InputParser().parse(b"5512345")  # type: ignore[arg-type]


def test_ean8_parser_rejects_non_string_input() -> None:
    """Non-string, non-bytes input is rejected as invalid."""
    with pytest.raises(InvalidInputError, match="text string"):
        Ean8InputParser().parse(5512345)  # type: ignore[arg-type]


def test_ean8_parser_rejects_empty_string() -> None:
    """An empty string is rejected."""
    with pytest.raises(InvalidInputError, match="empty"):
        Ean8InputParser().parse("")


def test_ean8_parser_rejects_whitespace_only_string() -> None:
    """A whitespace-only string is treated as empty and rejected."""
    with pytest.raises(InvalidInputError, match="empty"):
        Ean8InputParser().parse(" ")


def test_ean8_parser_rejects_non_digit_at_last_position() -> None:
    """A non-digit character is reported with its 1-based position."""
    with pytest.raises(InvalidInputError, match="position 7"):
        Ean8InputParser().parse("551234X")


def test_ean8_parser_rejects_non_digit_at_first_position() -> None:
    """A leading non-digit character is reported at position 1."""
    with pytest.raises(InvalidInputError, match="position 1"):
        Ean8InputParser().parse("X512345")


@pytest.mark.parametrize("length", [1, 6, 9, 20])
def test_ean8_parser_rejects_various_wrong_lengths(length: int) -> None:
    """Digit strings of unsupported lengths are rejected."""
    data = "1" * length
    with pytest.raises(InvalidInputError, match="7 or 8 digits"):
        Ean8InputParser().parse(data)


def test_ean8_parser_rejects_8_digit_input_without_flag() -> None:
    """An 8-digit value requires the allow_check_digit_input flag."""
    with pytest.raises(InvalidInputError, match="allow_check_digit_input"):
        Ean8InputParser().parse("55123457")


def test_ean8_parser_rejects_wrong_check_digit_when_flag_is_set() -> None:
    """An 8-digit value with a wrong check digit is rejected as a mismatch."""
    with pytest.raises(InvalidInputError, match="mismatch"):
        Ean8InputParser().parse("20000003", options=Ean8Options(allow_check_digit_input=True))


@pytest.mark.parametrize(
    ("options", "message_fragment"),
    [
        (Ean8Options(gs1_enabled=True), "GS1"),
        (EncodeOptions(eci_assignment_number=26), "ECI"),
    ],
)
def test_ean8_parser_rejects_unsupported_capabilities(options: EncodeOptions, message_fragment: str) -> None:
    """Capability requests unsupported by EAN-8 are rejected."""
    with pytest.raises(UnsupportedCapabilityError, match=message_fragment):
        Ean8InputParser().parse("5512345", options=options)


@pytest.mark.parametrize("options", [object(), [], {}])
def test_ean8_parser_rejects_unsupported_option_containers(options: object) -> None:
    """Unsupported option container types are rejected."""
    with pytest.raises(InvalidInputError, match="encode options"):
        Ean8InputParser().parse("5512345", options=options)  # type: ignore[arg-type]
