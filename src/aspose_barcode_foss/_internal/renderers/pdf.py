"""PDF renderer."""

from __future__ import annotations

from aspose_barcode_foss._internal.models.artifacts import RenderedArtifact
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.renderers.base import Renderer


class PdfRenderer(Renderer):
    """Render a barcode into PDF or another vector-friendly artifact."""

    def render(
        self,
        symbol: EncodedSymbol,
        *,
        layout: TextLayout,
        options: ResolvedRenderOptions,
    ) -> RenderedArtifact:
        """Render an encoded symbol as PDF."""
        raise NotImplementedError
