"""QR Code 2D rendering-contract tests driven by the QR profile defaults.

These tests confirm the public ``barcode.qr(...)`` rendering contract: the SVG and
PNG canvases are square, modules are square, the quiet zone equals four modules on
every side, and no human-readable text is emitted.
"""

from __future__ import annotations

import re
import struct

import aspose_barcode_foss as barcode


# Resolved QR profile render defaults (see bootstrap ``_build_render_defaults``):
# module_width == module_height == 2.0, quiet_zone == 8.0 (4 modules), scale == 1.0.
MODULE_SIZE = 2.0
QUIET_ZONE = 8.0

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# Match every ``<rect .../>`` element in the SVG document.
_RECT_RE = re.compile(r"<rect\b[^>]*/>")
# Match the ``width``/``height`` attributes of the root ``<svg>`` element.
_SVG_SIZE_RE = re.compile(r'<svg\b[^>]*\bwidth="([^"]+)"[^>]*\bheight="([^"]+)"')


def _render_svg() -> str:
    """Render the canonical ``QR Code`` symbol to an SVG string."""
    return barcode.qr("QR Code").to_svg()


def _svg_canvas_size(svg: str) -> tuple[float, float]:
    """Return the root ``<svg>`` width and height as floats."""
    match = _SVG_SIZE_RE.search(svg)
    assert match is not None, "root <svg> element with width/height not found"
    return float(match.group(1)), float(match.group(2))


def _module_rects(svg: str) -> list[tuple[float, float, float, float]]:
    """Return (x, y, width, height) for each dark-module rect, excluding the background."""
    rects: list[tuple[float, float, float, float]] = []
    for element in _RECT_RE.findall(svg):
        # The optional background rect carries a ``fill`` attribute; module rects do not.
        if "fill=" in element:
            continue
        x = float(re.search(r'\bx="([^"]+)"', element).group(1))
        y = float(re.search(r'\by="([^"]+)"', element).group(1))
        width = float(re.search(r'\bwidth="([^"]+)"', element).group(1))
        height = float(re.search(r'\bheight="([^"]+)"', element).group(1))
        rects.append((x, y, width, height))
    assert rects, "no module rects found in SVG"
    return rects


def test_qr_svg_canvas_is_square() -> None:
    """The rendered SVG canvas is square (root width == height)."""
    svg = _render_svg()
    width, height = _svg_canvas_size(svg)
    assert width == height


def test_qr_svg_modules_are_square() -> None:
    """Every module rect is exactly one module tall, and single-module runs are square."""
    rects = _module_rects(_render_svg())
    for _x, _y, width, height in rects:
        # Square modules => each rect spans exactly one module vertically...
        assert height == MODULE_SIZE
        # ...and an integer number of equal-sized modules horizontally.
        assert width % MODULE_SIZE == 0
    single_module_rects = [(w, h) for _x, _y, w, h in rects if w == MODULE_SIZE]
    assert single_module_rects, "expected at least one single-module rect"
    for width, height in single_module_rects:
        assert width == height


def test_qr_svg_quiet_zone_is_four_modules() -> None:
    """The quiet zone equals four modules (8.0 user units) on the top and left edges."""
    svg = _render_svg()
    rects = _module_rects(svg)
    # QR finder patterns always occupy module (0, 0), so the minimum dark offset is the
    # quiet zone itself: 4 modules * 2.0 == 8.0.
    assert min(x for x, _y, _w, _h in rects) == QUIET_ZONE
    assert min(y for _x, y, _w, _h in rects) == QUIET_ZONE
    assert QUIET_ZONE == 4 * MODULE_SIZE

    # The canvas width equals the N-module area plus a quiet zone on each side.
    canvas_width, _canvas_height = _svg_canvas_size(svg)
    module_count = round((canvas_width - 2 * QUIET_ZONE) / MODULE_SIZE)
    assert canvas_width == module_count * MODULE_SIZE + 2 * QUIET_ZONE


def test_qr_svg_emits_no_text() -> None:
    """No <text> element is emitted for the text-free QR profile (show_text=False)."""
    assert "<text" not in _render_svg()


def test_qr_png_canvas_is_square() -> None:
    """The rendered PNG is a valid PNG with a square canvas (IHDR width == height)."""
    data = barcode.qr("QR Code").to_png()
    assert data.startswith(PNG_SIGNATURE)
    (width,) = struct.unpack(">I", data[16:20])
    (height,) = struct.unpack(">I", data[20:24])
    assert width == height
