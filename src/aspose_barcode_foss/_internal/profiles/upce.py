"""UPC-E profile."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.profiles.base import SymbologyProfile


@dataclass(slots=True, frozen=True)
class UpceProfile(SymbologyProfile):
    """Profile for UPC-E defaults, capabilities, and text behavior."""
