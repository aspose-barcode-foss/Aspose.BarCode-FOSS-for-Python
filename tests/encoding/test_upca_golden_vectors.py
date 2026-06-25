"""Golden-vector tests for UPC-A encoding.

Parametrized over all five UPC-A vectors (covering first digits 0, 1, 3, 4, 9).
Each test builds a NormalizedPayload directly — without going through UpcaInputParser —
so the tests remain valid even if the parser has independent issues.
"""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.upca import UpcaEncoder
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.standards.ean import EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X
from tests.encoding.vectors.upca import UPCA_GOLDEN_VECTORS, UpcaVector

# Guard-bar positions that must always be dark in the extension row (row 1).
_GUARD_DARK_POSITIONS: frozenset[int] = frozenset({0, 2, 46, 48, 92, 94})

# Slice boundaries for the first and last data character extension ranges.
_D1_SLICE = range(3, 10)
_D12_SLICE = range(85, 92)

# Positions that are never part of the guard/data-extension ranges (ordinary data bars).
_INNER_LEFT_RANGE = range(10, 46)
_INNER_RIGHT_RANGE = range(50, 85)


def _build_payload(data12: str) -> NormalizedPayload:
    """Return a minimal, pre-validated UPC-A payload for the given 12-digit string."""
    return NormalizedPayload(symbology="upca", data=data12, input_kind="text")


@pytest.mark.parametrize("vector", UPCA_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upca_row0_matches_golden_module_string(vector: UpcaVector) -> None:
    """Row 0 of the encoded UPC-A symbol should match the pre-computed module string."""
    symbol = UpcaEncoder().encode(_build_payload(vector.input_data))
    actual_row0 = "".join(str(bit) for bit in symbol.matrix.modules[0])

    assert actual_row0 == vector.expected_row0


@pytest.mark.parametrize("vector", UPCA_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upca_matrix_dimensions(vector: UpcaVector) -> None:
    """UPC-A matrix must be exactly 95 modules wide and 2 rows tall."""
    symbol = UpcaEncoder().encode(_build_payload(vector.input_data))

    assert symbol.matrix.width == 95
    assert symbol.matrix.height == 2


@pytest.mark.parametrize("vector", UPCA_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upca_row_heights_match_iso_constants(vector: UpcaVector) -> None:
    """Row heights must match the ISO 15420 dimensional constants."""
    symbol = UpcaEncoder().encode(_build_payload(vector.input_data))

    assert symbol.matrix.row_heights_x == pytest.approx((EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X))


@pytest.mark.parametrize("vector", UPCA_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upca_row1_guard_and_extension_mask(vector: UpcaVector) -> None:
    """Row 1 must have dark modules at guard positions and at dark modules in D1/D12 ranges.

    Expected dark positions = fixed guard positions
        ∪ {pos ∈ [3,10) : row0[pos] == 1}
        ∪ {pos ∈ [85,92) : row0[pos] == 1}

    The expected set is derived from the validated row0 (which is itself checked by
    test_upca_row0_matches_golden_module_string), so this test remains independent of
    any specific digit pattern.
    """
    symbol = UpcaEncoder().encode(_build_payload(vector.input_data))
    row0 = symbol.matrix.modules[0]
    row1 = symbol.matrix.modules[1]

    expected_dark = set(_GUARD_DARK_POSITIONS)
    for pos in _D1_SLICE:
        if row0[pos] == 1:
            expected_dark.add(pos)
    for pos in _D12_SLICE:
        if row0[pos] == 1:
            expected_dark.add(pos)

    actual_dark = {pos for pos, bit in enumerate(row1) if bit == 1}
    assert actual_dark == expected_dark


@pytest.mark.parametrize("vector", UPCA_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upca_row1_no_inner_data_bars(vector: UpcaVector) -> None:
    """Row 1 must be entirely dark-free in the ordinary inner data bar ranges.

    Positions 10–45 (left data characters 2–6) and 50–84 (right data characters 1–5)
    must all be 0 in row 1, regardless of whether they are dark in row 0.
    """
    symbol = UpcaEncoder().encode(_build_payload(vector.input_data))
    row1 = symbol.matrix.modules[1]

    for pos in _INNER_LEFT_RANGE:
        assert row1[pos] == 0, f"Expected row1[{pos}] == 0, got {row1[pos]}"
    for pos in _INNER_RIGHT_RANGE:
        assert row1[pos] == 0, f"Expected row1[{pos}] == 0, got {row1[pos]}"


@pytest.mark.parametrize("vector", UPCA_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upca_metadata_fields(vector: UpcaVector) -> None:
    """Symbol metadata must reflect the normalized 12-digit input and display text."""
    symbol = UpcaEncoder().encode(_build_payload(vector.input_data))

    assert symbol.metadata.symbology == "upca"
    assert symbol.metadata.input_kind == "text"
    assert symbol.metadata.normalized_data == vector.input_data
    assert symbol.metadata.display_text == vector.input_data
