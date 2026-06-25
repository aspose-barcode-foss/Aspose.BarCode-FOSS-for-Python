"""Bit-stream assembly into the QR data-codeword list.

Consumes an ordered segment list (plus an optional leading ECI header) and turns
it into the data-codeword list for a given (version, ECC): each segment's mode
indicator + character-count + data bits are emitted by ``segments.emit_segment``,
then this module owns the common tail for ALL modes -- terminator, bit padding,
and alternating pad codewords (0xEC / 0x11) up to the data-codeword capacity.

This module emits ONLY the data-codeword list. Reed-Solomon EC, block splitting,
interleaving, and remainder bits are the encoder's job.

References: ISO/IEC 18004 (byte-mode encoding).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from aspose_barcode_foss._internal.standards.qr.tables import data_codewords

if TYPE_CHECKING:
    from aspose_barcode_foss._internal.standards.qr.segments import Segment

_PAD_CODEWORD_A: int = 0xEC  # 11101100
_PAD_CODEWORD_B: int = 0x11  # 00010001


def latin1_bytes(text: str) -> list[int]:
    """Return the Latin-1 (ISO-8859-1) byte values of text; raise ValueError on code points > 255."""
    result: list[int] = []
    for ch in text:
        code = ord(ch)
        if code > 255:
            raise ValueError(f"Character {ch!r} (U+{code:04X}) is not representable in Latin-1 byte mode")
        result.append(code)
    return result


def build_data_codewords(
    segments: list[Segment],
    version: int,
    ecc_letter: str,
    *,
    eci_assignment_number: int | None = None,
) -> list[int]:
    """Assemble the data-codeword list for the (version, ECC) symbol from an ordered segment list."""
    # Deferred import to avoid the bitstream <-> segments import cycle (segments imports latin1_bytes here).
    from aspose_barcode_foss._internal.standards.qr.segments import emit_eci_header, emit_segment  # noqa: PLC0415

    bits: list[int] = []
    if eci_assignment_number is not None:
        emit_eci_header(bits, eci_assignment_number)
    for segment in segments:
        emit_segment(bits, segment, version)

    num_data_cw = data_codewords(version, ecc_letter)
    capacity_bits = num_data_cw * 8

    # Terminator: up to 4 zero bits, but no more than the remaining capacity.
    terminator = min(4, capacity_bits - len(bits))
    bits.extend([0] * terminator)

    # Bit padding to the next byte boundary.
    if len(bits) % 8 != 0:
        bits.extend([0] * (8 - len(bits) % 8))

    codewords = [int("".join(str(b) for b in bits[i : i + 8]), 2) for i in range(0, len(bits), 8)]

    # Pad codewords: alternate 0xEC / 0x11 (starting with 0xEC) until the capacity is filled.
    pad_cycle = (_PAD_CODEWORD_A, _PAD_CODEWORD_B)
    pad_index = 0
    while len(codewords) < num_data_cw:
        codewords.append(pad_cycle[pad_index % 2])
        pad_index += 1

    return codewords
