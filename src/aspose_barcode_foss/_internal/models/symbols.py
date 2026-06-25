"""Logical barcode symbol models."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.models.payloads import InputKind


@dataclass(slots=True, frozen=True)
class ModuleMatrix:
    """Logical module grid returned by an encoder."""

    width: int
    height: int
    modules: tuple[tuple[int, ...], ...]
    row_heights_x: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        """Validate matrix dimensions and module storage."""
        if self.width <= 0:
            raise ValueError("width must be a positive integer")
        if self.height <= 0:
            raise ValueError("height must be a positive integer")
        if len(self.modules) != self.height:
            raise ValueError("modules row count must match height")

        for row in self.modules:
            if len(row) != self.width:
                raise ValueError("each module row length must match width")
            for module in row:
                if type(module) is not int or module not in (0, 1):
                    raise ValueError("module values must be literal 0 or 1 integers")

        if self.row_heights_x is not None:
            if len(self.row_heights_x) != self.height:
                raise ValueError("row_heights_x length must match height")
            for v in self.row_heights_x:
                if type(v) not in (int, float):
                    raise ValueError("row_heights_x values must be int or float, not bool or other types")
                if v <= 0:
                    raise ValueError("row_heights_x values must be strictly greater than 0")

    def get(self, x: int, y: int) -> int:
        """Return the state of a single module."""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError("module coordinates out of bounds")
        return self.modules[y][x]


@dataclass(slots=True, frozen=True)
class SymbolMetadata:
    """Renderer-neutral metadata about an encoded symbol."""

    symbology: str
    normalized_data: str | bytes
    display_text: str
    input_kind: InputKind = "text"
    gs1_enabled: bool = False
    eci_assignment_number: int | None = None

    def __post_init__(self) -> None:
        """Validate local metadata invariants."""
        if not isinstance(self.symbology, str) or not self.symbology:
            raise ValueError("symbology must be a non-empty string")
        if self.input_kind == "text" and not isinstance(self.normalized_data, str):
            raise ValueError("text input_kind requires normalized_data to be str")
        if self.input_kind == "binary" and not isinstance(self.normalized_data, bytes):
            raise ValueError("binary input_kind requires normalized_data to be bytes")


@dataclass(slots=True, frozen=True)
class EncodedSymbol:
    """Encoded symbol returned by a symbology encoder."""

    matrix: ModuleMatrix
    metadata: SymbolMetadata
