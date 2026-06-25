"""Per-mode segment encoders and cost functions for QR Code (ISO/IEC 18004:2015 §7.4).

Owns the verbatim per-mode normative encoders and their data-bit cost functions:
the 4-bit mode indicators, the Table 3 character-count widths, numeric
grouping, the 45-character alphanumeric table, Kanji / Shift-JIS 13-bit
packing, and the ECI header.

It also defines the internal ``QrMode`` enum, the ``Segment`` dataclass, the
eligibility predicates, the four ``*_data_bits`` cost functions, the per-segment
bit emitters, and the ECI header emitter.

This module is PURE and SIDE-EFFECT-FREE: it emits *mode indicator + count
indicator + data bits* per segment into a shared ``bits`` list, and never owns the
terminator / bit-pad / pad-codeword tail (that stays in ``bitstream.py``).
The internal ``QrMode`` is distinct from the public ``QrEncodeMode`` (which also has
an ``AUTO`` member that does not exist here).

References: ISO/IEC 18004:2015 §7.4.1 Table 2, §7.4.1 Table 3,
§7.4.3, §7.4.4 Table 5, §7.4.6, §7.4.2 / §7.4.2.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from aspose_barcode_foss._internal.standards.qr.bitstream import latin1_bytes
from aspose_barcode_foss._internal.standards.qr.tables import byte_count_bits

# ---------------------------------------------------------------------------
# Mode indicators (4-bit, MSB-first)
# ---------------------------------------------------------------------------

NUMERIC: int = 0b0001
ALPHANUMERIC: int = 0b0010
BYTE: int = 0b0100
KANJI: int = 0b1000
ECI: int = 0b0111
TERMINATOR: int = 0b0000


class QrMode(Enum):
    """Internal QR data mode (no ``AUTO`` — that lives only on the public ``QrEncodeMode``)."""

    NUMERIC = "numeric"
    ALPHANUMERIC = "alphanumeric"
    BYTE = "byte"
    KANJI = "kanji"

    @property
    def indicator(self) -> int:
        """Return the 4-bit mode indicator for this mode."""
        return _MODE_INDICATOR[self]


_MODE_INDICATOR: dict[QrMode, int] = {
    QrMode.NUMERIC: NUMERIC,
    QrMode.ALPHANUMERIC: ALPHANUMERIC,
    QrMode.BYTE: BYTE,
    QrMode.KANJI: KANJI,
}


# ---------------------------------------------------------------------------
# Character-count-indicator bit length (Table 3)
#
# Version groups: 1-9, 10-26, 27-40. The byte row is delegated to
# tables.byte_count_bits so it cannot diverge.
# ---------------------------------------------------------------------------

_COUNT_INDICATOR_BITS: dict[QrMode, tuple[int, int, int]] = {
    QrMode.NUMERIC: (10, 12, 14),
    QrMode.ALPHANUMERIC: (9, 11, 13),
    QrMode.KANJI: (8, 10, 12),
}


def _version_group_index(version: int) -> int:
    """Return 0 for versions 1-9, 1 for 10-26, 2 for 27-40."""
    if version <= 9:
        return 0
    if version <= 26:
        return 1
    return 2


def count_indicator_bits(mode: QrMode, version: int) -> int:
    """Return the character-count-indicator bit length (Table 3) for mode at version."""
    if mode is QrMode.BYTE:
        return byte_count_bits(version)
    return _COUNT_INDICATOR_BITS[mode][_version_group_index(version)]


# ---------------------------------------------------------------------------
# Alphanumeric table (45 chars, values 0..44; no lowercase letters)
# ---------------------------------------------------------------------------

ALPHANUMERIC_CHARS: tuple[str, ...] = tuple("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")
ALPHANUMERIC_VALUES: dict[str, int] = {ch: value for value, ch in enumerate(ALPHANUMERIC_CHARS)}


# ---------------------------------------------------------------------------
# Eligibility predicates
# ---------------------------------------------------------------------------


def is_numeric(ch: str) -> bool:
    """Return True if ch is a single decimal digit '0'-'9'."""
    return ch in "0123456789"


def is_alphanumeric(ch: str) -> bool:
    """Return True if ch is in the 45-character alphanumeric table."""
    return ch in ALPHANUMERIC_VALUES


def shift_jis_double_byte(ch: str) -> int | None:
    """Return the big-endian Shift-JIS code C if ch is Kanji-encodable, else None.

    Encodes ch via the stdlib ``shift_jis`` codec. Returns ``C = (b0 << 8) | b1`` only
    when ch yields exactly two bytes whose code falls in a range; single-byte or
    un-encodable characters return ``None``.
    """
    try:
        encoded = ch.encode("shift_jis")
    except UnicodeEncodeError:
        return None
    if len(encoded) != 2:
        return None
    code = (encoded[0] << 8) | encoded[1]
    if 0x8140 <= code <= 0x9FFC or 0xE040 <= code <= 0xEBBF:
        return code
    return None


def kanji_value(code: int) -> int:
    """Return the 13-bit packed Kanji value for a Shift-JIS code C.

    1. D = C - 0x8140 (range [0x8140, 0x9FFC]) or C - 0xC140 (range [0xE040, 0xEBBF]).
    2. value = (D >> 8) * 0xC0 + (D & 0xFF).
    """
    if 0x8140 <= code <= 0x9FFC:
        offset = 0x8140
    elif 0xE040 <= code <= 0xEBBF:
        offset = 0xC140
    else:
        raise ValueError(f"Shift-JIS code 0x{code:04X} is outside the Kanji-mode ranges")
    diff = code - offset
    return (diff >> 8) * 0xC0 + (diff & 0xFF)


# ---------------------------------------------------------------------------
# Data-bit cost functions (counts are characters, except byte = bytes)
# ---------------------------------------------------------------------------


def numeric_data_bits(n: int) -> int:
    """Return the numeric data-bit length for n digits: 10 bits / group of 3, +7 or +4 tail."""
    return 10 * (n // 3) + (7 if n % 3 == 2 else 4 if n % 3 == 1 else 0)


def alphanumeric_data_bits(n: int) -> int:
    """Return the alphanumeric data-bit length for n chars: 11 bits / pair, +6 for a trailing single."""
    return 11 * (n // 2) + (6 if n % 2 == 1 else 0)


def byte_data_bits(n: int) -> int:
    """Return the byte-mode data-bit length for n bytes: 8 bits each."""
    return 8 * n


def kanji_data_bits(n: int) -> int:
    """Return the Kanji data-bit length for n Kanji characters: 13 bits each."""
    return 13 * n


# ---------------------------------------------------------------------------
# Segment value object
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Segment:
    """A single QR data segment: a mode and the verbatim input text it encodes."""

    mode: QrMode
    text: str


# ---------------------------------------------------------------------------
# MSB-first append helper (local twin of bitstream._append_bits — same behavior,
# kept here to avoid import coupling to the soon-to-be-generalized bitstream).
# ---------------------------------------------------------------------------


def _append_bits(bits: list[int], value: int, length: int) -> None:
    """Append value as length bits, MSB first, to the bits list."""
    for shift in range(length - 1, -1, -1):
        bits.append((value >> shift) & 1)


# ---------------------------------------------------------------------------
# Per-mode data-bit emitters (data only — no mode indicator / count)
# ---------------------------------------------------------------------------


def _emit_numeric_data(bits: list[int], text: str) -> None:
    """Emit numeric data bits: 10 bits / group of 3, 7 bits for a trailing 2, 4 bits for a trailing 1."""
    index = 0
    length = len(text)
    while index + 3 <= length:
        _append_bits(bits, int(text[index : index + 3]), 10)
        index += 3
    remainder = length - index
    if remainder == 2:
        _append_bits(bits, int(text[index:length]), 7)
    elif remainder == 1:
        _append_bits(bits, int(text[index:length]), 4)


def _emit_alphanumeric_data(bits: list[int], text: str) -> None:
    """Emit alphanumeric data bits: 11 bits / pair (45*V(c1)+V(c2)), 6 bits for a trailing single."""
    index = 0
    length = len(text)
    while index + 2 <= length:
        value = 45 * ALPHANUMERIC_VALUES[text[index]] + ALPHANUMERIC_VALUES[text[index + 1]]
        _append_bits(bits, value, 11)
        index += 2
    if index < length:
        _append_bits(bits, ALPHANUMERIC_VALUES[text[index]], 6)


def _emit_byte_data(bits: list[int], text: str) -> None:
    """Emit byte-mode data bits: 8 bits per Latin-1 byte (identical to the current byte-mode builder)."""
    for byte in latin1_bytes(text):
        _append_bits(bits, byte, 8)


def _emit_kanji_data(bits: list[int], text: str) -> None:
    """Emit Kanji data bits: 13 bits per character via the Shift-JIS 13-bit packing."""
    for ch in text:
        code = shift_jis_double_byte(ch)
        if code is None:
            raise ValueError(f"Character {ch!r} is not Kanji-encodable (not a Shift-JIS double byte)")
        _append_bits(bits, kanji_value(code), 13)


_DATA_EMITTERS = {
    QrMode.NUMERIC: _emit_numeric_data,
    QrMode.ALPHANUMERIC: _emit_alphanumeric_data,
    QrMode.BYTE: _emit_byte_data,
    QrMode.KANJI: _emit_kanji_data,
}


def _segment_count(segment: Segment) -> int:
    """Return the character-count-indicator value: input characters (bytes for byte mode)."""
    if segment.mode is QrMode.BYTE:
        return len(latin1_bytes(segment.text))
    return len(segment.text)


# ---------------------------------------------------------------------------
# Segment emission + cost helpers
# ---------------------------------------------------------------------------


def emit_segment(bits: list[int], segment: Segment, version: int) -> None:
    """Append mode indicator + count indicator + data bits for segment to bits (in order)."""
    _append_bits(bits, segment.mode.indicator, 4)
    _append_bits(bits, _segment_count(segment), count_indicator_bits(segment.mode, version))
    _DATA_EMITTERS[segment.mode](bits, segment.text)


def segment_data_bits(segment: Segment, version: int) -> int:
    """Return the data-bit length of segment (excluding the 4-bit mode + count indicator)."""
    count = _segment_count(segment)
    if segment.mode is QrMode.NUMERIC:
        return numeric_data_bits(count)
    if segment.mode is QrMode.ALPHANUMERIC:
        return alphanumeric_data_bits(count)
    if segment.mode is QrMode.BYTE:
        return byte_data_bits(count)
    return kanji_data_bits(count)


def segment_total_bits(segment: Segment, version: int) -> int:
    """Return the full segment bit length: 4 (mode) + count_indicator_bits + data bits."""
    return 4 + count_indicator_bits(segment.mode, version) + segment_data_bits(segment, version)


# ---------------------------------------------------------------------------
# ECI header
# ---------------------------------------------------------------------------


def emit_eci_header(bits: list[int], assignment_number: int) -> None:
    """Append the ECI header: the 0111 indicator then the range-selected assignment number.

    Layout (MSB-first):
      0 .. 127 -> 1 codeword (8 bits): 0 + 7-bit number
      128 .. 16383 -> 2 codewords (16 bits): 10 + 14-bit number
      16384 .. 999999 -> 3 codewords (24 bits): 110 + 21-bit number
    """
    _append_bits(bits, ECI, 4)
    if assignment_number <= 127:
        _append_bits(bits, assignment_number, 8)
    elif assignment_number <= 16383:
        _append_bits(bits, 0b10 << 14 | assignment_number, 16)
    else:
        _append_bits(bits, 0b110 << 21 | assignment_number, 24)
