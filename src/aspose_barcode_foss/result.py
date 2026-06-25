"""Public result object returned by the API."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.exceptions import RenderingError, UnsupportedFeatureError
from aspose_barcode_foss._internal.models.artifacts import RenderedArtifact
from aspose_barcode_foss._internal.models.options import RenderOptions
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.profiles.base import SymbologyProfile
from aspose_barcode_foss._internal.renderers.base import Renderer
from aspose_barcode_foss._internal.renderers.svg import SvgRenderer
from aspose_barcode_foss._internal.renderers.png import PngRenderer
from aspose_barcode_foss._internal.resolver import OptionsResolver


@dataclass(slots=True)
class Barcode:
    """Public barcode object returned by the high-level API."""

    symbol: EncodedSymbol
    profile: SymbologyProfile
    default_render_options: RenderOptions | None = None

    def render(
        self,
        renderer: Renderer,
        *,
        options: RenderOptions | None = None,
    ) -> RenderedArtifact:
        """Render the barcode with the provided renderer."""
        options_resolver = OptionsResolver()
        merged_options = options_resolver.merge_options(
            self.default_render_options,
            options,
        )
        resolved_options = options_resolver.resolve(
            self.profile,
            options=merged_options,
        )

        if resolved_options.show_text:
            try:
                layout = self.profile.text_policy.create_layout(
                    self.symbol,
                    options=resolved_options,
                )
            except NotImplementedError as exc:
                message = f"text layout is not implemented for symbology {self.profile.name!r}"
                raise UnsupportedFeatureError(message) from exc
        else:
            layout = TextLayout()

        return renderer.render(
            self.symbol,
            layout=layout,
            options=resolved_options,
        )

    def to_svg(
        self,
        *,
        options: RenderOptions | None = None,
    ) -> str:
        """Render the barcode as SVG."""
        artifact = self.render(SvgRenderer(), options=options)
        if artifact.backend != "svg" or artifact.media_type != "image/svg+xml" or not isinstance(artifact.data, str):
            msg = "SVG renderer returned an invalid artifact"
            raise RenderingError(msg)
        return artifact.data

    def to_png(
        self,
        *,
        options: RenderOptions | None = None,
    ) -> bytes:
        """Render the barcode as PNG."""
        artifact = self.render(PngRenderer(), options=options)
        if artifact.backend != "png" or artifact.media_type != "image/png" or not isinstance(artifact.data, bytes):
            msg = "PNG renderer returned an invalid artifact"
            raise RenderingError(msg)
        return artifact.data

    def to_pdf(
        self,
        *,
        options: RenderOptions | None = None,
    ) -> bytes:
        """Render the barcode as PDF when the backend is available."""
        raise NotImplementedError
