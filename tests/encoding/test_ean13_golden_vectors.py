"""Golden-vector tests for EAN-13 encoding.

Parametrized over all ten EAN-13 vectors (one per first digit, covering every
parity row in ISO/IEC 15420:2009 Table 3). Each test builds a NormalizedPayload
directly — without going through Ean13InputParser — so the tests remain valid
even if the parser has independent issues.
"""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.ean13 import Ean13Encoder
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.standards.ean import EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X
from tests.encoding.vectors.ean13 import EAN13_GOLDEN_VECTORS, Ean13Vector

# Guard-bar positions that must be dark in the extension row (row 1).
_GUARD_DARK_POSITIONS: frozenset[int] = frozenset({0, 2, 46, 48, 92, 94})


def _build_payload(data13: str) -> NormalizedPayload:
    """Return a minimal, pre-validated EAN-13 payload for the given 13-digit string."""
    return NormalizedPayload(symbology="ean13", data=data13, input_kind="text")


@pytest.mark.parametrize("vector", EAN13_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean13_row0_matches_golden_module_string(vector: Ean13Vector) -> None:
    """Row 0 of the encoded EAN-13 symbol should match the pre-computed module string."""
    symbol = Ean13Encoder().encode(_build_payload(vector.input_data))
    actual_row0 = "".join(str(bit) for bit in symbol.matrix.modules[0])

    assert actual_row0 == vector.expected_row0


@pytest.mark.parametrize("vector", EAN13_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean13_matrix_dimensions(vector: Ean13Vector) -> None:
    """EAN-13 matrix must be exactly 95 modules wide and 2 rows tall."""
    symbol = Ean13Encoder().encode(_build_payload(vector.input_data))

    assert symbol.matrix.width == 95
    assert symbol.matrix.height == 2


@pytest.mark.parametrize("vector", EAN13_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean13_row_heights_match_iso_constants(vector: Ean13Vector) -> None:
    """Row heights must match the ISO 15420 dimensional constants."""
    symbol = Ean13Encoder().encode(_build_payload(vector.input_data))

    assert symbol.matrix.row_heights_x == pytest.approx((EAN_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X))


@pytest.mark.parametrize("vector", EAN13_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean13_row1_guard_extension_mask(vector: Ean13Vector) -> None:
    """Row 1 must have dark modules only at guard-bar extension positions {0,2,46,48,92,94}."""
    symbol = Ean13Encoder().encode(_build_payload(vector.input_data))
    row1 = symbol.matrix.modules[1]

    actual_dark = {pos for pos, bit in enumerate(row1) if bit == 1}
    assert actual_dark == _GUARD_DARK_POSITIONS


@pytest.mark.parametrize("vector", EAN13_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean13_metadata_fields(vector: Ean13Vector) -> None:
    """Symbol metadata must reflect the normalized 13-digit input and display text."""
    symbol = Ean13Encoder().encode(_build_payload(vector.input_data))

    assert symbol.metadata.symbology == "ean13"
    assert symbol.metadata.input_kind == "text"
    assert symbol.metadata.normalized_data == vector.input_data
    assert symbol.metadata.display_text == vector.input_data
