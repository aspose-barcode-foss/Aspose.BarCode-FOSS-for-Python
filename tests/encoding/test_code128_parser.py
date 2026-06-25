"""Contract tests for Code 128 parser validation and normalization."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import (
    Code128EncodeMode,
    Code128Options,
    EncodeOptions,
)
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.code128 import Code128InputParser


@pytest.mark.parametrize(
    ("data", "options"),
    [
        ("A", None),
        ("ABC123", Code128Options()),
        ("A", EncodeOptions()),
    ],
)
def test_code128_parser_accepts_supported_text_and_option_forms(
    data: str,
    options: Code128Options | EncodeOptions | None,
) -> None:
    """Supported text input should normalize into the Code 128 payload contract."""
    payload = Code128InputParser().parse(data, options=options)

    assert payload == NormalizedPayload(
        symbology="code128",
        data=data,
        input_kind="text",
        code128_encode_mode=Code128EncodeMode.AUTO,
    )


def test_code128_parser_rejects_bytes_input() -> None:
    """The should not silently coerce bytes into text."""
    with pytest.raises(UnsupportedCapabilityError, match="bytes"):
        Code128InputParser().parse(b"ABC123")


def test_code128_parser_preserves_supported_whitespace_verbatim() -> None:
    """Supported spaces should survive parsing without trimming or rewriting."""
    data = " A B "

    payload = Code128InputParser().parse(data)

    assert payload.data == data


@pytest.mark.parametrize(
    ("data", "mode"),
    [
        ("ABC123", Code128EncodeMode.CODE_A),
        ("ABC123", Code128EncodeMode.CODE_B),
        ("1234", Code128EncodeMode.CODE_C),
        ("ABC123", Code128EncodeMode.CODE_AB),
        ("ABC123", Code128EncodeMode.CODE_AC),
        ("ABC123", Code128EncodeMode.CODE_BC),
    ],
)
def test_code128_parser_preserves_supported_typed_encode_modes(
    data: str,
    mode: Code128EncodeMode,
) -> None:
    """Parser output should carry the exact typed encode mode through to encoding."""
    payload = Code128InputParser().parse(data, options=Code128Options(encode_mode=mode))

    assert payload.code128_encode_mode is mode


@pytest.mark.parametrize(
    ("options", "message_fragment"),
    [
        (Code128Options(gs1_enabled=True), "GS1"),
        (EncodeOptions(eci_assignment_number=26), "ECI"),
    ],
)
def test_code128_parser_rejects_unsupported_capabilities(
    options: Code128Options | EncodeOptions,
    message_fragment: str,
) -> None:
    """Unsupported capabilities should fail as typed capability errors."""
    with pytest.raises(UnsupportedCapabilityError, match=message_fragment):
        Code128InputParser().parse("ABC123", options=options)


def test_code128_parser_rejects_empty_text() -> None:
    """Code 128 requires at least one supported text character."""
    with pytest.raises(InvalidInputError, match="empty"):
        Code128InputParser().parse("")


@pytest.mark.parametrize(
    ("data", "options", "message_fragment"),
    [
        ("A\n", Code128Options(encode_mode=Code128EncodeMode.CODE_B), "CODE_B"),
        ("a", Code128Options(encode_mode=Code128EncodeMode.CODE_A), "CODE_A"),
        ("123", Code128Options(encode_mode=Code128EncodeMode.CODE_C), "CODE_C"),
        ("\x7f", None, "ASCII code points 0 through 126"),
    ],
)
def test_code128_parser_rejects_text_that_conflicts_with_the_requested_mode(
    data: str,
    options: Code128Options | None,
    message_fragment: str,
) -> None:
    """Standard-invalid text should fail before the encoder runs."""
    with pytest.raises(InvalidInputError, match=message_fragment):
        Code128InputParser().parse(data, options=options)


def test_code128_parser_accepts_control_characters_in_auto_mode() -> None:
    """AUTO should preserve standard-valid Code Set A control characters."""
    payload = Code128InputParser().parse("A\n")

    assert payload == NormalizedPayload(
        symbology="code128",
        data="A\n",
        input_kind="text",
        code128_encode_mode=Code128EncodeMode.AUTO,
    )


@pytest.mark.parametrize(
    "options",
    [
        Code128Options(encode_mode=None),  # type: ignore[arg-type]
        Code128Options(encode_mode="code-c"),  # type: ignore[arg-type]
        Code128Options(encode_mode=object()),  # type: ignore[arg-type]
    ],
)
def test_code128_parser_rejects_non_enum_encode_modes(options: Code128Options) -> None:
    """encode_mode must be expressed through the shared Code128 enum."""
    with pytest.raises(InvalidInputError, match="Code128EncodeMode"):
        Code128InputParser().parse("ABC123", options=options)


@pytest.mark.parametrize("options", [object(), [], {}])
def test_code128_parser_rejects_unsupported_option_containers(
    options: object,
) -> None:
    """Only the documented option container types should be accepted."""
    with pytest.raises(InvalidInputError, match="encode options"):
        Code128InputParser().parse("ABC123", options=options)  # type: ignore[arg-type]
