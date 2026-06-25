"""Code 128 text layout policy."""

from __future__ import annotations

from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout, TextSegment
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


class Code128TextLayoutPolicy(TextLayoutPolicy):
    """Provide text layout behavior for Code 128."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        """Build text layout for Code 128."""
        display_text = symbol.metadata.display_text
        if not display_text:
            return TextLayout()

        module_area_width = symbol.matrix.width * options.module_width * options.scale
        module_area_height = symbol.matrix.height * options.module_height * options.scale
        text_top = module_area_height + (2.0 * options.scale)

        return TextLayout(
            segments=(
                TextSegment(
                    text=display_text,
                    anchor="middle",
                    offset_x=module_area_width / 2.0,
                    offset_y=text_top,
                ),
            )
        )
