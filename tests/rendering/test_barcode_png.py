"""Integration tests for Barcode.to_png() and Barcode.render(PngRenderer()) orchestration."""

from __future__ import annotations

import io

import PIL.Image
import pytest

import aspose_barcode_foss as barcode
from aspose_barcode_foss._internal.exceptions import RenderingError
from aspose_barcode_foss._internal.models.artifacts import RenderedArtifact
from aspose_barcode_foss._internal.models.options import RenderOptions
from aspose_barcode_foss._internal.renderers.png import PngRenderer
from aspose_barcode_foss.result import Barcode


def test_barcode_to_png_returns_bytes() -> None:
    """to_png() should return a bytes object."""
    b = barcode.code128("ABC123")
    result = b.to_png(options=RenderOptions(show_text=False))
    assert isinstance(result, bytes)


def test_barcode_to_png_produces_valid_png_bytes() -> None:
    """to_png() should produce well-formed PNG data readable by Pillow."""
    b = barcode.code128("ABC123")
    png_bytes = b.to_png(options=RenderOptions(show_text=False))
    PIL.Image.open(io.BytesIO(png_bytes))  # must not raise
    assert png_bytes[:4] == b"\x89PNG"


def test_barcode_render_png_renderer_returns_correct_artifact() -> None:
    """render(PngRenderer()) should return an artifact with png backend and image/png media type."""
    b = barcode.code128("ABC123")
    artifact = b.render(PngRenderer(), options=RenderOptions(show_text=False))
    assert artifact.backend == "png"
    assert artifact.media_type == "image/png"
    assert isinstance(artifact.data, bytes)


@pytest.mark.parametrize(
    "artifact",
    [
        RenderedArtifact(data=b"PNG", media_type="image/png", backend="wrong"),
        RenderedArtifact(data=b"PNG", media_type="image/jpeg", backend="png"),
        RenderedArtifact(data="not-bytes", media_type="image/png", backend="png"),
    ],
)
def test_barcode_to_png_rejects_internal_render_contract_mismatches(
    monkeypatch: pytest.MonkeyPatch,
    artifact: RenderedArtifact,
) -> None:
    """Internal render-path contract mismatches should raise RenderingError."""
    b = barcode.code128("ABC123")

    def fake_render(self: Barcode, renderer: object, *, options: object = None) -> RenderedArtifact:
        return artifact

    monkeypatch.setattr(Barcode, "render", fake_render)

    with pytest.raises(RenderingError):
        b.to_png()


def test_barcode_to_png_respects_render_options_scale() -> None:
    """Larger scale values should produce a proportionally larger PNG image."""
    b = barcode.code128("ABC123")
    small = PIL.Image.open(io.BytesIO(b.to_png(options=RenderOptions(scale=1.0, show_text=False))))
    large = PIL.Image.open(io.BytesIO(b.to_png(options=RenderOptions(scale=3.0, show_text=False))))
    assert large.width > small.width
    assert large.height > small.height


def test_barcode_to_png_with_show_text_false_does_not_raise() -> None:
    """to_png() with show_text=False should complete without error and return bytes."""
    b = barcode.code128("ABC123")
    result = b.to_png(options=RenderOptions(show_text=False))
    assert isinstance(result, bytes)
