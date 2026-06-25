"""Base symbology profile model."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.models.capabilities import SymbologyCapabilities, SymbologyStatus
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


@dataclass(slots=True, frozen=True)
class SymbologyProfile:
    """Defaults and policies for a symbology."""

    name: str
    status: SymbologyStatus
    defaults: ResolvedRenderOptions
    capabilities: SymbologyCapabilities
    text_policy: TextLayoutPolicy
    spec_references: tuple[str, ...] = ()
    known_limitations: tuple[str, ...] = ()
