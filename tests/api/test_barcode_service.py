"""Contract tests for service-level parse and encode orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from aspose_barcode_foss._internal.bootstrap import build_default_service
from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import (
    InvalidInputError,
    UnsupportedCapabilityError,
    UnsupportedFeatureError,
)
from aspose_barcode_foss._internal.models.capabilities import SymbologyCapabilities
from aspose_barcode_foss._internal.models.options import (
    EncodeOptions,
    RenderOptions,
    ResolvedRenderOptions,
)
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.profiles.base import SymbologyProfile
from aspose_barcode_foss._internal.registry import SymbologyDefinition, SymbologyRegistry
from aspose_barcode_foss._internal.resolver import OptionsResolver
from aspose_barcode_foss._internal.service import BarcodeService
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy
from aspose_barcode_foss.result import Barcode


class NoOpTextPolicy(TextLayoutPolicy):
    """Minimal text-policy double for constructing test profiles."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        return TextLayout()


@dataclass
class RecordingParser(InputParser):
    """Parser double that records inputs and can raise a configured failure."""

    payload: NormalizedPayload
    events: list[str]
    failure: Exception | None = None
    calls: list[tuple[str | bytes, EncodeOptions | None]] = field(default_factory=list)

    def parse(
        self,
        data: str | bytes,
        *,
        options: EncodeOptions | None = None,
    ) -> NormalizedPayload:
        self.events.append("parse")
        self.calls.append((data, options))
        if self.failure is not None:
            raise self.failure
        return self.payload


@dataclass
class RecordingEncoder(SymbologyEncoder):
    """Encoder double that records inputs and can raise a configured failure."""

    symbol: EncodedSymbol
    events: list[str]
    failure: Exception | None = None
    calls: list[tuple[NormalizedPayload, EncodeOptions | None]] = field(default_factory=list)

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: EncodeOptions | None = None,
    ) -> EncodedSymbol:
        self.events.append("encode")
        self.calls.append((payload, options))
        if self.failure is not None:
            raise self.failure
        return self.symbol


def _build_defaults() -> ResolvedRenderOptions:
    return ResolvedRenderOptions(
        scale=1.0,
        dpi=300,
        module_width=2.0,
        module_height=10.0,
        quiet_zone=4.0,
        foreground_color="#111111",
        background_color="#fefefe",
        transparent_background=False,
        show_text=True,
        font_family="Fira Sans",
        font_size=8.0,
    )


def _build_profile(name: str = "code128") -> SymbologyProfile:
    return SymbologyProfile(
        name=name,
        status="stable",
        defaults=_build_defaults(),
        capabilities=SymbologyCapabilities(
            gs1_support="unsupported",
            eci_support="unsupported",
            structured_append_support="unsupported",
            binary_input_support="partial",
            rendering_outputs=("svg",),
        ),
        text_policy=NoOpTextPolicy(),
    )


def _build_payload(symbology: str = "code128") -> NormalizedPayload:
    return NormalizedPayload(
        symbology=symbology,
        data="ABC123",
        input_kind="text",
    )


def _build_symbol(symbology: str = "code128") -> EncodedSymbol:
    return EncodedSymbol(
        matrix=ModuleMatrix(
            width=4,
            height=1,
            modules=((1, 0, 1, 1),),
        ),
        metadata=SymbolMetadata(
            symbology=symbology,
            normalized_data="ABC123",
            display_text="ABC123",
            input_kind="text",
        ),
    )


def _build_service(
    *,
    name: str = "code128",
    aliases: tuple[str, ...] = ("code-128",),
    parser: RecordingParser | None = None,
    encoder: RecordingEncoder | None = None,
) -> tuple[BarcodeService, RecordingParser, RecordingEncoder, SymbologyProfile, list[str]]:
    events = parser.events if parser is not None else None
    if events is None and encoder is not None:
        events = encoder.events
    if events is None:
        events = []

    if parser is None:
        parser = RecordingParser(payload=_build_payload(name), events=events)
    if encoder is None:
        encoder = RecordingEncoder(symbol=_build_symbol(name), events=events)
    profile = _build_profile(name)

    registry = SymbologyRegistry()
    registry.register(
        SymbologyDefinition(
            name=name,
            aliases=aliases,
            parser=parser,
            encoder=encoder,
            profile=profile,
        )
    )

    return (
        BarcodeService(registry=registry, options_resolver=OptionsResolver()),
        parser,
        encoder,
        profile,
        events,
    )


@pytest.mark.parametrize("symbology", ["", " ", 123, None])
def test_barcode_service_rejects_blank_and_non_string_symbologies(
    symbology: object,
) -> None:
    """Invalid public symbology selectors should fail before registry lookup."""
    service = BarcodeService(
        registry=SymbologyRegistry(),
        options_resolver=OptionsResolver(),
    )

    with pytest.raises(InvalidInputError, match="symbology"):
        service.generate(symbology, "ABC123")


def test_barcode_service_runs_parse_before_encode_and_forwards_encode_options() -> None:
    """The service should orchestrate parse -> encode without mutating encode options."""
    service, parser, encoder, profile, events = _build_service()
    encode_options = EncodeOptions(gs1_enabled=True, eci_assignment_number=26)

    barcode = service.generate(" CODE-128 ", "ABC123", encode=encode_options)

    assert events == ["parse", "encode"]
    assert parser.calls == [("ABC123", encode_options)]
    assert encoder.calls == [(parser.payload, encode_options)]
    assert barcode == Barcode(
        symbol=encoder.symbol,
        profile=profile,
        default_render_options=None,
    )


def test_barcode_service_returns_barcode_with_normalized_render_options() -> None:
    """Generation-time render overrides should be normalized and stored on the result."""
    service, _, encoder, profile, _ = _build_service()

    barcode = service.generate(
        "code128",
        "ABC123",
        render=RenderOptions(
            scale=2.5,
            foreground_color=" #222222 ",
            font_family=" IBM Plex Sans ",
        ),
    )

    assert barcode == Barcode(
        symbol=encoder.symbol,
        profile=profile,
        default_render_options=RenderOptions(
            scale=2.5,
            foreground_color="#222222",
            font_family="IBM Plex Sans",
        ),
    )


@pytest.mark.parametrize(
    ("symbology", "data", "expected_width", "expected_data"),
    [
        ("ean13", "400638133393", 95, "4006381333931"),
        ("upca", "03600029145", 95, "036000291452"),
        ("upce", "01200000001", 51, "012000000010"),
    ],
)
def test_default_barcode_service_generates_and_renders_ean_upc_symbols(
    symbology: str,
    data: str,
    expected_width: int,
    expected_data: str,
) -> None:
    """The default service should run EAN/UPC through parse, encode, and SVG rendering."""
    service = build_default_service()

    barcode = service.generate(symbology, data)
    svg = barcode.to_svg()

    assert barcode.profile.status == "beta"
    assert barcode.symbol.metadata.normalized_data == expected_data
    assert barcode.symbol.matrix.width == expected_width
    assert barcode.symbol.matrix.height == 2
    assert svg.startswith("<svg")
    assert "<rect" in svg


def test_barcode_service_rejects_invalid_render_options_before_running_pipeline() -> None:
    """Invalid generation-time render overrides should fail before parse or encode."""
    service, parser, encoder, _, events = _build_service()

    with pytest.raises(InvalidInputError, match="scale"):
        service.generate("code128", "ABC123", render=RenderOptions(scale=0))

    assert events == []
    assert parser.calls == []
    assert encoder.calls == []


def test_barcode_service_wraps_parser_not_implemented_errors() -> None:
    """Placeholder parser failures should surface as UnsupportedFeatureError."""
    events: list[str] = []
    parser = RecordingParser(
        payload=_build_payload(),
        events=events,
        failure=NotImplementedError("parse not implemented"),
    )
    service, _, encoder, _, _ = _build_service(parser=parser)

    with pytest.raises(UnsupportedFeatureError) as exc_info:
        service.generate(" CODE-128 ", "ABC123")

    assert "code128" in str(exc_info.value)
    assert "parse" in str(exc_info.value)
    assert events == ["parse"]
    assert encoder.calls == []


def test_barcode_service_wraps_encoder_not_implemented_errors() -> None:
    """Placeholder encoder failures should surface as UnsupportedFeatureError."""
    events: list[str] = []
    encoder = RecordingEncoder(
        symbol=_build_symbol(),
        events=events,
        failure=NotImplementedError("encode not implemented"),
    )
    service, parser, _, _, _ = _build_service(encoder=encoder)

    with pytest.raises(UnsupportedFeatureError) as exc_info:
        service.generate("code128", "ABC123")

    assert "code128" in str(exc_info.value)
    assert "encode" in str(exc_info.value)
    assert events == ["parse", "encode"]
    assert parser.calls == [("ABC123", None)]


@pytest.mark.parametrize(
    ("stage", "failure", "expected_events"),
    [
        ("parse", InvalidInputError("invalid barcode data"), ["parse"]),
        (
            "encode",
            UnsupportedCapabilityError("requested capability is unsupported"),
            ["parse", "encode"],
        ),
    ],
)
def test_barcode_service_propagates_typed_domain_errors(
    stage: str,
    failure: Exception,
    expected_events: list[str],
) -> None:
    """Typed barcode-domain exceptions should propagate unchanged."""
    events: list[str] = []
    parser = RecordingParser(
        payload=_build_payload(),
        events=events,
        failure=failure if stage == "parse" else None,
    )
    encoder = RecordingEncoder(
        symbol=_build_symbol(),
        events=events,
        failure=failure if stage == "encode" else None,
    )
    service, _, _, _, _ = _build_service(parser=parser, encoder=encoder)

    with pytest.raises(type(failure)) as exc_info:
        service.generate("code128", "ABC123")

    assert exc_info.value is failure
    assert events == expected_events
