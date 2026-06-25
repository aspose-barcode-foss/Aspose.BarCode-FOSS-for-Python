"""Contract tests for the Code 128 text layout policy."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.text.code128 import Code128TextLayoutPolicy


def _build_options() -> ResolvedRenderOptions:
    return ResolvedRenderOptions(
        scale=1.5,
        dpi=300,
        module_width=2.0,
        module_height=10.0,
        quiet_zone=20.0,
        foreground_color="#111111",
        background_color="#fefefe",
        transparent_background=False,
        show_text=True,
        font_family="Fira Sans",
        font_size=8.0,
    )


def _build_symbol(*, display_text: str) -> EncodedSymbol:
    return EncodedSymbol(
        matrix=ModuleMatrix(
            width=6,
            height=1,
            modules=((1, 0, 1, 1, 0, 1),),
        ),
        metadata=SymbolMetadata(
            symbology="code128",
            normalized_data=display_text,
            display_text=display_text,
            input_kind="text",
        ),
    )


def test_code128_text_layout_centers_display_text_below_the_module_area() -> None:
    """Code 128 text should be centered below the module area in scaled units."""
    symbol = _build_symbol(display_text="ABC123")
    options = _build_options()

    layout = Code128TextLayoutPolicy().create_layout(symbol, options=options)

    assert len(layout.segments) == 1
    segment = layout.segments[0]
    assert segment.text == "ABC123"
    assert segment.anchor == "middle"
    assert segment.offset_x == pytest.approx(9.0)
    assert segment.offset_y == pytest.approx(18.0)


def test_code128_text_layout_returns_empty_layout_for_empty_display_text() -> None:
    """Empty display text should suppress all text segments."""
    symbol = _build_symbol(display_text="")

    layout = Code128TextLayoutPolicy().create_layout(symbol, options=_build_options())

    assert layout.segments == ()
