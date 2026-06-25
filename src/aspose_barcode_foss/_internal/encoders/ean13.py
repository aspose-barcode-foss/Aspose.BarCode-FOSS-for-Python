"""EAN-13 encoder."""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import Ean13Options, EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.standards.ean import (
    CENTRE_GUARD,
    EAN13_PARITY,
    EAN_BAR_HEIGHT_X,
    EAN_GUARD_EXTENSION_X,
    NORMAL_GUARD,
    encode_digit,
)

# Absolute positions in the 95-module row that carry guard bar dark modules in row 1.
# Left guard: 0, 2; Centre guard: 46, 48; Right guard: 92, 94.
_GUARD_EXTENSION_POSITIONS: frozenset[int] = frozenset({0, 2, 46, 48, 92, 94})


class Ean13Encoder(SymbologyEncoder):
    """Encode normalized payloads into EAN-13 symbols."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: Ean13Options | EncodeOptions | None = None,
    ) -> EncodedSymbol:
        """Encode an EAN-13 payload into a 95-module, 2-row ModuleMatrix.

        Row 0 contains the full 95-module symbol sequence.
        Row 1 is a guard-extension mask with dark modules only at the guard bar
        positions (absolute indices 0, 2, 46, 48, 92, 94).

        Args:
            payload: Normalized payload with ``symbology="ean13"``,
                ``input_kind="text"``, and ``data`` as a 13-digit string.
            options: Optional encoder options (currently unused).

        Returns:
            An :class:`EncodedSymbol` containing the module matrix and metadata.

        Raises:
            InvalidInputError: If the payload symbology, input kind, or data
                do not satisfy EAN-13 requirements.
        """
        # --- Validate payload ---
        if payload.symbology != "ean13":
            raise InvalidInputError(f"EAN-13 encoder requires symbology='ean13', got {payload.symbology!r}")
        if payload.input_kind != "text":
            raise InvalidInputError(f"EAN-13 encoder requires input_kind='text', got {payload.input_kind!r}")
        data = payload.data
        if not isinstance(data, str) or len(data) != 13 or not all("0" <= ch <= "9" for ch in data):
            raise InvalidInputError(f"EAN-13 data must be a string of exactly 13 digits, got {data!r}")

        # --- Encoding ---
        first_digit = int(data[0])
        parity = EAN13_PARITY[first_digit]

        # Left half: digits 1–6 encoded with the parity-selected number set (A or B).
        left_modules: tuple[int, ...] = ()
        for i in range(6):
            left_modules += encode_digit(int(data[1 + i]), parity[i])

        # Right half: digits 7–12 encoded with Set C.
        right_modules: tuple[int, ...] = ()
        for i in range(6):
            right_modules += encode_digit(int(data[7 + i]), "C")

        # Assemble row 0: left_guard(3) + left_data(42) + centre_guard(5) + right_data(42) + right_guard(3) = 95
        row0: tuple[int, ...] = NORMAL_GUARD + left_modules + CENTRE_GUARD + right_modules + NORMAL_GUARD
        assert len(row0) == 95, f"EAN-13 row 0 must be 95 modules, got {len(row0)}"  # noqa: S101

        # Build row 1: guard extension mask — dark only at guard bar positions.
        row1: tuple[int, ...] = tuple(1 if pos in _GUARD_EXTENSION_POSITIONS else 0 for pos in range(95))

        # --- Assemble result ---
        matrix = ModuleMatrix(
            width=95,
            height=2,
            modules=(row0, row1),
            row_heights_x=(EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X),
        )
        metadata = SymbolMetadata(
            symbology="ean13",
            normalized_data=data,
            display_text=data,
            input_kind="text",
        )
        return EncodedSymbol(matrix=matrix, metadata=metadata)
