"""UPC-A encoder."""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import EncodeOptions, UpcaOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.standards.ean import (
    CENTRE_GUARD,
    EAN_BAR_HEIGHT_X,
    EAN_GUARD_EXTENSION_X,
    NORMAL_GUARD,
    encode_digit,
)

# Absolute positions in the 95-module row that carry guard bar dark modules in row 1.
# Left guard: 0, 2; Centre guard: 46, 48; Right guard: 92, 94.
_GUARD_EXTENSION_POSITIONS: frozenset[int] = frozenset({0, 2, 46, 48, 92, 94})

# Slice boundaries for the first (D1) and last (D12) data character positions.
# D1 occupies modules 3–9 (inclusive); D12 occupies modules 85–91 (inclusive).
_D1_START: int = 3
_D1_END: int = 10  # exclusive upper bound: row0[3:10]
_D12_START: int = 85
_D12_END: int = 92  # exclusive upper bound: row0[85:92]


class UpcaEncoder(SymbologyEncoder):
    """Encode data into a UPC-A symbol."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: UpcaOptions | EncodeOptions | None = None,
    ) -> EncodedSymbol:
        """Encode a UPC-A payload into a 95-module, 2-row ModuleMatrix.

        Row 0 contains the full 95-module symbol sequence.
        Row 1 is a guard-extension mask with dark modules at guard bar positions
        (absolute indices 0, 2, 46, 48, 92, 94) and at all dark module positions
        within the first data character (modules 3–9) and last data character
        (modules 85–91), per ISO 15420:2009 §4.3.3.

        Args:
            payload: Normalized payload with ``symbology="upca"``,
                ``input_kind="text"``, and ``data`` as a 12-digit string.
            options: Optional encoder options (currently unused).

        Returns:
            An :class:`EncodedSymbol` containing the module matrix and metadata.

        Raises:
            InvalidInputError: If the payload symbology, input kind, or data
                do not satisfy UPC-A requirements.
        """
        # --- Validate payload ---
        if payload.symbology != "upca":
            raise InvalidInputError(f"UPC-A encoder requires symbology='upca', got {payload.symbology!r}")
        if payload.input_kind != "text":
            raise InvalidInputError(f"UPC-A encoder requires input_kind='text', got {payload.input_kind!r}")
        data = payload.data
        if not isinstance(data, str) or len(data) != 12 or not all("0" <= ch <= "9" for ch in data):
            raise InvalidInputError(f"UPC-A data must be a string of exactly 12 digits, got {data!r}")

        # --- Encoding ---
        # Left half: digits 0–5 encoded with Set A (no parity variation in UPC-A).
        left_modules: tuple[int, ...] = ()
        for i in range(6):
            left_modules += encode_digit(int(data[i]), "A")

        # Right half: digits 6–11 encoded with Set C.
        right_modules: tuple[int, ...] = ()
        for i in range(6):
            right_modules += encode_digit(int(data[6 + i]), "C")

        # Assemble row 0: left_guard(3) + left_data(42) + centre_guard(5) + right_data(42) + right_guard(3) = 95
        row0: tuple[int, ...] = NORMAL_GUARD + left_modules + CENTRE_GUARD + right_modules + NORMAL_GUARD
        assert len(row0) == 95, f"UPC-A row 0 must be 95 modules, got {len(row0)}"  # noqa: S101

        # Build row 1: guard extension mask.
        # Dark modules appear at fixed guard positions AND at all dark positions within
        # the first data character (D1, modules 3–9) and last data character (D12, modules 85–91).
        def _is_extension(pos: int) -> bool:
            if pos in _GUARD_EXTENSION_POSITIONS:
                return True
            if _D1_START <= pos < _D1_END and row0[pos] == 1:
                return True
            if _D12_START <= pos < _D12_END and row0[pos] == 1:
                return True
            return False

        row1: tuple[int, ...] = tuple(1 if _is_extension(pos) else 0 for pos in range(95))

        # --- Assemble result ---
        matrix = ModuleMatrix(
            width=95,
            height=2,
            modules=(row0, row1),
            row_heights_x=(EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X),
        )
        metadata = SymbolMetadata(
            symbology="upca",
            normalized_data=data,
            display_text=data,
            input_kind="text",
        )
        return EncodedSymbol(matrix=matrix, metadata=metadata)
