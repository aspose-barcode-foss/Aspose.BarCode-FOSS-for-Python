"""Application service coordinating the barcode pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedFeatureError
from aspose_barcode_foss._internal.models.options import EncodeOptions, RenderOptions
from aspose_barcode_foss._internal.registry import SymbologyRegistry
from aspose_barcode_foss._internal.resolver import OptionsResolver
from aspose_barcode_foss.result import Barcode


def _require_symbology_name(symbology: object) -> str:
    """Validate the public symbology selector before registry lookup."""
    if not isinstance(symbology, str):
        msg = "symbology must be a non-empty string"
        raise InvalidInputError(msg)

    normalized_symbology = symbology.strip()
    if not normalized_symbology:
        msg = "symbology must be a non-empty string"
        raise InvalidInputError(msg)
    return normalized_symbology


def _raise_unsupported_stage(symbology_id: str, stage: str, exc: NotImplementedError) -> None:
    """Translate placeholder parser or encoder stages into a typed API error."""
    message = f"symbology {symbology_id!r} does not implement the {stage} stage"
    raise UnsupportedFeatureError(message) from exc


@dataclass(slots=True)
class BarcodeService:
    """Coordinate encoder selection, option resolution, and result creation."""

    registry: SymbologyRegistry
    options_resolver: OptionsResolver

    def generate(
        self,
        symbology: str,
        data: str | bytes,
        *,
        encode: EncodeOptions | None = None,
        render: RenderOptions | None = None,
    ) -> Barcode:
        """Build a barcode object for the requested symbology."""
        requested_symbology = _require_symbology_name(symbology)
        definition = self.registry.get_definition(requested_symbology)

        normalized_render_options = self.options_resolver.coerce_options(render)
        if normalized_render_options is not None:
            self.options_resolver.resolve(
                definition.profile,
                options=normalized_render_options,
            )

        try:
            payload = definition.parser.parse(data, options=encode)
        except NotImplementedError as exc:
            _raise_unsupported_stage(definition.name, "parse", exc)

        try:
            encoded_symbol = definition.encoder.encode(payload, options=encode)
        except NotImplementedError as exc:
            _raise_unsupported_stage(definition.name, "encode", exc)

        return Barcode(
            symbol=encoded_symbol,
            profile=definition.profile,
            default_render_options=normalized_render_options,
        )
