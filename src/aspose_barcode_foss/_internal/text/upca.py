"""UPC-A text layout policy."""

from __future__ import annotations

from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout, TextSegment
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


class UpcaTextLayoutPolicy(TextLayoutPolicy):
    """Provide text layout behavior for UPC-A."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        """Build text layout for UPC-A."""
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

        scaled_qz = options.quiet_zone * options.scale
        d1_offset_x = -(scaled_qz / 2.0)
        left_offset_x = 27.5 * mw
        right_offset_x = 67.5 * mw
        scaled_font_size = options.font_size * options.scale
        d12_offset_x = 95.0 * mw + max(1.5 * mw, 0.35 * scaled_font_size)

        return TextLayout(
            segments=(
                TextSegment(text=display_text[0], anchor="middle", offset_x=d1_offset_x, offset_y=text_y),
                TextSegment(text=display_text[1:6], anchor="middle", offset_x=left_offset_x, offset_y=text_y),
                TextSegment(text=display_text[6:11], anchor="middle", offset_x=right_offset_x, offset_y=text_y),
                TextSegment(text=display_text[11], anchor="middle", offset_x=d12_offset_x, offset_y=text_y),
            )
        )
