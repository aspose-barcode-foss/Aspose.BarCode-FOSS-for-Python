"""Contract tests for QR GF(256) arithmetic tables and multiplication."""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.galois import (
    EXP,
    LOG,
    _SPEC_EXP,
    _SPEC_LOG,
    gmul,
)


def test_exp_table_matches_spec_a() -> None:
    assert tuple(EXP[0:255]) == _SPEC_EXP


def test_log_table_matches_spec_a() -> None:
    assert tuple(LOG[1:256]) == _SPEC_LOG[1:256]


def test_gmul_zero_left() -> None:
    assert gmul(0, 5) == 0


def test_gmul_zero_right() -> None:
    assert gmul(7, 0) == 0


def test_gmul_identity() -> None:
    assert gmul(1, 200) == 200


def test_gmul_spec_a_product() -> None:
    assert gmul(2, 128) == 29
