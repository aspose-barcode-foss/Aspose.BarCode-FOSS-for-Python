"""Code 39 (ISO/IEC 16388:2017) encoder."""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import Code39EncodeMode
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.standards.code39 import (
    INTER_CHARACTER_GAP_MODULES,
    START_STOP,
    WIDE_NARROW_RATIO,
    checksum_char,
    code39_checksum,
    expand_full_ascii,
    get_code39_pattern,
)

_CONTROL_CHAR_NAMES: dict[int, str] = {
    0: "NUL",
    1: "SOH",
    2: "STX",
    3: "ETX",
    4: "EOT",
    5: "ENQ",
    6: "ACK",
    7: "BEL",
    8: "BS",
    9: "HT",
    10: "LF",
    11: "VT",
    12: "FF",
    13: "CR",
    14: "SO",
    15: "SI",
    16: "DLE",
    17: "DC1",
    18: "DC2",
    19: "DC3",
    20: "DC4",
    21: "NAK",
    22: "SYN",
    23: "ETB",
    24: "CAN",
    25: "EM",
    26: "SUB",
    27: "ESC",
    28: "FS",
    29: "GS",
    30: "RS",
    31: "US",
    127: "DEL",
}


class Code39Encoder(SymbologyEncoder):
    """Encode data into a Code 39 (base or Full-ASCII) symbol."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: object | None = None,
    ) -> EncodedSymbol:
        """Encode a Code 39 payload into a flat module-row symbol."""
        del options

        text, mode, add_check = self._validate_payload(payload)

        try:
            base_chars = expand_full_ascii(text) if mode is Code39EncodeMode.FULL_ASCII else text
        except ValueError as exc:
            msg = f"unsupported Code 39 character in payload: {text!r}"
            raise InvalidInputError(msg) from exc

        if add_check:
            try:
                check_value = code39_checksum(base_chars)
                base_chars = base_chars + checksum_char(check_value)
            except ValueError as exc:
                msg = f"unsupported Code 39 character in payload: {base_chars!r}"
                raise InvalidInputError(msg) from exc

        symbol_chars = [START_STOP, *base_chars, START_STOP]
        module_row = self._build_module_row(symbol_chars)
        display_text = self._build_display_text(text)

        return EncodedSymbol(
            matrix=ModuleMatrix(
                width=len(module_row),
                height=1,
                modules=(module_row,),
            ),
            metadata=SymbolMetadata(
                symbology=payload.symbology,
                normalized_data=text,
                display_text=display_text,
                input_kind="text",
                gs1_enabled=False,
                eci_assignment_number=None,
            ),
        )

    def _validate_payload(
        self,
        payload: NormalizedPayload,
    ) -> tuple[str, Code39EncodeMode, bool]:
        """Validate the normalized payload contract before encoding."""
        if payload.symbology not in ("code39", "code39ext"):
            msg = "Code 39 encoder requires symbology='code39' or 'code39ext'"
            raise InvalidInputError(msg)
        if payload.input_kind != "text":
            msg = "Code 39 encoder requires input_kind='text'"
            raise InvalidInputError(msg)
        if not isinstance(payload.data, str):
            msg = "Code 39 encoder requires payload.data to be a text string"
            raise InvalidInputError(msg)
        if not payload.data:
            msg = "Code 39 text must not be empty"
            raise InvalidInputError(msg)

        mode = self._require_code39_mode(payload)
        add_check = bool(payload.code39_add_check_digit)
        return payload.data, mode, add_check

    def _require_code39_mode(self, payload: NormalizedPayload) -> Code39EncodeMode:
        """Require the typed Code 39 encode-mode handoff from the parser."""
        mode = payload.code39_encode_mode
        if mode is None:
            msg = "Code 39 encoder requires payload.code39_encode_mode"
            raise InvalidInputError(msg)
        if not isinstance(mode, Code39EncodeMode):
            msg = "Code 39 payload.code39_encode_mode must be a Code39EncodeMode"
            raise InvalidInputError(msg)
        return mode

    def _build_module_row(self, symbol_chars: list[str]) -> tuple[int, ...]:
        """Flatten each character's 9-bit pattern into a flat module row (NF-3)."""
        modules: list[int] = []
        for char in symbol_chars:
            try:
                pattern = get_code39_pattern(char)
            except ValueError as exc:
                msg = f"unsupported Code 39 character in payload: {char!r}"
                raise InvalidInputError(msg) from exc
            for element_index, bit in enumerate(pattern):
                run = WIDE_NARROW_RATIO if bit == "1" else 1
                fill = 1 if element_index % 2 == 0 else 0
                modules.extend([fill] * run)
            modules.extend([0] * INTER_CHARACTER_GAP_MODULES)
        return tuple(modules)

    def _build_display_text(self, text: str) -> str:
        """Produce a printable representation of the original input.

        Control characters (ASCII 0-31) and DEL (127) are rendered as
        <MNEMONIC>; all other characters pass through unchanged.
        """
        parts: list[str] = []
        for char in text:
            o = ord(char)
            if (0 <= o <= 31) or o == 127:
                parts.append(f"<{_CONTROL_CHAR_NAMES[o]}>")
            else:
                parts.append(char)
        return "".join(parts)
