"""Contract tests for Barcode SVG orchestration."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import pytest

from aspose_barcode_foss._internal.exceptions import RenderingError, UnsupportedFeatureError
from aspose_barcode_foss._internal.models.artifacts import RenderedArtifact
from aspose_barcode_foss._internal.models.capabilities import SymbologyCapabilities
from aspose_barcode_foss._internal.models.options import (
    RenderOptions,
    ResolvedRenderOptions,
)
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.models.text import TextLayout, TextSegment
from aspose_barcode_foss._internal.profiles.base import SymbologyProfile
from aspose_barcode_foss._internal.renderers.base import Renderer
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy
from aspose_barcode_foss.result import Barcode


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SVG_TAG = f"{{{SVG_NAMESPACE}}}"


def _build_defaults(**overrides: object) -> ResolvedRenderOptions:
    values: dict[str, object] = {
        "scale": 1.0,
        "dpi": 300,
        "module_width": 2.0,
        "module_height": 10.0,
        "quiet_zone": 4.0,
        "foreground_color": "#111111",
        "background_color": "#fefefe",
        "transparent_background": False,
        "show_text": True,
        "font_family": "Fira Sans",
        "font_size": 8.0,
    }
    values.update(overrides)
    return ResolvedRenderOptions(**values)


def _build_symbol() -> EncodedSymbol:
    matrix = ModuleMatrix(
        width=4,
        height=2,
        modules=(
            (1, 0, 1, 1),
            (0, 1, 1, 0),
        ),
    )
    metadata = SymbolMetadata(
        symbology="test-symbology",
        normalized_data="ABC123",
        display_text="ABC123",
        input_kind="text",
    )
    return EncodedSymbol(matrix=matrix, metadata=metadata)


def _build_barcode(
    text_policy: TextLayoutPolicy,
    *,
    defaults: ResolvedRenderOptions | None = None,
    default_render_options: RenderOptions | None = None,
) -> Barcode:
    profile = SymbologyProfile(
        name="test-symbology",
        status="stable",
        defaults=defaults or _build_defaults(),
        capabilities=SymbologyCapabilities(
            gs1_support="unsupported",
            eci_support="unsupported",
            structured_append_support="unsupported",
            binary_input_support="partial",
            rendering_outputs=("svg",),
        ),
        text_policy=text_policy,
    )
    return Barcode(
        symbol=_build_symbol(),
        profile=profile,
        default_render_options=default_render_options,
    )


@dataclass
class RecordingTextPolicy(TextLayoutPolicy):
    """Text policy double that records the resolved options it receives."""

    layout: TextLayout
    calls: list[tuple[EncodedSymbol, ResolvedRenderOptions]] = field(default_factory=list)

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        self.calls.append((symbol, options))
        return self.layout


class FailIfCalledTextPolicy(TextLayoutPolicy):
    """Text policy double for proving the no-text path stays untouched."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        raise AssertionError("text policy should not be called")


class NotImplementedTextPolicy(TextLayoutPolicy):
    """Text policy double for unsupported-feature wrapping tests."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        raise NotImplementedError("not implemented yet")


@dataclass
class RecordingRenderer(Renderer):
    """Renderer double that records the layout and resolved options it receives."""

    artifact: RenderedArtifact
    calls: list[tuple[EncodedSymbol, TextLayout, ResolvedRenderOptions]] = field(default_factory=list)

    def render(
        self,
        symbol: EncodedSymbol,
        *,
        layout: TextLayout,
        options: ResolvedRenderOptions,
    ) -> RenderedArtifact:
        self.calls.append((symbol, layout, options))
        return self.artifact


class FailIfCalledRenderer(Renderer):
    """Renderer double for paths that should stop before backend execution."""

    def render(
        self,
        symbol: EncodedSymbol,
        *,
        layout: TextLayout,
        options: ResolvedRenderOptions,
    ) -> RenderedArtifact:
        raise AssertionError("renderer should not be called")


def test_barcode_render_resolves_options_before_invoking_policy_and_renderer() -> None:
    """Resolved options should be passed consistently to text policy and renderer."""
    layout = TextLayout(segments=(TextSegment(text="ABC123", anchor="middle", offset_x=4.0, offset_y=18.0),))
    text_policy = RecordingTextPolicy(layout=layout)
    renderer = RecordingRenderer(
        artifact=RenderedArtifact(
            data="rendered-payload",
            media_type="application/test",
            backend="recording",
        )
    )
    barcode = _build_barcode(text_policy)

    artifact = barcode.render(
        renderer,
        options=RenderOptions(
            scale=2.5,
            foreground_color="#222222",
            transparent_background=True,
            font_size=10.0,
        ),
    )

    expected_options = ResolvedRenderOptions(
        scale=2.5,
        dpi=300,
        module_width=2.0,
        module_height=10.0,
        quiet_zone=4.0,
        foreground_color="#222222",
        background_color=None,
        transparent_background=True,
        show_text=True,
        font_family="Fira Sans",
        font_size=10.0,
    )

    assert artifact == renderer.artifact
    assert text_policy.calls == [(barcode.symbol, expected_options)]
    assert renderer.calls == [(barcode.symbol, layout, expected_options)]


def test_barcode_render_applies_stored_default_render_options() -> None:
    """Stored generation-time defaults should affect later render calls."""
    layout = TextLayout(segments=(TextSegment(text="ABC123", anchor="middle", offset_x=4.0, offset_y=18.0),))
    text_policy = RecordingTextPolicy(layout=layout)
    renderer = RecordingRenderer(
        artifact=RenderedArtifact(
            data="rendered-payload",
            media_type="application/test",
            backend="recording",
        )
    )
    barcode = _build_barcode(
        text_policy,
        default_render_options=RenderOptions(
            scale=2.5,
            foreground_color=" #222222 ",
            transparent_background=True,
            font_size=10.0,
        ),
    )

    artifact = barcode.render(renderer)

    expected_options = ResolvedRenderOptions(
        scale=2.5,
        dpi=300,
        module_width=2.0,
        module_height=10.0,
        quiet_zone=4.0,
        foreground_color="#222222",
        background_color=None,
        transparent_background=True,
        show_text=True,
        font_family="Fira Sans",
        font_size=10.0,
    )

    assert artifact == renderer.artifact
    assert text_policy.calls == [(barcode.symbol, expected_options)]
    assert renderer.calls == [(barcode.symbol, layout, expected_options)]


def test_barcode_render_lets_call_time_options_override_stored_defaults() -> None:
    """Per-call options should win over stored defaults field by field."""
    layout = TextLayout(segments=(TextSegment(text="ABC123", anchor="middle", offset_x=4.0, offset_y=18.0),))
    text_policy = RecordingTextPolicy(layout=layout)
    renderer = RecordingRenderer(
        artifact=RenderedArtifact(
            data="rendered-payload",
            media_type="application/test",
            backend="recording",
        )
    )
    barcode = _build_barcode(
        text_policy,
        default_render_options=RenderOptions(
            scale=2.5,
            foreground_color="#222222",
            show_text=False,
            font_family="IBM Plex Sans",
        ),
    )

    artifact = barcode.render(
        renderer,
        options=RenderOptions(
            scale=3.0,
            show_text=True,
            font_family=" Fira Mono ",
            font_size=10.0,
        ),
    )

    expected_options = ResolvedRenderOptions(
        scale=3.0,
        dpi=300,
        module_width=2.0,
        module_height=10.0,
        quiet_zone=4.0,
        foreground_color="#222222",
        background_color="#fefefe",
        transparent_background=False,
        show_text=True,
        font_family="Fira Mono",
        font_size=10.0,
    )

    assert artifact == renderer.artifact
    assert text_policy.calls == [(barcode.symbol, expected_options)]
    assert renderer.calls == [(barcode.symbol, layout, expected_options)]


def test_barcode_render_bypasses_the_text_policy_when_text_is_disabled() -> None:
    """show_text=False should hand an empty layout directly to the renderer."""
    renderer = RecordingRenderer(
        artifact=RenderedArtifact(
            data="rendered-payload",
            media_type="application/test",
            backend="recording",
        )
    )
    barcode = _build_barcode(FailIfCalledTextPolicy())

    artifact = barcode.render(renderer, options=RenderOptions(show_text=False))

    assert artifact == renderer.artifact
    assert renderer.calls[0][0] == barcode.symbol
    assert renderer.calls[0][1] == TextLayout()
    assert renderer.calls[0][2].show_text is False


def test_barcode_to_svg_uses_stored_default_render_options() -> None:
    """Stored defaults should flow through to_svg via Barcode.render()."""
    barcode = _build_barcode(
        FailIfCalledTextPolicy(),
        default_render_options=RenderOptions(
            show_text=False,
            scale=2.0,
            quiet_zone=1.5,
            foreground_color="#222222",
        ),
    )

    svg_text = barcode.to_svg()

    root = ET.fromstring(svg_text)

    assert isinstance(svg_text, str)
    assert root.tag == f"{SVG_TAG}svg"
    assert float(root.attrib["width"]) == pytest.approx(22.0)
    assert root.findall(f".//{SVG_TAG}text") == []


def test_barcode_to_svg_accepts_typed_overrides_and_returns_a_string() -> None:
    """to_svg should accept RenderOptions overrides without requiring text layout."""
    barcode = _build_barcode(FailIfCalledTextPolicy())

    svg_text = barcode.to_svg(
        options=RenderOptions(
            show_text=False,
            scale=2.0,
            quiet_zone=1.5,
            foreground_color="#222222",
        )
    )

    root = ET.fromstring(svg_text)

    assert isinstance(svg_text, str)
    assert root.tag == f"{SVG_TAG}svg"
    assert float(root.attrib["width"]) == pytest.approx(22.0)
    assert root.findall(f".//{SVG_TAG}text") == []


def test_barcode_render_wraps_unimplemented_text_policies_when_text_is_requested() -> None:
    """NotImplemented text policies should surface as UnsupportedFeatureError."""
    barcode = _build_barcode(NotImplementedTextPolicy())

    with pytest.raises(UnsupportedFeatureError, match="test-symbology"):
        barcode.render(FailIfCalledRenderer())


@pytest.mark.parametrize(
    "artifact",
    [
        RenderedArtifact(data="<svg/>", media_type="image/svg+xml", backend="png"),
        RenderedArtifact(data="<svg/>", media_type="application/xml", backend="svg"),
        RenderedArtifact(data=b"<svg/>", media_type="image/svg+xml", backend="svg"),
    ],
)
def test_barcode_to_svg_rejects_internal_render_contract_mismatches(
    monkeypatch: pytest.MonkeyPatch,
    artifact: RenderedArtifact,
) -> None:
    """Internal render-path contract mismatches should raise RenderingError."""
    barcode = _build_barcode(FailIfCalledTextPolicy())

    def fake_render(self: Barcode, renderer: object, *, options: object = None) -> RenderedArtifact:
        return artifact

    monkeypatch.setattr(Barcode, "render", fake_render)

    with pytest.raises(RenderingError):
        barcode.to_svg()
