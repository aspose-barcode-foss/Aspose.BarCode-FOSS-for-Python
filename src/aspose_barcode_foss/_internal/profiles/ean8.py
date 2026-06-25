"""EAN-8 profile."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.profiles.base import SymbologyProfile


@dataclass(slots=True, frozen=True)
class Ean8Profile(SymbologyProfile):
    """Profile for EAN-8 defaults, capabilities, and text behavior."""
