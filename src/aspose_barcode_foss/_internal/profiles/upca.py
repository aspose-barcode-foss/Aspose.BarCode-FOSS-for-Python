"""UPC-A profile."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.profiles.base import SymbologyProfile


@dataclass(slots=True, frozen=True)
class UpcaProfile(SymbologyProfile):
    """Profile for UPC-A defaults and text behavior."""
