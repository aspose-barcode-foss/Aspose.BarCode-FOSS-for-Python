"""Unit tests for PngRenderer.render()."""

from __future__ import annotations

import io

import PIL.Image
import PIL.ImageColor
import pytest

from aspose_barcode_foss._internal.exceptions import RenderingError
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.models.text import TextLayout, TextSegment
from aspose_barcode_foss._internal.renderers._matrix import _iter_dark_runs
from aspose_barcode_foss._internal.renderers.png import PngRenderer


def _build_symbol() -> EncodedSymbol:
    matrix = ModuleMatrix(
        width=6,
        height=2,
        modules=(
            (1, 1, 0, 1, 1, 1),
            (0, 1, 1, 0, 0, 1),
        ),
    )
    metadata = SymbolMetadata(
        symbology="test-symbology",
        normalized_data="ABC123",
        display_text="ABC123",
        input_kind="text",
    )
    return EncodedSymbol(matrix=matrix, metadata=metadata)


def _build_options(**overrides: object) -> ResolvedRenderOptions:
    values: dict[str, object] = {
        "scale": 2.0,
        "dpi": 300,
        "module_width": 1.5,
        "module_height": 4.0,
        "quiet_zone": 2.0,
        "foreground_color": "#111111",
        "background_color": "#fefefe",
        "transparent_background": False,
        "show_text": False,
        "font_family": "Fira Sans",
        "font_size": 6.0,
    }
    values.update(overrides)
    return ResolvedRenderOptions(**values)


def _decode_png(artifact_data: bytes) -> PIL.Image.Image:
    return PIL.Image.open(io.BytesIO(artifact_data))


def test_png_renderer_returns_correct_artifact_fields() -> None:
    artifact = PngRenderer().render(_build_symbol(), layout=TextLayout(), options=_build_options())
    assert artifact.backend == "png"
    assert artifact.media_type == "image/png"
    assert isinstance(artifact.data, bytes)


def test_png_renderer_canvas_pixel_dimensions() -> None:
    # scale=2, module_width=1.5, module_height=4, quiet_zone=2, show_text=False, symbol 6×2
    # px_width = round((6*1.5 + 2*2) * 2) = round(26.0) = 26
    # px_height = round((2*4.0 + 2*2) * 2) = round(24.0) = 24
    artifact = PngRenderer().render(_build_symbol(), layout=TextLayout(), options=_build_options())
    image = _decode_png(artifact.data)
    assert image.width == 26
    assert image.height == 24


def test_png_renderer_background_color_fills_corner_pixel() -> None:
    options = _build_options(transparent_background=False, background_color="#fefefe")
    artifact = PngRenderer().render(_build_symbol(), layout=TextLayout(), options=options)
    image = _decode_png(artifact.data)
    assert image.getpixel((0, 0))[:3] == (254, 254, 254)


def test_png_renderer_foreground_color_on_dark_module() -> None:
    # Matrix row 0 starts with (1, 1, ...) — module (col=0, row=0) is dark.
    # x0 = round(scaled_quiet_zone + 0 * scaled_module_width) = round(4.0) = 4
    # y0 = round(scaled_quiet_zone + 0 * scaled_module_height) = round(4.0) = 4
    artifact = PngRenderer().render(_build_symbol(), layout=TextLayout(), options=_build_options())
    image = _decode_png(artifact.data)
    assert image.getpixel((4, 4))[:3] == (17, 17, 17)


def test_png_renderer_light_module_retains_background_color() -> None:
    # Matrix row 0, column 2 is light (value 0).
    # x = round(4.0 + 2 * 3.0) + 1 = 10 + 1 = 11
    # y = round(4.0 + 0 * 8.0) + 1 = 4 + 1 = 5
    artifact = PngRenderer().render(_build_symbol(), layout=TextLayout(), options=_build_options())
    image = _decode_png(artifact.data)
    assert image.getpixel((11, 5))[:3] == (254, 254, 254)


def test_png_renderer_transparent_background_produces_rgba_with_zero_alpha() -> None:
    options = _build_options(transparent_background=True, background_color=None)
    artifact = PngRenderer().render(_build_symbol(), layout=TextLayout(), options=options)
    image = _decode_png(artifact.data)
    assert image.mode == "RGBA"
    assert image.getpixel((0, 0))[3] == 0


def test_png_renderer_opaque_no_background_color_defaults_to_white() -> None:
    options = _build_options(transparent_background=False, background_color=None)
    artifact = PngRenderer().render(_build_symbol(), layout=TextLayout(), options=options)
    image = _decode_png(artifact.data)
    assert image.mode == "RGB"
    assert image.getpixel((0, 0)) == (255, 255, 255)


def test_png_renderer_with_text_segments_expands_canvas_height() -> None:
    # show_text=True, scale=2.0, quiet_zone=2.0, font_size=6.0
    # segment: offset_y=20.0, offset_x=0.0, anchor="start", text="ABC"
    # scaled_quiet_zone = 2.0 * 2.0 = 4.0
    # canvas_height_no_text = 2 * 4.0 * 2.0 + 2 * 4.0 = 24.0
    # text_bottom = 20.0 + 6.0 * 2.0 = 32.0
    # canvas_height = max(24.0, 4.0 + 32.0) = 36.0 → px_height = 36
    layout = TextLayout(segments=(TextSegment(text="ABC", anchor="start", offset_x=0.0, offset_y=20.0),))
    options = _build_options(show_text=True, scale=2.0, quiet_zone=2.0, font_size=6.0)
    artifact = PngRenderer().render(_build_symbol(), layout=layout, options=options)
    image = _decode_png(artifact.data)
    assert image.height == 36


def test_png_renderer_does_not_render_text_when_show_text_false() -> None:
    layout = TextLayout(segments=(TextSegment(text="ABC", anchor="start", offset_x=0.0, offset_y=20.0),))
    options = _build_options(show_text=False)
    artifact = PngRenderer().render(_build_symbol(), layout=layout, options=options)
    image = _decode_png(artifact.data)
    assert image.height == 24


def test_png_renderer_raises_on_invalid_text_anchor() -> None:
    layout = TextLayout(segments=(TextSegment(text="ABC", anchor="invalid", offset_x=0.0, offset_y=0.0),))
    options = _build_options(show_text=True)
    with pytest.raises(RenderingError):
        PngRenderer().render(_build_symbol(), layout=layout, options=options)


def test_iter_dark_runs_shared_module() -> None:
    result = _iter_dark_runs((1, 1, 0, 1, 1, 1))
    assert result == ((0, 2), (3, 3))


def test_png_renderer_variable_row_heights_canvas_dimensions() -> None:
    matrix = ModuleMatrix(
        width=4,
        height=2,
        modules=((1, 0, 1, 0), (1, 1, 0, 0)),
        row_heights_x=(4.0, 1.0),
    )
    metadata = SymbolMetadata(
        symbology="test-symbology",
        normalized_data="TEST",
        display_text="TEST",
        input_kind="text",
    )
    symbol = EncodedSymbol(matrix=matrix, metadata=metadata)
    options = _build_options(module_width=2.0, scale=1.0, quiet_zone=5.0, module_height=99.0, show_text=False)
    artifact = PngRenderer().render(symbol, layout=TextLayout(), options=options)
    image = _decode_png(artifact.data)
    assert image.width == 18
    assert image.height == 20


def test_png_renderer_variable_row_heights_second_row_y_position() -> None:
    matrix = ModuleMatrix(
        width=4,
        height=2,
        modules=((1, 0, 1, 0), (1, 1, 0, 0)),
        row_heights_x=(4.0, 1.0),
    )
    metadata = SymbolMetadata(
        symbology="test-symbology",
        normalized_data="TEST",
        display_text="TEST",
        input_kind="text",
    )
    symbol = EncodedSymbol(matrix=matrix, metadata=metadata)
    options = _build_options(
        module_width=2.0,
        scale=1.0,
        quiet_zone=5.0,
        module_height=99.0,
        show_text=False,
        foreground_color="#000000",
        background_color="#ffffff",
    )
    artifact = PngRenderer().render(symbol, layout=TextLayout(), options=options)
    image = _decode_png(artifact.data)
    # col 1 in row 0 is light, col 1 in row 1 is dark — use x=7 (quiet_zone=5 + col*2=2)
    # row 1 starts at y=13 (quiet_zone=5 + row0_height=8), so y=13 is dark and y=12 is light
    assert image.getpixel((7, 13))[:3] == (0, 0, 0)
    assert image.getpixel((7, 12))[:3] == (255, 255, 255)
