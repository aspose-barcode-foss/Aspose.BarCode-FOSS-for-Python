"""Contract tests for QR Reed-Solomon encoding and generator polynomials."""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.galois import (
    GENERATOR_POLYS_ALPHA,
    _alpha_to_int,
    rs_generator_poly,
)
from aspose_barcode_foss._internal.standards.qr.reed_solomon import rs_encode


def test_rs_encode_annex_i_anchor() -> None:
    data = [16, 32, 12, 86, 97, 128, 236, 17, 236, 17, 236, 17, 236, 17, 236, 17]
    assert rs_encode(data, 10) == [165, 36, 212, 193, 237, 54, 199, 135, 44, 85]


def test_generator_poly_matches_spec_d() -> None:
    for n in (7, 10, 13, 15, 16, 17, 18, 20, 22, 24, 26, 28, 30):
        expected = _alpha_to_int(GENERATOR_POLYS_ALPHA[n])
        assert rs_generator_poly(n) == expected, f"generator poly mismatch for n={n}"
