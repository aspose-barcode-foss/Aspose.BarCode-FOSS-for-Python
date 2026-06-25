"""Contract tests for QR format-information and version-information strings."""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.info_strings import (
    FORMAT_INFO,
    VERSION_INFO,
    format_info,
    version_info,
)


def test_format_info_matches_spec_i() -> None:
    for ecc in ("L", "M", "Q", "H"):
        for mask in range(8):
            assert (ecc, mask) in FORMAT_INFO, f"missing key ({ecc!r}, {mask})"
            assert format_info(ecc, mask) == FORMAT_INFO[(ecc, mask)], f"format_info mismatch for ({ecc!r}, {mask})"


def test_version_info_matches_spec_j() -> None:
    for version in range(7, 41):
        assert version_info(version) == VERSION_INFO[version], f"version_info mismatch for v={version}"
