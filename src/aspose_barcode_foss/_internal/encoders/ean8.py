"""EAN-8 encoder."""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import Ean8Options, EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.standards.ean import (
    CENTRE_GUARD,
    EAN8_BAR_HEIGHT_X,
    EAN_GUARD_EXTENSION_X,
    NORMAL_GUARD,
    encode_digit,
)

# Absolute positions in the 67-module row that carry guard bar dark modules in row 1.
# Left guard: 0, 2; Centre guard bars: 32, 34; Right guard: 64, 66.
_GUARD_EXTENSION_POSITIONS: frozenset[int] = frozenset({0, 2, 32, 34, 64, 66})


class Ean8Encoder(SymbologyEncoder):
    """Encode normalized payloads into EAN-8 symbols."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: Ean8Options | EncodeOptions | None = None,
    ) -> EncodedSymbol:
        """Encode an EAN-8 payload into a 67-module, 2-row ModuleMatrix.

        Row 0 contains the full 67-module symbol sequence. The left half is four
        digits encoded with Set A (no parity mixing, unlike EAN-13) and the right
        half is four digits encoded with Set C.
        Row 1 is a guard-extension mask with dark modules only at the guard bar
        positions (absolute indices 0, 2, 32, 34, 64, 66).

        Args:
            payload: Normalized payload with ``symbology="ean8"``,
                ``input_kind="text"``, and ``data`` as an 8-digit string.
            options: Optional encoder options (currently unused).

        Returns:
            An :class:`EncodedSymbol` containing the module matrix and metadata.

        Raises:
            InvalidInputError: If the payload symbology, input kind, or data
                do not satisfy EAN-8 requirements.
        """
        # --- Validate payload ---
        if payload.symbology != "ean8":
            raise InvalidInputError(f"EAN-8 encoder requires symbology='ean8', got {payload.symbology!r}")
        if payload.input_kind != "text":
            raise InvalidInputError(f"EAN-8 encoder requires input_kind='text', got {payload.input_kind!r}")
        data = payload.data
        if not isinstance(data, str) or len(data) != 8 or not all("0" <= ch <= "9" for ch in data):
            raise InvalidInputError(f"EAN-8 data must be a string of exactly 8 digits, got {data!r}")

        # --- Encoding ---
        # Left half: digits 1–4 encoded with Set A (no parity lookup).
        left_modules: tuple[int, ...] = ()
        for i in range(4):
            left_modules += encode_digit(int(data[i]), "A")

        # Right half: digits 5–8 (incl. check) encoded with Set C.
        right_modules: tuple[int, ...] = ()
        for i in range(4):
            right_modules += encode_digit(int(data[4 + i]), "C")

        # Assemble row 0: left_guard(3) + left_data(28) + centre_guard(5) + right_data(28) + right_guard(3) = 67
        row0: tuple[int, ...] = NORMAL_GUARD + left_modules + CENTRE_GUARD + right_modules + NORMAL_GUARD
        assert len(row0) == 67, f"EAN-8 row 0 must be 67 modules, got {len(row0)}"  # noqa: S101

        # Build row 1: guard extension mask — dark only at guard bar positions.
        row1: tuple[int, ...] = tuple(1 if pos in _GUARD_EXTENSION_POSITIONS else 0 for pos in range(67))

        # --- Assemble result ---
        matrix = ModuleMatrix(
            width=67,
            height=2,
            modules=(row0, row1),
            row_heights_x=(EAN8_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X),
        )
        metadata = SymbolMetadata(
            symbology="ean8",
            normalized_data=data,
            display_text=data,
            input_kind="text",
        )
        return EncodedSymbol(matrix=matrix, metadata=metadata)
