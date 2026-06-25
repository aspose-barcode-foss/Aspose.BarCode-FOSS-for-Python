"""Contract tests for the Code 39 text layout policy."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.code39 import Code39Encoder
from aspose_barcode_foss._internal.models.options import Code39Options, ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.parsers.code39 import Code39InputParser
from aspose_barcode_foss._internal.text.code39 import Code39TextLayoutPolicy


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
            symbology="code39",
            normalized_data=display_text,
            display_text=display_text,
            input_kind="text",
        ),
    )


def test_code39_text_layout_centers_display_text_below_the_module_area() -> None:
    """Code 39 text should be centered below the module area in scaled units."""
    symbol = _build_symbol(display_text="CODE 39")
    options = _build_options()

    layout = Code39TextLayoutPolicy().create_layout(symbol, options=options)

    assert len(layout.segments) == 1
    segment = layout.segments[0]
    assert segment.text == "CODE 39"
    assert segment.anchor == "middle"
    assert segment.offset_x == pytest.approx(9.0)
    assert segment.offset_y == pytest.approx(18.0)


def test_code39_text_layout_passes_control_char_mnemonic_through_unchanged() -> None:
    """The policy centers whatever display_text it receives, including mnemonics."""
    symbol = _build_symbol(display_text="<HT>")

    layout = Code39TextLayoutPolicy().create_layout(symbol, options=_build_options())

    assert len(layout.segments) == 1
    assert layout.segments[0].text == "<HT>"


def test_code39_text_layout_returns_empty_layout_for_empty_display_text() -> None:
    """Empty display text should suppress all text segments."""
    symbol = _build_symbol(display_text="")

    layout = Code39TextLayoutPolicy().create_layout(symbol, options=_build_options())

    assert layout.segments == ()


def test_code39_text_layout_excludes_start_stop_and_check_char_from_text() -> None:
    """A check-digit request must not leak '*' or the check char into the text."""
    payload = Code39InputParser(default_full_ascii=False, symbology_name="code39").parse(
        "CODE 39",
        options=Code39Options(add_check_digit=True),
    )
    symbol = Code39Encoder().encode(payload)

    layout = Code39TextLayoutPolicy().create_layout(symbol, options=_build_options())

    assert layout.segments[0].text == "CODE 39"
    assert "*" not in layout.segments[0].text
    assert "R" not in layout.segments[0].text
