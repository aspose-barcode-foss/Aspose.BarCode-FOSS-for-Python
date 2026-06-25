"""UPC-E text layout policy."""

from __future__ import annotations

from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout, TextSegment
from aspose_barcode_foss._internal.standards.ean import upce_zero_suppress
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


class UpceTextLayoutPolicy(TextLayoutPolicy):
    """Provide text layout behavior for UPC-E."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        """Build text layout for UPC-E."""
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
        ns_offset_x = -(scaled_qz / 2.0)
        data_offset_x = 24.0 * mw
        scaled_font_size = options.font_size * options.scale
        check_offset_x = 51.0 * mw + max(1.5 * mw, 0.35 * scaled_font_size)

        six_digits = upce_zero_suppress(display_text) or display_text[1:7]

        return TextLayout(
            segments=(
                TextSegment(text=display_text[0], anchor="middle", offset_x=ns_offset_x, offset_y=text_y),
                TextSegment(text=six_digits, anchor="middle", offset_x=data_offset_x, offset_y=text_y),
                TextSegment(text=display_text[-1], anchor="middle", offset_x=check_offset_x, offset_y=text_y),
            )
        )
