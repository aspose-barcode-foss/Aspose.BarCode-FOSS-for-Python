"""Contract tests for logical barcode symbol models."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata


def test_module_matrix_linear_dimensions_and_get() -> None:
    """A 1 x N matrix should expose zero-based row access."""
    matrix = ModuleMatrix(
        width=1,
        height=4,
        modules=((1,), (0,), (1,), (1,)),
    )

    assert matrix.width == 1
    assert matrix.height == 4
    assert matrix.modules == ((1,), (0,), (1,), (1,))
    assert matrix.get(0, 0) == 1
    assert matrix.get(0, 1) == 0
    assert matrix.get(0, 2) == 1
    assert matrix.get(0, 3) == 1


def test_module_matrix_rectangular_dimensions_and_get() -> None:
    """A rectangular matrix should read values using modules[y][x]."""
    matrix = ModuleMatrix(
        width=3,
        height=2,
        modules=((1, 0, 1), (0, 1, 0)),
    )

    assert matrix.width == 3
    assert matrix.height == 2
    assert matrix.modules == ((1, 0, 1), (0, 1, 0))
    assert matrix.get(0, 0) == 1
    assert matrix.get(1, 0) == 0
    assert matrix.get(2, 0) == 1
    assert matrix.get(0, 1) == 0
    assert matrix.get(1, 1) == 1
    assert matrix.get(2, 1) == 0


@pytest.mark.parametrize(
    ("width", "height", "modules"),
    [
        (0, 1, ((),)),
        (-1, 1, ((1,),)),
        (1, 0, ()),
        (1, -1, ((1,),)),
    ],
)
def test_module_matrix_rejects_non_positive_dimensions(
    width: int,
    height: int,
    modules: tuple[tuple[int, ...], ...],
) -> None:
    """Matrix dimensions must be strictly positive."""
    with pytest.raises(ValueError):
        ModuleMatrix(width=width, height=height, modules=modules)


def test_module_matrix_rejects_row_count_mismatch() -> None:
    """Row count must match the declared height."""
    with pytest.raises(ValueError):
        ModuleMatrix(
            width=2,
            height=3,
            modules=((1, 0), (0, 1)),
        )


def test_module_matrix_rejects_row_width_mismatch() -> None:
    """Every row must match the declared width."""
    with pytest.raises(ValueError):
        ModuleMatrix(
            width=2,
            height=2,
            modules=((1, 0), (1,)),
        )


@pytest.mark.parametrize(
    "modules",
    [
        ((True, 0),),
        ((1, False),),
        ((2, 0),),
        ((-1, 1),),
        (("dark", 0),),
    ],
)
def test_module_matrix_rejects_non_binary_integer_module_values(
    modules: tuple[tuple[object, ...], ...],
) -> None:
    """Module values must be literal 0 or 1 integers."""
    with pytest.raises(ValueError):
        ModuleMatrix(width=2, height=1, modules=modules)


@pytest.mark.parametrize(
    ("x", "y"),
    [(-1, 0), (0, -1), (2, 0), (0, 2)],
)
def test_module_matrix_get_rejects_out_of_bounds_coordinates(x: int, y: int) -> None:
    """Coordinate access should reject negative and out-of-range values."""
    matrix = ModuleMatrix(
        width=2,
        height=2,
        modules=((1, 0), (0, 1)),
    )

    with pytest.raises(IndexError):
        matrix.get(x, y)


def test_symbol_metadata_accepts_text_payloads() -> None:
    """Text metadata should accept string payloads."""
    metadata = SymbolMetadata(
        symbology="code128",
        normalized_data="ABC123",
        display_text="ABC123",
        input_kind="text",
    )

    assert metadata.symbology == "code128"
    assert metadata.normalized_data == "ABC123"
    assert metadata.display_text == "ABC123"
    assert metadata.input_kind == "text"
    assert metadata.gs1_enabled is False
    assert metadata.eci_assignment_number is None


def test_symbol_metadata_accepts_binary_payloads() -> None:
    """Binary metadata should accept bytes payloads."""
    payload = b"\x00\xff"
    metadata = SymbolMetadata(
        symbology="code128",
        normalized_data=payload,
        display_text="",
        input_kind="binary",
    )

    assert metadata.symbology == "code128"
    assert metadata.normalized_data == payload
    assert metadata.display_text == ""
    assert metadata.input_kind == "binary"


def test_symbol_metadata_rejects_empty_symbology() -> None:
    """Symbology names must not be empty."""
    with pytest.raises(ValueError):
        SymbolMetadata(
            symbology="",
            normalized_data="ABC123",
            display_text="ABC123",
            input_kind="text",
        )


def test_symbol_metadata_rejects_text_kind_with_bytes_data() -> None:
    """Text input kind should not accept bytes payloads."""
    with pytest.raises(ValueError):
        SymbolMetadata(
            symbology="code128",
            normalized_data=b"ABC123",
            display_text="ABC123",
            input_kind="text",
        )


def test_symbol_metadata_rejects_binary_kind_with_string_data() -> None:
    """Binary input kind should not accept string payloads."""
    with pytest.raises(ValueError):
        SymbolMetadata(
            symbology="code128",
            normalized_data="ABC123",
            display_text="ABC123",
            input_kind="binary",
        )


def test_encoded_symbol_preserves_validated_components() -> None:
    """EncodedSymbol should stay a thin bundle of matrix and metadata."""
    matrix = ModuleMatrix(
        width=2,
        height=1,
        modules=((1, 0),),
    )
    metadata = SymbolMetadata(
        symbology="code128",
        normalized_data="ABC123",
        display_text="ABC123",
        input_kind="text",
    )

    symbol = EncodedSymbol(matrix=matrix, metadata=metadata)

    assert symbol.matrix is matrix
    assert symbol.metadata is metadata


def test_module_matrix_accepts_valid_row_heights_x() -> None:
    matrix = ModuleMatrix(
        width=3,
        height=2,
        modules=((1, 0, 1), (0, 1, 0)),
        row_heights_x=(10.0, 2.5),
    )

    assert matrix.row_heights_x == (10.0, 2.5)


def test_module_matrix_row_heights_x_defaults_to_none() -> None:
    matrix = ModuleMatrix(
        width=3,
        height=2,
        modules=((1, 0, 1), (0, 1, 0)),
    )

    assert matrix.row_heights_x is None


def test_module_matrix_rejects_row_heights_x_length_mismatch() -> None:
    with pytest.raises(ValueError):
        ModuleMatrix(
            width=3,
            height=2,
            modules=((1, 0, 1), (0, 1, 0)),
            row_heights_x=(5.0,),
        )


@pytest.mark.parametrize(
    "row_heights_x",
    [
        (5.0, 0.0),
        (5.0, -1.0),
        (5.0, True),
        (5.0, "2.0"),
    ],
)
def test_module_matrix_rejects_invalid_row_heights_x_values(
    row_heights_x: tuple[object, ...],
) -> None:
    with pytest.raises(ValueError):
        ModuleMatrix(
            width=3,
            height=2,
            modules=((1, 0, 1), (0, 1, 0)),
            row_heights_x=row_heights_x,
        )
