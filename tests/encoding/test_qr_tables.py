"""Contract tests for QR capacity tables, alignment centres, and byte-mode bitstream."""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.alignment import alignment_centers
from aspose_barcode_foss._internal.standards.qr.bitstream import build_data_codewords
from aspose_barcode_foss._internal.standards.qr.segments import QrMode, Segment
from aspose_barcode_foss._internal.standards.qr.tables import (
    EC_CHARACTERISTICS,
    byte_count_bits,
    symbol_size,
)


def test_ec_characteristics_self_consistent() -> None:
    for key, (total_cw, data_cw, ec_blk, num_blocks, groups) in EC_CHARACTERISTICS.items():
        assert data_cw + ec_blk * num_blocks == total_cw, f"total mismatch for {key}"
        assert sum(count * k for count, k in groups) == data_cw, f"data-per-block mismatch for {key}"
        assert sum(count for count, _ in groups) == num_blocks, f"block-count mismatch for {key}"


def test_symbol_size_endpoints() -> None:
    assert symbol_size(1) == 21
    assert symbol_size(40) == 177


def test_alignment_centers_anchors() -> None:
    assert alignment_centers(1) == []
    assert alignment_centers(5) == [(30, 30)]


def test_byte_count_bits_boundaries() -> None:
    assert byte_count_bits(9) == 8
    assert byte_count_bits(10) == 16
    assert byte_count_bits(40) == 16


def test_build_data_codewords_byte_mode_anchor() -> None:
    codewords = build_data_codewords([Segment(QrMode.BYTE, "QR Code")], 1, "M")
    assert len(codewords) == 16
    assert codewords[-7:] == [236, 17, 236, 17, 236, 17, 236]
