"""PNG renderer."""

from __future__ import annotations

import io

import PIL.Image
import PIL.ImageColor
import PIL.ImageDraw
import PIL.ImageFont

from aspose_barcode_foss._internal.exceptions import RenderingError
from aspose_barcode_foss._internal.models.artifacts import RenderedArtifact
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.renderers._matrix import _iter_dark_runs
from aspose_barcode_foss._internal.renderers.base import Renderer


_ANCHOR_MAP: dict[str, str] = {
    "start": "lt",
    "middle": "mt",
    "end": "rt",
}


class PngRenderer(Renderer):
    """Render a barcode into PNG output.

    Canvas geometry mirrors SvgRenderer: scale all dimensions, add quiet-zone
    padding, optionally expand height for text. The dpi field is embedded as
    PNG metadata only and does not affect pixel dimensions.

    Text rendering uses Pillow's built-in default TrueType font. The font_family
    field of ResolvedRenderOptions is not used in this implementation.
    """

    def render(
        self,
        symbol: EncodedSymbol,
        *,
        layout: TextLayout,
        options: ResolvedRenderOptions,
    ) -> RenderedArtifact:
        """Render an encoded symbol as PNG."""
        scaled_module_width = options.module_width * options.scale
        scaled_module_height = options.module_height * options.scale
        scaled_quiet_zone = options.quiet_zone * options.scale
        scaled_font_size = options.font_size * options.scale

        module_area_width = symbol.matrix.width * scaled_module_width
        if symbol.matrix.row_heights_x:
            module_area_height = sum(h * scaled_module_width for h in symbol.matrix.row_heights_x)
        else:
            module_area_height = symbol.matrix.height * scaled_module_height

        canvas_width = module_area_width + 2 * scaled_quiet_zone
        canvas_height = module_area_height + 2 * scaled_quiet_zone

        if options.show_text and layout.segments:
            text_bottom = max(segment.offset_y + scaled_font_size for segment in layout.segments)
            canvas_height = max(canvas_height, scaled_quiet_zone + text_bottom)

        px_width = round(canvas_width)
        px_height = round(canvas_height)

        # --- background / image mode ---
        if options.transparent_background:
            image = PIL.Image.new("RGBA", (px_width, px_height), (0, 0, 0, 0))
        elif options.background_color is not None:
            bg = PIL.ImageColor.getrgb(options.background_color)
            image = PIL.Image.new("RGB", (px_width, px_height), bg)
        else:
            image = PIL.Image.new("RGB", (px_width, px_height), (255, 255, 255))

        draw = PIL.ImageDraw.Draw(image)
        fg_color = PIL.ImageColor.getrgb(options.foreground_color)

        # --- dark module rectangles ---
        if symbol.matrix.row_heights_x:
            row_pixel_heights = [h * scaled_module_width for h in symbol.matrix.row_heights_x]
            row_y_offsets: list[float] = []
            acc = 0.0
            for h in row_pixel_heights:
                row_y_offsets.append(acc)
                acc += h
        else:
            row_pixel_heights = [scaled_module_height] * symbol.matrix.height
            row_y_offsets = [i * scaled_module_height for i in range(symbol.matrix.height)]

        for row_index, row in enumerate(symbol.matrix.modules):
            for start, length in _iter_dark_runs(row):
                x0 = round(scaled_quiet_zone + start * scaled_module_width)
                x1 = round(scaled_quiet_zone + (start + length) * scaled_module_width)
                y0 = round(scaled_quiet_zone + row_y_offsets[row_index])
                y1 = round(scaled_quiet_zone + row_y_offsets[row_index] + row_pixel_heights[row_index])
                draw.rectangle([(x0, y0), (x1 - 1, y1 - 1)], fill=fg_color)

        # --- text segments ---
        if options.show_text and layout.segments:
            font = PIL.ImageFont.load_default(size=round(scaled_font_size))
            for segment in layout.segments:
                if segment.anchor not in _ANCHOR_MAP:
                    message = f"unsupported text anchor: {segment.anchor!r}"
                    raise RenderingError(message)
                x = round(scaled_quiet_zone + segment.offset_x)
                y = round(scaled_quiet_zone + segment.offset_y)
                draw.text(
                    (x, y),
                    segment.text,
                    fill=fg_color,
                    font=font,
                    anchor=_ANCHOR_MAP[segment.anchor],
                )

        buf = io.BytesIO()
        save_kwargs: dict[str, object] = {}
        if options.dpi is not None:
            save_kwargs["dpi"] = (options.dpi, options.dpi)
        image.save(buf, "PNG", **save_kwargs)

        return RenderedArtifact(
            data=buf.getvalue(),
            media_type="image/png",
            backend="png",
        )
