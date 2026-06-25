"""Contract tests for Code 39 parser validation and normalization."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import (
    Code39EncodeMode,
    Code39Options,
    EncodeOptions,
)
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.code39 import Code39InputParser


def _base_parser() -> Code39InputParser:
    """Build a parser whose definition defaults to base (non Full-ASCII) mode."""
    return Code39InputParser(default_full_ascii=False, symbology_name="code39")


def _ext_parser() -> Code39InputParser:
    """Build a parser whose definition defaults to Full-ASCII mode."""
    return Code39InputParser(default_full_ascii=True, symbology_name="code39ext")


def test_code39_parser_accepts_base_text_with_full_payload_equality() -> None:
    """A simple base input should normalize into the exact Code 39 payload contract."""
    payload = _base_parser().parse("CODE 39")

    assert payload == NormalizedPayload(
        symbology="code39",
        data="CODE 39",
        input_kind="text",
        code39_encode_mode=Code39EncodeMode.BASE,
        code39_add_check_digit=False,
    )


def test_code39_parser_accepts_every_base_sub_group() -> None:
    """A digit, an uppercase letter and the base symbols should all be accepted in base mode."""
    data = "Z-. $/+%"

    payload = _base_parser().parse(data)

    assert payload.code39_encode_mode is Code39EncodeMode.BASE
    assert payload.data == data


def test_code39_parser_uses_definition_full_ascii_default() -> None:
    """The code39ext definition should default lowercase input to Full-ASCII mode."""
    payload = _ext_parser().parse("abc")

    assert payload.symbology == "code39ext"
    assert payload.code39_encode_mode is Code39EncodeMode.FULL_ASCII


def test_code39_parser_option_override_enables_full_ascii_on_base_definition() -> None:
    """An explicit full_ascii=True should flip a base definition into Full-ASCII mode."""
    payload = _base_parser().parse("abc", options=Code39Options(full_ascii=True))

    assert payload.code39_encode_mode is Code39EncodeMode.FULL_ASCII


def test_code39_parser_option_override_disables_full_ascii_on_ext_definition() -> None:
    """An explicit full_ascii=False should flip a Full-ASCII definition into base mode."""
    payload = _ext_parser().parse("ABC", options=Code39Options(full_ascii=False))

    assert payload.code39_encode_mode is Code39EncodeMode.BASE


def test_code39_parser_carries_check_digit_request() -> None:
    """A check-digit request should propagate onto the normalized payload."""
    payload = _base_parser().parse("ABC", options=Code39Options(add_check_digit=True))

    assert payload.code39_add_check_digit is True


def test_code39_parser_defaults_check_digit_to_false() -> None:
    """Without an explicit request the payload should report no check digit."""
    payload = _base_parser().parse("ABC")

    assert payload.code39_add_check_digit is False


def test_code39_parser_accepts_plain_encode_options_container() -> None:
    """A plain EncodeOptions container should resolve to the definition's default mode."""
    payload = _base_parser().parse("ABC", options=EncodeOptions())

    assert payload.code39_encode_mode is Code39EncodeMode.BASE
    assert payload.code39_add_check_digit is False


def test_code39_parser_rejects_bytes_input() -> None:
    """Bytes input should fail as an unsupported capability rather than silently decode."""
    with pytest.raises(UnsupportedCapabilityError, match="bytes"):
        _base_parser().parse(b"ABC")


def test_code39_parser_rejects_empty_text() -> None:
    """Code 39 requires at least one supported text character."""
    with pytest.raises(InvalidInputError, match="empty"):
        _base_parser().parse("")


@pytest.mark.parametrize(
    ("options", "message_fragment"),
    [
        (Code39Options(gs1_enabled=True), "GS1"),
        (Code39Options(eci_assignment_number=3), "ECI"),
    ],
)
def test_code39_parser_rejects_unsupported_capabilities(
    options: Code39Options,
    message_fragment: str,
) -> None:
    """GS1 and ECI requests should fail as typed capability errors."""
    with pytest.raises(UnsupportedCapabilityError, match=message_fragment):
        _base_parser().parse("ABC", options=options)


@pytest.mark.parametrize(
    ("data", "position"),
    [
        ("abc", 1),
        ("A*B", 2),
        ("A#", 2),
    ],
)
def test_code39_parser_rejects_base_out_of_set_characters(data: str, position: int) -> None:
    """Characters outside the 43-character base set should fail with a 1-based position."""
    with pytest.raises(InvalidInputError, match=f"position {position}"):
        _base_parser().parse(data)


def test_code39_parser_rejects_non_ascii_in_full_ascii_mode() -> None:
    """Full-ASCII mode should reject code points above 127."""
    with pytest.raises(InvalidInputError, match="position 1"):
        _ext_parser().parse("é")


def test_code39_parser_accepts_star_in_full_ascii_mode() -> None:
    """The '*' character is only forbidden in base mode; Full-ASCII should accept it."""
    payload = _ext_parser().parse("*")

    assert payload.code39_encode_mode is Code39EncodeMode.FULL_ASCII
    assert payload.data == "*"


def test_code39_parser_preserves_whitespace_verbatim() -> None:
    """Supported spaces should survive parsing without trimming or rewriting."""
    data = "A B C"

    payload = _base_parser().parse(data)

    assert payload.data == data


@pytest.mark.parametrize("options", [object(), [], {}])
def test_code39_parser_rejects_unsupported_option_containers(options: object) -> None:
    """Only the documented option container types should be accepted."""
    with pytest.raises(InvalidInputError, match="encode options"):
        _base_parser().parse("ABC", options=options)  # type: ignore[arg-type]
