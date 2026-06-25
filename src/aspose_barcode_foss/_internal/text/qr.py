"""QR Code text layout policy."""

from __future__ import annotations

from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


class QrTextLayoutPolicy(TextLayoutPolicy):
    """Provide no-op text layout for QR Code (no human-readable line)."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        """Return an empty layout; QR Code has no human-readable text line."""
        del symbol, options
        return TextLayout()
