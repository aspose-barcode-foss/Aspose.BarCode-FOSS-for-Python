"""Golden-vector tests for Code 39 encoding."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.code39 import Code39Encoder
from aspose_barcode_foss._internal.models.options import Code39EncodeMode
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from tests.encoding.vectors.code39 import (
    CODE39_BASE_GOLDEN_VECTORS,
    CODE39EXT_GOLDEN_VECTORS,
    Code39Vector,
)


def _build_payload(vector: Code39Vector) -> NormalizedPayload:
    """Return the Code 39 test payload shape for a vector."""
    return NormalizedPayload(
        symbology="code39ext" if vector.full_ascii else "code39",
        data=vector.input_data,
        input_kind="text",
        code39_encode_mode=Code39EncodeMode.FULL_ASCII if vector.full_ascii else Code39EncodeMode.BASE,
        code39_add_check_digit=vector.add_check_digit,
    )


def _render_modules(vector: Code39Vector) -> tuple[str, ...]:
    """Encode one vector and flatten the module rows for assertion."""
    symbol = Code39Encoder().encode(_build_payload(vector))
    return tuple("".join(str(module) for module in row) for row in symbol.matrix.modules)


@pytest.mark.parametrize(
    "vector",
    CODE39_BASE_GOLDEN_VECTORS + CODE39EXT_GOLDEN_VECTORS,
    ids=lambda vector: vector.input_data.encode("unicode_escape").decode("ascii"),
)
def test_code39_encoder_matches_golden_modules(vector: Code39Vector) -> None:
    """Code 39 encoding should match a known-good module sequence."""
    symbol = Code39Encoder().encode(_build_payload(vector))
    actual_rows = tuple("".join(str(module) for module in row) for row in symbol.matrix.modules)

    assert actual_rows == vector.expected_modules
    assert symbol.matrix.height == 1


def test_code39_encoder_renders_display_text() -> None:
    """Display text should exclude sentinels/check char and escape control characters."""
    code_39_vector = next(
        vector for vector in CODE39_BASE_GOLDEN_VECTORS if vector.input_data == "CODE 39" and vector.add_check_digit
    )
    ht_vector = next(vector for vector in CODE39EXT_GOLDEN_VECTORS if vector.input_data == chr(9))
    del_vector = next(vector for vector in CODE39EXT_GOLDEN_VECTORS if vector.input_data == chr(127))

    code_39_symbol = Code39Encoder().encode(_build_payload(code_39_vector))
    ht_symbol = Code39Encoder().encode(_build_payload(ht_vector))
    del_symbol = Code39Encoder().encode(_build_payload(del_vector))

    assert code_39_symbol.metadata.display_text == "CODE 39"
    assert ht_symbol.metadata.display_text == "<HT>"
    assert del_symbol.metadata.display_text == "<DEL>"
