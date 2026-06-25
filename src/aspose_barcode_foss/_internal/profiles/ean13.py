"""EAN-13 profile."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.profiles.base import SymbologyProfile


@dataclass(slots=True, frozen=True)
class Ean13Profile(SymbologyProfile):
    """Profile for EAN-13 defaults, capabilities, and text behavior."""
