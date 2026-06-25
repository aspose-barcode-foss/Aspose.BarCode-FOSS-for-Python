"""EAN-8 text layout policy."""

from __future__ import annotations

from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout, TextSegment
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


class Ean8TextLayoutPolicy(TextLayoutPolicy):
    """Provide text layout behavior for EAN-8."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        """Build text layout for EAN-8."""
        display_text = symbol.metadata.display_text
        if not options.show_text or not display_text:
            return TextLayout()

        mw = options.module_width * options.scale

        if symbol.matrix.row_heights_x:
            main_bar_h = symbol.matrix.row_heights_x[0] * mw
        else:
            main_bar_h = symbol.matrix.height * options.module_height * options.scale

        gap = 0.5 * mw
        text_y = main_bar_h + gap

        left_offset_x = (3 + 14) * mw
        right_offset_x = (36 + 14) * mw

        return TextLayout(
            segments=(
                TextSegment(text=display_text[0:4], anchor="middle", offset_x=left_offset_x, offset_y=text_y),
                TextSegment(text=display_text[4:8], anchor="middle", offset_x=right_offset_x, offset_y=text_y),
            )
        )
