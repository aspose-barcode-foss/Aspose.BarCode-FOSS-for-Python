"""Golden-vector tests for EAN-8 encoding.

Parametrized over the seven oracle-sourced EAN-8 vectors. Each test builds a
NormalizedPayload directly — without going through Ean8InputParser — so the
tests remain valid even if the parser has independent issues.
"""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.ean8 import Ean8Encoder
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.standards.ean import EAN8_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X
from tests.encoding.vectors.ean8 import EAN8_GOLDEN_VECTORS, Ean8Vector

_GUARD_DARK_POSITIONS: frozenset[int] = frozenset({0, 2, 32, 34, 64, 66})


def _build_payload(data8: str) -> NormalizedPayload:
    """Return a minimal, pre-validated EAN-8 payload for the given 8-digit string."""
    return NormalizedPayload(symbology="ean8", data=data8, input_kind="text")


@pytest.mark.parametrize("vector", EAN8_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean8_row0_matches_golden_module_string(vector: Ean8Vector) -> None:
    symbol = Ean8Encoder().encode(_build_payload(vector.input_data))
    actual_row0 = "".join(str(bit) for bit in symbol.matrix.modules[0])
    assert actual_row0 == vector.expected_row0


@pytest.mark.parametrize("vector", EAN8_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean8_matrix_dimensions(vector: Ean8Vector) -> None:
    symbol = Ean8Encoder().encode(_build_payload(vector.input_data))
    assert symbol.matrix.width == 67
    assert symbol.matrix.height == 2


@pytest.mark.parametrize("vector", EAN8_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean8_row_heights_match_iso_constants(vector: Ean8Vector) -> None:
    symbol = Ean8Encoder().encode(_build_payload(vector.input_data))
    assert symbol.matrix.row_heights_x == pytest.approx((EAN8_BAR_HEIGHT_X, EAN_GUARD_EXTENSION_X))


@pytest.mark.parametrize("vector", EAN8_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean8_row1_guard_extension_mask(vector: Ean8Vector) -> None:
    symbol = Ean8Encoder().encode(_build_payload(vector.input_data))
    row1 = symbol.matrix.modules[1]
    actual_dark = {pos for pos, bit in enumerate(row1) if bit == 1}
    assert actual_dark == _GUARD_DARK_POSITIONS


@pytest.mark.parametrize("vector", EAN8_GOLDEN_VECTORS, ids=lambda v: v.input_data)
def test_ean8_metadata_fields(vector: Ean8Vector) -> None:
    symbol = Ean8Encoder().encode(_build_payload(vector.input_data))
    assert symbol.metadata.symbology == "ean8"
    assert symbol.metadata.input_kind == "text"
    assert symbol.metadata.normalized_data == vector.input_data
    assert symbol.metadata.display_text == vector.input_data
