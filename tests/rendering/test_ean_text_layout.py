"""Contract tests for EAN/UPC text layout policies."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.encoders.ean8 import Ean8Encoder
from aspose_barcode_foss._internal.encoders.ean13 import Ean13Encoder
from aspose_barcode_foss._internal.encoders.upca import UpcaEncoder
from aspose_barcode_foss._internal.encoders.upce import UpceEncoder
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.parsers.ean8 import Ean8InputParser
from aspose_barcode_foss._internal.parsers.ean13 import Ean13InputParser
from aspose_barcode_foss._internal.parsers.upca import UpcaInputParser
from aspose_barcode_foss._internal.parsers.upce import UpceInputParser
from aspose_barcode_foss._internal.standards.ean import upce_zero_suppress
from aspose_barcode_foss._internal.text.ean8 import Ean8TextLayoutPolicy
from aspose_barcode_foss._internal.text.ean13 import Ean13TextLayoutPolicy
from aspose_barcode_foss._internal.text.upca import UpcaTextLayoutPolicy
from aspose_barcode_foss._internal.text.upce import UpceTextLayoutPolicy


def _build_options(
    *,
    show_text: bool = True,
    quiet_zone: float = 20.0,
    font_size: float = 8.0,
) -> ResolvedRenderOptions:
    return ResolvedRenderOptions(
        scale=1.0,
        dpi=300,
        module_width=2.0,
        module_height=10.0,
        quiet_zone=quiet_zone,
        foreground_color="#111111",
        background_color="#fefefe",
        transparent_background=False,
        show_text=show_text,
        font_family="Fira Sans",
        font_size=font_size,
    )


def _expected_text_y(symbol: EncodedSymbol, options: ResolvedRenderOptions) -> float:
    module_width = options.module_width * options.scale
    assert symbol.matrix.row_heights_x is not None
    return symbol.matrix.row_heights_x[0] * module_width + (0.5 * module_width)


def _assert_text_y_uses_main_bar_height(symbol: EncodedSymbol, options: ResolvedRenderOptions) -> None:
    layout = {
        "ean8": Ean8TextLayoutPolicy(),
        "ean13": Ean13TextLayoutPolicy(),
        "upca": UpcaTextLayoutPolicy(),
        "upce": UpceTextLayoutPolicy(),
    }[symbol.metadata.symbology].create_layout(symbol, options=options)

    assert layout.segments
    assert all(segment.offset_y == pytest.approx(_expected_text_y(symbol, options)) for segment in layout.segments)


def _build_ean8_symbol() -> EncodedSymbol:
    payload = Ean8InputParser().parse("5512345")
    return Ean8Encoder().encode(payload)


def _build_ean13_symbol() -> EncodedSymbol:
    payload = Ean13InputParser().parse("400638133393")
    return Ean13Encoder().encode(payload)


def _build_upca_symbol() -> EncodedSymbol:
    payload = UpcaInputParser().parse("01234567890")
    return UpcaEncoder().encode(payload)


def _build_upce_symbol() -> EncodedSymbol:
    payload = UpceInputParser().parse("01234000005")
    return UpceEncoder().encode(payload)


def test_ean8_text_layout_two_centred_4_digit_groups() -> None:
    symbol = _build_ean8_symbol()
    options = _build_options()

    layout = Ean8TextLayoutPolicy().create_layout(symbol, options=options)

    assert [segment.text for segment in layout.segments] == ["5512", "3457"]
    assert [segment.anchor for segment in layout.segments] == ["middle", "middle"]
    assert layout.segments[0].offset_x > 0.0
    assert layout.segments[1].offset_x > 0.0
    assert layout.segments[0].offset_x == pytest.approx(34.0)
    assert layout.segments[1].offset_x == pytest.approx(100.0)
    assert all(segment.offset_y == pytest.approx(_expected_text_y(symbol, options)) for segment in layout.segments)


def test_ean13_text_layout_segments_outside_digit_and_data_groups() -> None:
    symbol = _build_ean13_symbol()
    options = _build_options(quiet_zone=22.0)

    layout = Ean13TextLayoutPolicy().create_layout(symbol, options=options)

    assert [segment.text for segment in layout.segments] == ["4", "006381", "333931"]
    assert [segment.anchor for segment in layout.segments] == ["middle", "middle", "middle"]
    assert layout.segments[0].offset_x < 0.0
    assert layout.segments[1].offset_x == pytest.approx(48.0)
    assert layout.segments[2].offset_x == pytest.approx(142.0)
    assert all(segment.offset_y == pytest.approx(_expected_text_y(symbol, options)) for segment in layout.segments)


def test_upca_text_layout_segments_outside_digits_and_inner_groups() -> None:
    symbol = _build_upca_symbol()
    options = _build_options(quiet_zone=18.0)
    module_area_width = symbol.matrix.width * options.module_width * options.scale

    layout = UpcaTextLayoutPolicy().create_layout(symbol, options=options)

    assert [segment.text for segment in layout.segments] == ["0", "12345", "67890", "5"]
    assert [segment.anchor for segment in layout.segments] == ["middle", "middle", "middle", "middle"]
    assert layout.segments[0].offset_x < 0.0
    assert layout.segments[3].offset_x > module_area_width
    assert layout.segments[1].offset_x == pytest.approx(55.0)
    assert layout.segments[2].offset_x == pytest.approx(135.0)
    assert layout.segments[3].offset_x == pytest.approx(193.0)
    assert all(segment.offset_y == pytest.approx(_expected_text_y(symbol, options)) for segment in layout.segments)


def test_upca_right_outside_digit_moves_right_for_large_font_size() -> None:
    symbol = _build_upca_symbol()
    small_options = _build_options(quiet_zone=18.0, font_size=8.0)
    large_options = _build_options(quiet_zone=18.0, font_size=20.0)

    small_layout = UpcaTextLayoutPolicy().create_layout(symbol, options=small_options)
    large_layout = UpcaTextLayoutPolicy().create_layout(symbol, options=large_options)

    assert small_layout.segments[3].offset_x == pytest.approx(193.0)
    assert large_layout.segments[3].offset_x == pytest.approx(197.0)
    assert large_layout.segments[3].offset_x > small_layout.segments[3].offset_x


def test_upce_text_layout_segments_number_system_compressed_digits_and_check_digit() -> None:
    symbol = _build_upce_symbol()
    options = _build_options(quiet_zone=18.0)
    module_area_width = symbol.matrix.width * options.module_width * options.scale

    layout = UpceTextLayoutPolicy().create_layout(symbol, options=options)

    assert upce_zero_suppress(symbol.metadata.display_text) == "123454"
    assert [segment.text for segment in layout.segments] == ["0", "123454", "3"]
    assert [segment.anchor for segment in layout.segments] == ["middle", "middle", "middle"]
    assert layout.segments[0].offset_x < 0.0
    assert layout.segments[1].offset_x == pytest.approx(48.0)
    assert layout.segments[2].offset_x > module_area_width
    assert layout.segments[2].offset_x == pytest.approx(105.0)
    assert all(segment.offset_y == pytest.approx(_expected_text_y(symbol, options)) for segment in layout.segments)


def test_upce_right_outside_digit_moves_right_for_large_font_size() -> None:
    symbol = _build_upce_symbol()
    small_options = _build_options(quiet_zone=18.0, font_size=8.0)
    large_options = _build_options(quiet_zone=18.0, font_size=20.0)

    small_layout = UpceTextLayoutPolicy().create_layout(symbol, options=small_options)
    large_layout = UpceTextLayoutPolicy().create_layout(symbol, options=large_options)

    assert small_layout.segments[2].offset_x == pytest.approx(105.0)
    assert large_layout.segments[2].offset_x == pytest.approx(109.0)
    assert large_layout.segments[2].offset_x > small_layout.segments[2].offset_x


@pytest.mark.parametrize(
    ("symbol", "policy"),
    [
        (_build_ean8_symbol(), Ean8TextLayoutPolicy()),
        (_build_ean13_symbol(), Ean13TextLayoutPolicy()),
        (_build_upca_symbol(), UpcaTextLayoutPolicy()),
        (_build_upce_symbol(), UpceTextLayoutPolicy()),
    ],
)
def test_ean_upc_text_layout_returns_empty_layout_when_text_is_disabled(
    symbol: EncodedSymbol,
    policy: Ean8TextLayoutPolicy | Ean13TextLayoutPolicy | UpcaTextLayoutPolicy | UpceTextLayoutPolicy,
) -> None:
    options = _build_options(show_text=False)

    layout = policy.create_layout(symbol, options=options)

    assert layout.segments == ()


@pytest.mark.parametrize(
    "symbol",
    [
        _build_ean8_symbol(),
        _build_ean13_symbol(),
        _build_upca_symbol(),
        _build_upce_symbol(),
    ],
)
def test_ean_upc_text_y_is_based_on_main_bar_height_not_guard_extension(symbol: EncodedSymbol) -> None:
    options = _build_options()

    _assert_text_y_uses_main_bar_height(symbol, options)
