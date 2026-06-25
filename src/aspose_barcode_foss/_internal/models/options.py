"""Option models used across encoding and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Code128EncodeMode(Enum):
    """Supported public Code 128 encode-mode requests."""

    AUTO = auto()
    CODE_A = auto()
    CODE_B = auto()
    CODE_C = auto()
    CODE_AB = auto()
    CODE_AC = auto()
    CODE_BC = auto()


class Code39EncodeMode(Enum):
    """Supported Code 39 encode modes."""

    BASE = auto()
    FULL_ASCII = auto()


class QrEncodeMode(Enum):
    """Supported public QR Code encode-mode requests."""

    AUTO = auto()
    NUMERIC = auto()
    ALPHANUMERIC = auto()
    BYTE = auto()
    KANJI = auto()


class QrErrorCorrectionLevel(Enum):
    """Supported QR Code error correction levels."""

    L = auto()
    M = auto()
    Q = auto()
    H = auto()


@dataclass(slots=True, frozen=True)
class EncodeOptions:
    """Base type for symbology-specific encoding options."""

    gs1_enabled: bool | None = None
    eci_assignment_number: int | None = None


@dataclass(slots=True, frozen=True)
class Code128Options(EncodeOptions):
    """Encoding options for Code 128."""

    encode_mode: Code128EncodeMode = Code128EncodeMode.AUTO


@dataclass(slots=True, frozen=True)
class Code39Options(EncodeOptions):
    """Encoding options for Code 39."""

    full_ascii: bool | None = None
    add_check_digit: bool | None = None


@dataclass(slots=True, frozen=True)
class QrOptions(EncodeOptions):
    """Encoding options for QR Code."""

    error_correction_level: QrErrorCorrectionLevel | str | None = None
    version: int | None = None
    mask: int | None = None
    encoding_mode: QrEncodeMode | str | None = None


@dataclass(slots=True, frozen=True)
class Ean13Options(EncodeOptions):
    """Encoding options for EAN-13."""

    allow_check_digit_input: bool | None = None


@dataclass(slots=True, frozen=True)
class Ean8Options(EncodeOptions):
    """Encoding options for EAN-8."""

    allow_check_digit_input: bool | None = None


@dataclass(slots=True, frozen=True)
class UpcaOptions(EncodeOptions):
    """Encoding options for UPC-A."""

    allow_check_digit_input: bool | None = None


@dataclass(slots=True, frozen=True)
class UpceOptions(EncodeOptions):
    """Encoding options for UPC-E."""

    number_system: str | None = None
    allow_check_digit_input: bool | None = None


@dataclass(slots=True, frozen=True)
class RenderOptions:
    """User-supplied rendering options."""

    scale: float | None = None
    dpi: int | None = None
    module_width: float | None = None
    module_height: float | None = None
    quiet_zone: float | None = None
    foreground_color: str | None = None
    background_color: str | None = None
    transparent_background: bool | None = None
    show_text: bool | None = None
    font_family: str | None = None
    font_size: float | None = None


@dataclass(slots=True, frozen=True)
class ResolvedRenderOptions:
    """Fully resolved rendering configuration."""

    scale: float
    dpi: int | None
    module_width: float
    module_height: float
    quiet_zone: float
    foreground_color: str
    background_color: str | None
    transparent_background: bool
    show_text: bool
    font_family: str
    font_size: float
