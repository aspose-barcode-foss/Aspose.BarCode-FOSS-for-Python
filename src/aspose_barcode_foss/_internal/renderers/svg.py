"""SVG renderer."""

from __future__ import annotations

from decimal import Decimal
from xml.sax.saxutils import escape

from aspose_barcode_foss._internal.exceptions import RenderingError
from aspose_barcode_foss._internal.models.artifacts import RenderedArtifact
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.renderers.base import Renderer
from aspose_barcode_foss._internal.renderers._matrix import _iter_dark_runs


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SUPPORTED_TEXT_ANCHORS = frozenset({"start", "middle", "end"})


def _format_number(value: float) -> str:
    """Return a deterministic SVG-safe string for a numeric value."""
    if value == 0:
        return "0"

    formatted = format(value, ".15g")
    if "e" in formatted or "E" in formatted:
        formatted = format(Decimal(str(value)), "f")

    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")

    return formatted


def _escape_text(value: str) -> str:
    """Escape text content for XML output."""
    return escape(value)


def _escape_attribute(value: str) -> str:
    """Escape an XML attribute value."""
    return escape(value, {'"': "&quot;", "'": "&apos;"})


class SvgRenderer(Renderer):
    """Render a barcode into SVG output."""

    def render(
        self,
        symbol: EncodedSymbol,
        *,
        layout: TextLayout,
        options: ResolvedRenderOptions,
    ) -> RenderedArtifact:
        """Render an encoded symbol as SVG."""
        scaled_module_width = options.module_width * options.scale
        scaled_module_height = options.module_height * options.scale
        scaled_quiet_zone = options.quiet_zone * options.scale
        scaled_font_size = options.font_size * options.scale

        module_area_width = symbol.matrix.width * scaled_module_width
        if symbol.matrix.row_heights_x:
            module_area_height = sum(h * scaled_module_width for h in symbol.matrix.row_heights_x)
        else:
            module_area_height = symbol.matrix.height * scaled_module_height

        svg_width = module_area_width + (2 * scaled_quiet_zone)
        svg_height = module_area_height + (2 * scaled_quiet_zone)

        if options.show_text and layout.segments:
            text_bottom = max(segment.offset_y + scaled_font_size for segment in layout.segments)
            svg_height = max(svg_height, scaled_quiet_zone + text_bottom)

        parts = [
            (
                f'<svg xmlns="{SVG_NAMESPACE}" width="{_format_number(svg_width)}" '
                f'height="{_format_number(svg_height)}" viewBox="0 0 '
                f'{_format_number(svg_width)} {_format_number(svg_height)}">'
            )
        ]

        if not options.transparent_background and options.background_color is not None:
            parts.append(
                f'<rect x="0" y="0" width="{_format_number(svg_width)}" '
                f'height="{_format_number(svg_height)}" '
                f'fill="{_escape_attribute(options.background_color)}"/>'
            )

        parts.append(f'<g fill="{_escape_attribute(options.foreground_color)}" shape-rendering="crispEdges">')
        parts.extend(
            self._render_module_rectangles(
                symbol=symbol,
                scaled_module_width=scaled_module_width,
                scaled_module_height=scaled_module_height,
                scaled_quiet_zone=scaled_quiet_zone,
            )
        )
        parts.append("</g>")

        if options.show_text and layout.segments:
            parts.append(
                f'<g fill="{_escape_attribute(options.foreground_color)}" '
                f'font-family="{_escape_attribute(options.font_family)}" '
                f'font-size="{_format_number(scaled_font_size)}">'
            )
            parts.extend(
                self._render_text_segments(
                    layout=layout,
                    scaled_quiet_zone=scaled_quiet_zone,
                )
            )
            parts.append("</g>")

        parts.append("</svg>")

        return RenderedArtifact(
            data="".join(parts),
            media_type="image/svg+xml",
            backend="svg",
        )

    def _render_module_rectangles(
        self,
        *,
        symbol: EncodedSymbol,
        scaled_module_width: float,
        scaled_module_height: float,
        scaled_quiet_zone: float,
    ) -> tuple[str, ...]:
        """Serialize matrix dark runs as SVG rectangles."""
        rectangles: list[str] = []

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
            y = scaled_quiet_zone + row_y_offsets[row_index]
            row_h = row_pixel_heights[row_index]
            for start, length in _iter_dark_runs(row):
                x = scaled_quiet_zone + (start * scaled_module_width)
                width = length * scaled_module_width
                rectangles.append(
                    f'<rect x="{_format_number(x)}" '
                    f'y="{_format_number(y)}" '
                    f'width="{_format_number(width)}" '
                    f'height="{_format_number(row_h)}"/>'
                )

        return tuple(rectangles)

    def _render_text_segments(
        self,
        *,
        layout: TextLayout,
        scaled_quiet_zone: float,
    ) -> tuple[str, ...]:
        """Serialize text layout segments as SVG text nodes."""
        text_elements: list[str] = []

        for segment in layout.segments:
            if segment.anchor not in SUPPORTED_TEXT_ANCHORS:
                message = f"unsupported text anchor: {segment.anchor!r}"
                raise RenderingError(message)

            x = scaled_quiet_zone + segment.offset_x
            y = scaled_quiet_zone + segment.offset_y
            text_elements.append(
                f'<text x="{_format_number(x)}" y="{_format_number(y)}" '
                f'text-anchor="{segment.anchor}" '
                'dominant-baseline="hanging">'
                f"{_escape_text(segment.text)}</text>"
            )

        return tuple(text_elements)
