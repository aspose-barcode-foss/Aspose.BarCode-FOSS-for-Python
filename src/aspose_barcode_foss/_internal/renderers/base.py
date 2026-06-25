"""Base renderer interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from aspose_barcode_foss._internal.models.artifacts import RenderedArtifact
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout


class Renderer(ABC):
    """Abstract renderer interface."""

    @abstractmethod
    def render(
        self,
        symbol: EncodedSymbol,
        *,
        layout: TextLayout,
        options: ResolvedRenderOptions,
    ) -> RenderedArtifact:
        """Render an encoded symbol into a backend-specific artifact."""
        raise NotImplementedError
