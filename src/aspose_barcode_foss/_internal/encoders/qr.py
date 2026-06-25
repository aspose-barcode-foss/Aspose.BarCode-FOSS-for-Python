"""QR Code (ISO/IEC 18004) byte-mode encoder.

Orchestrates the ``standards/qr`` package: builds the data codewords, splits them into blocks
and computes Reed-Solomon error-correction codewords per block, interleaves data + EC codewords and
appends the per-version remainder bits, selects (or accepts) a data mask and assembles
the final immutable N*N grid via ``assemble`` (which performs function-pattern construction,
zig-zag data placement, masking, and information writing).

This module contains no spec tables: every normative value is sourced from the ``standards/qr``
package.
"""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import EncodeOptions, QrEncodeMode, QrErrorCorrectionLevel
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.standards.qr import (
    QrMode,
    assemble,
    block_structure,
    build_data_codewords,
    ec_per_block,
    forced_segments,
    remainder_bits,
    rs_encode,
    segment_optimal,
    select_best_mask,
    symbol_size,
)

_MIN_VERSION = 1
_MAX_VERSION = 40
_MIN_MASK = 0
_MAX_MASK = 7


class QrEncoder(SymbologyEncoder):
    """Encode text data into a QR Code byte-mode symbol."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: EncodeOptions | None = None,
    ) -> EncodedSymbol:
        """Encode a QR payload into the final masked N*N module matrix."""
        del options

        text, version, letter, mask_request, qr_mode, eci = self._validate_payload(payload)

        if qr_mode is QrEncodeMode.AUTO:
            segments = segment_optimal(text, version)
        else:
            segments = forced_segments(text, QrMode[qr_mode.name])

        data_cw = build_data_codewords(segments, version, letter, eci_assignment_number=eci)
        bitstream = self._build_bitstream(data_cw, version, letter)

        if mask_request is None:
            mask = select_best_mask(lambda m: assemble(version, letter, bitstream, m))
        else:
            mask = mask_request

        grid = assemble(version, letter, bitstream, mask)
        side = symbol_size(version)

        return EncodedSymbol(
            matrix=ModuleMatrix(width=side, height=side, modules=grid),
            metadata=SymbolMetadata(
                symbology="qr",
                normalized_data=text,
                display_text="",
                input_kind="text",
                gs1_enabled=False,
                eci_assignment_number=eci,
            ),
        )

    def _validate_payload(
        self,
        payload: NormalizedPayload,
    ) -> tuple[str, int, str, int | None, QrEncodeMode, int | None]:
        """Validate the payload contract and return ``(text, version, letter, mask, qr_mode, eci)``."""
        if payload.symbology != "qr":
            msg = "QR encoder requires symbology='qr'"
            raise InvalidInputError(msg)
        if payload.input_kind != "text":
            msg = "QR encoder requires input_kind='text'"
            raise InvalidInputError(msg)
        if not isinstance(payload.data, str) or not payload.data:
            msg = "QR encoder requires payload.data to be a non-empty text string"
            raise InvalidInputError(msg)

        letter = self._require_ecc_letter(payload)
        version = self._require_version(payload)
        mask_request = self._require_mask(payload)
        qr_mode = self._require_encoding_mode(payload)
        eci = self._require_eci(payload)
        return payload.data, version, letter, mask_request, qr_mode, eci

    def _require_ecc_letter(self, payload: NormalizedPayload) -> str:
        """Require a ``QrErrorCorrectionLevel`` and return its letter (L/M/Q/H)."""
        level = payload.qr_error_correction_level
        if not isinstance(level, QrErrorCorrectionLevel):
            msg = "QR encoder requires payload.qr_error_correction_level to be a QrErrorCorrectionLevel"
            raise InvalidInputError(msg)
        return level.name

    def _require_version(self, payload: NormalizedPayload) -> int:
        """Require a resolved integer version in 1..40 (reject bool/None/out-of-range)."""
        version = payload.qr_version
        if not isinstance(version, int) or isinstance(version, bool):
            msg = "QR encoder requires payload.qr_version to be an int in 1..40"
            raise InvalidInputError(msg)
        if not (_MIN_VERSION <= version <= _MAX_VERSION):
            msg = "QR encoder requires payload.qr_version to be in 1..40"
            raise InvalidInputError(msg)
        return version

    def _require_mask(self, payload: NormalizedPayload) -> int | None:
        """Require ``qr_mask`` to be None or an int in 0..7 (reject bool)."""
        mask = payload.qr_mask
        if mask is None:
            return None
        if not isinstance(mask, int) or isinstance(mask, bool):
            msg = "QR encoder requires payload.qr_mask to be None or an int in 0..7"
            raise InvalidInputError(msg)
        if not (_MIN_MASK <= mask <= _MAX_MASK):
            msg = "QR encoder requires payload.qr_mask to be in 0..7"
            raise InvalidInputError(msg)
        return mask

    def _require_encoding_mode(self, payload: NormalizedPayload) -> QrEncodeMode:
        """Require a ``QrEncodeMode`` (the parser always stamps one); reject None/non-QrEncodeMode."""
        mode = payload.qr_encoding_mode
        if not isinstance(mode, QrEncodeMode):
            msg = "QR encoder requires payload.qr_encoding_mode to be a QrEncodeMode"
            raise InvalidInputError(msg)
        return mode

    def _require_eci(self, payload: NormalizedPayload) -> int | None:
        """Require ``qr_eci_assignment_number`` to be None or an int (reject bool); range is the parser's job."""
        eci = payload.qr_eci_assignment_number
        if eci is None:
            return None
        if not isinstance(eci, int) or isinstance(eci, bool):
            msg = "QR encoder requires payload.qr_eci_assignment_number to be None or an int"
            raise InvalidInputError(msg)
        return eci

    def _build_bitstream(self, data_cw: list[int], version: int, letter: str) -> list[int]:
        """Build the placement bit list: interleaved data + EC codewords plus remainder bits.

        Splits ``data_cw`` into blocks per the structure, computes RS EC codewords per block,
        interleaves the data then the EC codewords, expands each byte MSB-first, and appends the
        per-version remainder zero bits. The result length equals the number of free (non-function)
        modules, satisfying the ``place_data`` invariant.
        """
        blocks = self._split_blocks(data_cw, version, letter)
        ec_count = ec_per_block(version, letter)
        ec_blocks = [rs_encode(block, ec_count) for block in blocks]

        interleaved = self._interleave(blocks) + self._interleave(ec_blocks)

        bitstream: list[int] = []
        for byte in interleaved:
            for shift in range(7, -1, -1):
                bitstream.append((byte >> shift) & 1)
        bitstream.extend([0] * remainder_bits(version))
        return bitstream

    def _split_blocks(self, data_cw: list[int], version: int, letter: str) -> list[list[int]]:
        """Slice ``data_cw`` into blocks per ``block_structure`` (shorter blocks first, listed order)."""
        lengths: list[int] = []
        for count, data_per_block in block_structure(version, letter):
            lengths.extend([data_per_block] * count)

        blocks: list[list[int]] = []
        offset = 0
        for length in lengths:
            blocks.append(data_cw[offset : offset + length])
            offset += length
        return blocks

    def _interleave(self, blocks: list[list[int]]) -> list[int]:
        """Interleave codewords column-major: index 0 of every block, then index 1, ....

        A block is skipped once exhausted, so shorter blocks contribute fewer rounds.
        """
        if not blocks:
            return []
        max_len = max(len(block) for block in blocks)
        result: list[int] = []
        for index in range(max_len):
            for block in blocks:
                if index < len(block):
                    result.append(block[index])
        return result
