"""Contract tests for the SVG renderer."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from aspose_barcode_foss._internal.exceptions import RenderingError
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.models.text import TextLayout, TextSegment
from aspose_barcode_foss._internal.renderers.svg import SvgRenderer


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SVG_TAG = f"{{{SVG_NAMESPACE}}}"


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
        "show_text": True,
        "font_family": "Fira Sans",
        "font_size": 6.0,
    }
    values.update(overrides)
    return ResolvedRenderOptions(**values)


def _parse_svg(svg_text: str) -> ET.Element:
    return ET.fromstring(svg_text)


def _rect_geometry(element: ET.Element) -> tuple[float, float, float, float]:
    return (
        float(element.attrib["x"]),
        float(element.attrib["y"]),
        float(element.attrib["width"]),
        float(element.attrib["height"]),
    )


def test_svg_renderer_emits_canvas_geometry_background_and_coalesced_module_rectangles() -> None:
    """The renderer should emit deterministic canvas and row-run geometry."""
    renderer = SvgRenderer()

    artifact = renderer.render(
        _build_symbol(),
        layout=TextLayout(),
        options=_build_options(show_text=False),
    )

    assert artifact.backend == "svg"
    assert artifact.media_type == "image/svg+xml"
    assert isinstance(artifact.data, str)

    root = _parse_svg(artifact.data)
    children = list(root)

    assert root.tag == f"{SVG_TAG}svg"
    assert float(root.attrib["width"]) == pytest.approx(26.0)
    assert float(root.attrib["height"]) == pytest.approx(24.0)
    assert [float(value) for value in root.attrib["viewBox"].split()] == pytest.approx([0.0, 0.0, 26.0, 24.0])
    assert children[0].tag == f"{SVG_TAG}rect"
    assert children[0].attrib["fill"] == "#fefefe"
    assert _rect_geometry(children[0]) == pytest.approx((0.0, 0.0, 26.0, 24.0))

    assert children[1].tag == f"{SVG_TAG}g"
    assert children[1].attrib["fill"] == "#111111"
    assert children[1].attrib["shape-rendering"] == "crispEdges"
    assert [_rect_geometry(rect) for rect in children[1].findall(f"{SVG_TAG}rect")] == pytest.approx(
        [
            (4.0, 4.0, 6.0, 8.0),
            (13.0, 4.0, 9.0, 8.0),
            (7.0, 12.0, 6.0, 8.0),
            (19.0, 12.0, 3.0, 8.0),
        ]
    )


def test_svg_renderer_omits_the_background_rect_for_transparent_output() -> None:
    """Transparent backgrounds should suppress the root-level background rect."""
    renderer = SvgRenderer()

    artifact = renderer.render(
        _build_symbol(),
        layout=TextLayout(),
        options=_build_options(
            background_color=None,
            transparent_background=True,
            show_text=False,
        ),
    )

    root = _parse_svg(artifact.data)

    assert [child.tag for child in list(root)] == [f"{SVG_TAG}g"]


def test_svg_renderer_emits_text_with_supported_anchors_and_hanging_baseline() -> None:
    """Renderer-emitted text should use the documented anchor and y semantics."""
    renderer = SvgRenderer()
    layout = TextLayout(
        segments=(
            TextSegment(text="L", anchor="start", offset_x=0.0, offset_y=18.0),
            TextSegment(text="C", anchor="middle", offset_x=9.0, offset_y=18.0),
            TextSegment(text="R & Co", anchor="end", offset_x=18.0, offset_y=18.0),
        )
    )

    artifact = renderer.render(_build_symbol(), layout=layout, options=_build_options())

    root = _parse_svg(artifact.data)
    text_group = list(root)[2]
    text_elements = text_group.findall(f"{SVG_TAG}text")

    assert float(root.attrib["height"]) == pytest.approx(34.0)
    assert text_group.attrib["fill"] == "#111111"
    assert text_group.attrib["font-family"] == "Fira Sans"
    assert float(text_group.attrib["font-size"]) == pytest.approx(12.0)
    assert [element.text for element in text_elements] == ["L", "C", "R & Co"]
    assert [element.attrib["text-anchor"] for element in text_elements] == [
        "start",
        "middle",
        "end",
    ]
    assert [element.attrib["dominant-baseline"] for element in text_elements] == ["hanging"] * 3
    assert [float(element.attrib["x"]) for element in text_elements] == pytest.approx([4.0, 13.0, 22.0])
    assert [float(element.attrib["y"]) for element in text_elements] == pytest.approx([22.0, 22.0, 22.0])


def test_svg_renderer_suppresses_text_when_show_text_is_disabled() -> None:
    """Text layout should be ignored when the resolved options disable text."""
    renderer = SvgRenderer()
    layout = TextLayout(segments=(TextSegment(text="ABC123", anchor="middle", offset_x=9.0, offset_y=18.0),))

    artifact = renderer.render(
        _build_symbol(),
        layout=layout,
        options=_build_options(show_text=False),
    )

    root = _parse_svg(artifact.data)

    assert root.findall(f".//{SVG_TAG}text") == []


def test_svg_renderer_is_byte_for_byte_deterministic_for_identical_inputs() -> None:
    """Repeated renders of the same logical input should match exactly."""
    renderer = SvgRenderer()
    symbol = _build_symbol()
    layout = TextLayout(segments=(TextSegment(text="ABC123", anchor="middle", offset_x=9.0, offset_y=18.0),))
    options = _build_options()

    first = renderer.render(symbol, layout=layout, options=options)
    second = renderer.render(symbol, layout=layout, options=options)

    assert first == second
    assert first.data == second.data


def test_svg_renderer_rejects_unsupported_text_anchors() -> None:
    """Unsupported text anchors should raise a typed rendering error."""
    renderer = SvgRenderer()
    layout = TextLayout(segments=(TextSegment(text="ABC123", anchor="baseline", offset_x=9.0, offset_y=18.0),))

    with pytest.raises(RenderingError):
        renderer.render(_build_symbol(), layout=layout, options=_build_options())


def test_svg_renderer_variable_row_heights_canvas_and_geometry() -> None:
    matrix = ModuleMatrix(
        width=4,
        height=2,
        modules=(
            (1, 0, 1, 0),
            (1, 1, 0, 0),
        ),
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

    renderer = SvgRenderer()
    artifact = renderer.render(symbol, layout=TextLayout(), options=options)
    root = _parse_svg(artifact.data)

    assert float(root.attrib["width"]) == pytest.approx(18.0)
    assert float(root.attrib["height"]) == pytest.approx(20.0)

    children = list(root)
    g = children[1]
    assert g.tag == f"{SVG_TAG}g"
    rects = g.findall(f"{SVG_TAG}rect")

    row0_rects = [r for r in rects if float(r.attrib["y"]) == pytest.approx(5.0)]
    row1_rects = [r for r in rects if float(r.attrib["y"]) == pytest.approx(13.0)]

    assert len(row0_rects) > 0
    assert len(row1_rects) > 0

    for r in row0_rects:
        assert float(r.attrib["height"]) == pytest.approx(8.0)

    for r in row1_rects:
        assert float(r.attrib["height"]) == pytest.approx(2.0)
        assert float(r.attrib["y"]) == pytest.approx(13.0)


def test_svg_renderer_uniform_height_unchanged_when_row_heights_x_is_none() -> None:
    renderer = SvgRenderer()

    artifact = renderer.render(
        _build_symbol(),
        layout=TextLayout(),
        options=_build_options(show_text=False),
    )

    root = _parse_svg(artifact.data)

    assert float(root.attrib["width"]) == pytest.approx(26.0)
    assert float(root.attrib["height"]) == pytest.approx(24.0)
