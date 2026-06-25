"""Golden-vector tests for UPC-E encoding.

Parametrized over all UPC-E vectors (covering each zero-suppression rule and
multiple parity table rows). Each test builds a NormalizedPayload directly —
without going through UpceInputParser — so the tests remain valid even if the
parser has independent issues.

UPC-E structure (51 modules):
    NORMAL_GUARD(3) + 6×encoded_digits(42) + SPECIAL_GUARD(6) = 51 modules

Row 1 (guard extension mask) is dark only at the guard bar positions:
    Left normal guard bars: {0, 2}
    Right special guard bars: {46, 48, 50}
    Combined: {0, 2, 46, 48, 50}
"""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.upce import UpceEncoder
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.standards.ean import EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X
from tests.encoding.vectors.upce import UPCE_GOLDEN_VECTORS, UpceVector

# Fixed guard-bar positions that must always be dark in the extension row (row 1).
# Left normal guard (101): dark at absolute positions 0 and 2.
# Right special guard (010101): starts at module 45; dark at absolute positions 46, 48, 50.
_GUARD_EXTENSION_POSITIONS: frozenset[int] = frozenset({0, 2, 46, 48, 50})

# The special right guard occupies the last 6 modules of a 51-module row (indices 45–50).
# Its bit pattern is "010101", so dark modules land at relative offsets 1, 3, 5 → absolute 46, 48, 50.
_SPECIAL_GUARD_MODULE_STRING: str = "010101"
_SPECIAL_GUARD_START: int = 45


def _build_payload(data12: str) -> NormalizedPayload:
    """Return a minimal, pre-validated UPC-E payload for the given 12-digit GTIN-12 string."""
    return NormalizedPayload(symbology="upce", data=data12, input_kind="text")


@pytest.mark.parametrize("vector", UPCE_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upce_row0_matches_golden_module_string(vector: UpceVector) -> None:
    """Row 0 of the encoded UPC-E symbol should match the pre-computed module string."""
    symbol = UpceEncoder().encode(_build_payload(vector.input_data))
    actual_row0 = "".join(str(bit) for bit in symbol.matrix.modules[0])

    assert actual_row0 == vector.expected_row0


@pytest.mark.parametrize("vector", UPCE_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upce_matrix_dimensions(vector: UpceVector) -> None:
    """UPC-E matrix must be exactly 51 modules wide and 2 rows tall."""
    symbol = UpceEncoder().encode(_build_payload(vector.input_data))

    assert symbol.matrix.width == 51
    assert symbol.matrix.height == 2


@pytest.mark.parametrize("vector", UPCE_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upce_row_heights_match_iso_constants(vector: UpceVector) -> None:
    """Row heights must match the ISO 15420 dimensional constants."""
    symbol = UpceEncoder().encode(_build_payload(vector.input_data))

    assert symbol.matrix.row_heights_x == pytest.approx((EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X))


@pytest.mark.parametrize("vector", UPCE_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upce_row1_guard_dark_positions(vector: UpceVector) -> None:
    """Row 1 must have dark modules at exactly the guard bar positions {0, 2, 46, 48, 50}.

    UPC-E has no extended data character bars (unlike UPC-A which extends the first and
    last data characters). Only the left normal guard and right special guard contribute
    dark modules to the extension row, and these positions are always fixed regardless
    of digit values.
    """
    symbol = UpceEncoder().encode(_build_payload(vector.input_data))
    row1 = symbol.matrix.modules[1]

    actual_dark = {pos for pos, bit in enumerate(row1) if bit == 1}

    assert actual_dark == _GUARD_EXTENSION_POSITIONS


@pytest.mark.parametrize("vector", UPCE_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upce_row0_ends_with_special_guard(vector: UpceVector) -> None:
    """The last 6 modules of row 0 must be the special right guard pattern '010101'.

    The special guard occupies modules 45–50 (0-based) of the 51-module row.
    """
    symbol = UpceEncoder().encode(_build_payload(vector.input_data))
    row0 = symbol.matrix.modules[0]

    actual_tail = "".join(str(bit) for bit in row0[_SPECIAL_GUARD_START:])

    assert actual_tail == _SPECIAL_GUARD_MODULE_STRING


@pytest.mark.parametrize("vector", UPCE_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_upce_metadata_fields(vector: UpceVector) -> None:
    """Symbol metadata must reflect the normalized 12-digit GTIN-12 input and display text."""
    symbol = UpceEncoder().encode(_build_payload(vector.input_data))

    assert symbol.metadata.symbology == "upce"
    assert symbol.metadata.input_kind == "text"
    assert symbol.metadata.normalized_data == vector.input_data
    assert symbol.metadata.display_text == vector.input_data
