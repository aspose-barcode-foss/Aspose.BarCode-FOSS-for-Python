"""QR Code profile."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.profiles.base import SymbologyProfile


@dataclass(slots=True, frozen=True)
class QrProfile(SymbologyProfile):
    """Profile for QR Code defaults and text behavior."""
