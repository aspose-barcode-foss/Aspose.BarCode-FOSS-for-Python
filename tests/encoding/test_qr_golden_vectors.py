"""Golden-vector tests for QR Code (ISO/IEC 18004) encoding."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.qr import QrEncoder
from aspose_barcode_foss._internal.models.options import QrOptions
from aspose_barcode_foss._internal.parsers.qr import QrInputParser
from aspose_barcode_foss._internal.standards.qr import segmentation, segments
from aspose_barcode_foss._internal.standards.qr.bitstream import build_data_codewords
from tests.encoding.vectors.qr import (
    QR_GOLDEN_VECTORS,
    QR_MODE_CODEWORD_VECTORS,
    QrCodewordVector,
    QrVector,
)


def _render_modules(vector: QrVector) -> tuple[str, ...]:
    """Encode one vector at its pinned (version, ECC, mask) and flatten the grid."""
    payload = QrInputParser().parse(
        vector.input_data,
        options=QrOptions(
            error_correction_level=vector.ecc_level,
            version=vector.version,
            mask=vector.mask,
            encoding_mode=vector.encoding_mode,
            eci_assignment_number=vector.eci,
        ),
    )
    symbol = QrEncoder().encode(payload)
    return tuple("".join(str(module) for module in row) for row in symbol.matrix.modules)


@pytest.mark.parametrize(
    "vector",
    QR_GOLDEN_VECTORS,
    ids=lambda vector: f"v{vector.version}-{vector.ecc_level}-mask{vector.mask}",
)
def test_qr_encoder_matches_golden_modules(vector: QrVector) -> None:
    """QR encoding should reproduce the oracle-sourced grid for its pinned parameters."""
    assert _render_modules(vector) == vector.expected_modules


@pytest.mark.parametrize(
    "vector",
    QR_GOLDEN_VECTORS,
    ids=lambda vector: f"v{vector.version}-{vector.ecc_level}-mask{vector.mask}",
)
def test_qr_encoder_emits_square_matrix(vector: QrVector) -> None:
    """The encoded matrix should be the bare N*N grid where N = 4*version + 17."""
    payload = QrInputParser().parse(
        vector.input_data,
        options=QrOptions(
            error_correction_level=vector.ecc_level,
            version=vector.version,
            mask=vector.mask,
            encoding_mode=vector.encoding_mode,
            eci_assignment_number=vector.eci,
        ),
    )
    symbol = QrEncoder().encode(payload)
    expected_dimension = 4 * vector.version + 17

    assert symbol.matrix.width == expected_dimension
    assert symbol.matrix.height == expected_dimension


@pytest.mark.parametrize(
    "vector",
    QR_MODE_CODEWORD_VECTORS,
    ids=lambda vector: f"{vector.encoding_mode}-v{vector.version}-{vector.ecc_level}",
)
def test_qr_mode_codewords_match_spec_derivation(vector: QrCodewordVector) -> None:
    """Encoder data codewords should equal the spec-derived ground truth.

    The expected codewords are NOT produced by the encoder: they are the normative
    ISO/IEC 18004 §7.4.6 (Kanji 13-bit packing) / §7.4.2 (ECI header) bit strings, transcribed
    and byte-split by hand. This test pins the standards-layer data-codeword assembly against
    that independent derivation.
    """
    mode = segments.QrMode[vector.encoding_mode.upper()]
    built = build_data_codewords(
        segmentation.forced_segments(vector.input_data, mode),
        vector.version,
        vector.ecc_level,
        eci_assignment_number=vector.eci,
    )
    assert tuple(built) == vector.expected_codewords
