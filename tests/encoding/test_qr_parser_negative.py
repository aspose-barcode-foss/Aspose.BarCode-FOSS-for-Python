"""Contract tests for QR Code byte-mode parser validation and capability gating."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import QrEncodeMode, QrErrorCorrectionLevel, QrOptions
from aspose_barcode_foss._internal.parsers.qr import QrInputParser


def _parser() -> QrInputParser:
    """Build a default QR parser (symbology_name='qr')."""
    return QrInputParser()


def test_qr_parser_rejects_bytes_input() -> None:
    """Bytes input should fail as an unsupported capability (text only) before any validation."""
    with pytest.raises(UnsupportedCapabilityError, match="text only"):
        _parser().parse(b"ABC")


def test_qr_parser_rejects_empty_text() -> None:
    """QR byte mode requires at least one character; empty input is rejected."""
    with pytest.raises(InvalidInputError, match="empty"):
        _parser().parse("")


def test_qr_parser_rejects_non_latin1_character() -> None:
    """A code point above 255 cannot be encoded in byte mode and is rejected with a position."""
    with pytest.raises(InvalidInputError, match="byte mode"):
        _parser().parse("Ā")


@pytest.mark.parametrize(
    ("options", "message_fragment"),
    [
        (QrOptions(gs1_enabled=True), "GS1"),
    ],
)
def test_qr_parser_rejects_unsupported_capabilities(
    options: QrOptions,
    message_fragment: str,
) -> None:
    """GS1 requests should fail as typed capability errors (ECI, by contrast, is supported)."""
    with pytest.raises(UnsupportedCapabilityError, match=message_fragment):
        _parser().parse("ABC", options=options)


@pytest.mark.parametrize(
    "error_correction_level",
    ["Z", 5],
)
def test_qr_parser_rejects_invalid_error_correction_level(error_correction_level: object) -> None:
    """An out-of-set EC value or wrong type should fail during option coercion."""
    with pytest.raises(InvalidInputError, match="error_correction_level"):
        _parser().parse("ABC", options=QrOptions(error_correction_level=error_correction_level))


@pytest.mark.parametrize(
    ("version", "message_fragment"),
    [
        (0, "between 1 and 40"),
        (41, "between 1 and 40"),
        ("1", "version must be an integer"),
        (True, "version must be an integer"),
    ],
)
def test_qr_parser_rejects_invalid_version(version: object, message_fragment: str) -> None:
    """Out-of-range, non-int, and bool versions should all fail during option coercion."""
    with pytest.raises(InvalidInputError, match=message_fragment):
        _parser().parse("ABC", options=QrOptions(version=version))


@pytest.mark.parametrize(
    ("mask", "message_fragment"),
    [
        (-1, "between 0 and 7"),
        (8, "between 0 and 7"),
        ("0", "mask must be an integer"),
        (True, "mask must be an integer"),
    ],
)
def test_qr_parser_rejects_invalid_mask(mask: object, message_fragment: str) -> None:
    """Out-of-range, non-int, and bool masks should all fail during option coercion."""
    with pytest.raises(InvalidInputError, match=message_fragment):
        _parser().parse("ABC", options=QrOptions(mask=mask))


def test_qr_parser_rejects_data_too_large_for_auto_version() -> None:
    """An input larger than v40 capacity at any EC level should exhaust the version search."""
    with pytest.raises(InvalidInputError, match="too large"):
        _parser().parse("a" * 5000)


def test_qr_parser_rejects_data_too_large_for_forced_version() -> None:
    """An overlong input against a forced low-capacity version should fail explicitly."""
    options = QrOptions(error_correction_level=QrErrorCorrectionLevel.H, version=1)
    with pytest.raises(InvalidInputError, match="forced version"):
        _parser().parse("a" * 100, options=options)


def test_qr_parser_accepts_eci_assignment_number() -> None:
    """An ECI assignment number is now accepted and stamped onto the normalized payload."""
    payload = _parser().parse("ABC", options=QrOptions(eci_assignment_number=5))
    assert payload.qr_eci_assignment_number == 5


@pytest.mark.parametrize(
    ("data", "encoding_mode", "message_fragment"),
    [
        ("12A", QrEncodeMode.NUMERIC, "numeric mode"),
        ("abc", QrEncodeMode.ALPHANUMERIC, "alphanumeric mode"),
        ("AB", QrEncodeMode.KANJI, "Kanji mode"),
    ],
)
def test_qr_parser_rejects_input_not_representable_in_forced_mode(
    data: str,
    encoding_mode: QrEncodeMode,
    message_fragment: str,
) -> None:
    """A forced mode must reject input that cannot be represented in that mode."""
    with pytest.raises(InvalidInputError, match=message_fragment):
        _parser().parse(data, options=QrOptions(encoding_mode=encoding_mode))


@pytest.mark.parametrize(
    ("eci_assignment_number", "message_fragment"),
    [
        (1000000, "eci_assignment_number must be between"),
        (-1, "eci_assignment_number must be between"),
        ("5", "eci_assignment_number must be an integer"),
        (1.5, "eci_assignment_number must be an integer"),
    ],
)
def test_qr_parser_rejects_invalid_eci_assignment_number(
    eci_assignment_number: object,
    message_fragment: str,
) -> None:
    """Out-of-range and wrong-type ECI assignment numbers should fail during option coercion."""
    with pytest.raises(InvalidInputError, match=message_fragment):
        _parser().parse("ABC", options=QrOptions(eci_assignment_number=eci_assignment_number))


@pytest.mark.parametrize(
    ("data", "encoding_mode"),
    [
        ("123", QrEncodeMode.NUMERIC),
        ("ABC", QrEncodeMode.ALPHANUMERIC),
        ("点茗", QrEncodeMode.KANJI),
    ],
)
def test_qr_parser_rejects_eci_with_forced_non_byte_mode(
    data: str,
    encoding_mode: QrEncodeMode,
) -> None:
    """ECI is only valid with byte or auto mode; combining it with another forced mode fails."""
    options = QrOptions(encoding_mode=encoding_mode, eci_assignment_number=5)
    with pytest.raises(InvalidInputError, match="ECI is only supported with byte or auto"):
        _parser().parse(data, options=options)


@pytest.mark.parametrize(
    ("encoding_mode", "message_fragment"),
    [
        ("zzz", "encoding_mode must be one of"),
        (123, "encoding_mode must be a QrEncodeMode"),
    ],
)
def test_qr_parser_rejects_invalid_encoding_mode(
    encoding_mode: object,
    message_fragment: str,
) -> None:
    """An unknown encoding_mode string or a wrong-type value should fail during option coercion."""
    with pytest.raises(InvalidInputError, match=message_fragment):
        _parser().parse("ABC", options=QrOptions(encoding_mode=encoding_mode))


@pytest.mark.parametrize(
    "encoding_mode",
    [QrEncodeMode.BYTE, QrEncodeMode.AUTO],
)
def test_qr_parser_accepts_eci_with_byte_or_auto_mode(encoding_mode: QrEncodeMode) -> None:
    """ECI combined with byte or auto mode is allowed and the number is stamped on the payload."""
    options = QrOptions(encoding_mode=encoding_mode, eci_assignment_number=9)
    payload = _parser().parse("ABC", options=options)
    assert payload.qr_eci_assignment_number == 9
