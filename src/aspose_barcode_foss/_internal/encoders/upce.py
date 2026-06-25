"""UPC-E encoder."""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import EncodeOptions, UpceOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.standards.ean import (
    EAN_BAR_HEIGHT_X,
    EAN_GUARD_EXTENSION_X,
    NORMAL_GUARD,
    SPECIAL_GUARD,
    UPCE_PARITY,
    encode_digit,
    upce_zero_suppress,
)

# Absolute positions in the 51-module row that carry guard bar dark modules in row 1.
# Left guard (101): bars at 0 and 2.
# Special right guard (010101): starts at module 45; bars at relative positions 1, 3, 5 → absolute 46, 48, 50.
_GUARD_EXTENSION_POSITIONS: frozenset[int] = frozenset({0, 2, 46, 48, 50})


class UpceEncoder(SymbologyEncoder):
    """Encode normalized payloads into UPC-E symbols."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: UpceOptions | EncodeOptions | None = None,
    ) -> EncodedSymbol:
        """Encode a UPC-E payload into a 51-module, 2-row ModuleMatrix.

        Row 0 contains the full 51-module symbol sequence.
        Row 1 is a guard-extension mask with dark modules only at the guard bar
        positions (absolute indices 0, 2, 46, 48, 50).

        Args:
            payload: Normalized payload with ``symbology="upce"``,
                ``input_kind="text"``, and ``data`` as a 12-digit string
                whose first digit is ``"0"``.
            options: Optional encoder options (currently unused).

        Returns:
            An :class:`EncodedSymbol` containing the module matrix and metadata.

        Raises:
            InvalidInputError: If the payload symbology, input kind, or data
                do not satisfy UPC-E requirements, or if the GTIN-12 is not
                zero-suppressible into a valid UPC-E form.
        """
        # --- Validate payload ---
        if payload.symbology != "upce":
            raise InvalidInputError(f"UPC-E encoder requires symbology='upce', got {payload.symbology!r}")
        if payload.input_kind != "text":
            raise InvalidInputError(f"UPC-E encoder requires input_kind='text', got {payload.input_kind!r}")
        data = payload.data
        if not isinstance(data, str) or len(data) != 12 or not all("0" <= ch <= "9" for ch in data):
            raise InvalidInputError(f"UPC-E data must be a string of exactly 12 digits, got {data!r}")
        if data[0] != "0":
            raise InvalidInputError(f"UPC-E data must begin with '0' (number system digit), got {data[0]!r}")

        # --- Zero suppression: derive 6-character UPC-E explicit digits ---
        compressed = upce_zero_suppress(data)
        if compressed is None:
            raise InvalidInputError(f"GTIN-12 {data!r} cannot be zero-suppressed into a valid UPC-E symbol")

        # --- Encoding ---
        check_digit = int(data[-1])
        parity = UPCE_PARITY[check_digit]

        data_modules: tuple[int, ...] = ()
        for i in range(6):
            data_modules += encode_digit(int(compressed[i]), parity[i])

        # Assemble row 0: left_guard(3) + data(42) + special_guard(6) = 51
        row0: tuple[int, ...] = NORMAL_GUARD + data_modules + SPECIAL_GUARD
        assert len(row0) == 51, f"UPC-E row 0 must be 51 modules, got {len(row0)}"  # noqa: S101

        # Build row 1: guard extension mask — dark only at guard bar positions.
        row1: tuple[int, ...] = tuple(1 if pos in _GUARD_EXTENSION_POSITIONS else 0 for pos in range(51))

        # --- Assemble result ---
        matrix = ModuleMatrix(
            width=51,
            height=2,
            modules=(row0, row1),
            row_heights_x=(EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X),
        )
        metadata = SymbolMetadata(
            symbology="upce",
            normalized_data=data,
            display_text=data,
            input_kind="text",
        )
        return EncodedSymbol(matrix=matrix, metadata=metadata)
