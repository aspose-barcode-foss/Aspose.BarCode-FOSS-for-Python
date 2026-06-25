"""Contract tests for the concrete symbology registry bootstrap."""

from __future__ import annotations

from dataclasses import fields

import pytest

from aspose_barcode_foss._internal.bootstrap import build_default_registry, build_default_service
from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import SymbologyNotFoundError
from aspose_barcode_foss._internal.models.capabilities import SymbologyCapabilities
from aspose_barcode_foss._internal.models.options import EncodeOptions, ResolvedRenderOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.profiles.base import SymbologyProfile
from aspose_barcode_foss._internal.registry import SymbologyDefinition, SymbologyRegistry
from aspose_barcode_foss._internal.resolver import OptionsResolver
from aspose_barcode_foss._internal.service import BarcodeService
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


class TestInputParser(InputParser):
    """Minimal parser double for direct registry tests."""

    def parse(
        self,
        data: str | bytes,
        *,
        options: EncodeOptions | None = None,
    ) -> NormalizedPayload:
        raise AssertionError("parser should not be called in registry tests")


class TestEncoder(SymbologyEncoder):
    """Minimal encoder double for direct registry tests."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: EncodeOptions | None = None,
    ) -> EncodedSymbol:
        raise AssertionError("encoder should not be called in registry tests")


class TestTextPolicy(TextLayoutPolicy):
    """Minimal text-policy double for direct registry tests."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        raise AssertionError("text policy should not be called in registry tests")


def _build_profile(
    name: str,
    *,
    text_policy: TextLayoutPolicy | None = None,
) -> SymbologyProfile:
    return SymbologyProfile(
        name=name,
        status="stable",
        defaults=ResolvedRenderOptions(
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
        ),
        capabilities=SymbologyCapabilities(
            gs1_support="unsupported",
            eci_support="unsupported",
            structured_append_support="unsupported",
            binary_input_support="unsupported",
            rendering_outputs=("svg",),
        ),
        text_policy=text_policy or TestTextPolicy(),
    )


def _build_definition(
    name: str,
    *,
    aliases: tuple[str, ...] = (),
    text_policy: TextLayoutPolicy | None = None,
) -> SymbologyDefinition:
    return SymbologyDefinition(
        name=name,
        aliases=aliases,
        parser=TestInputParser(),
        encoder=TestEncoder(),
        profile=_build_profile(name.strip().lower(), text_policy=text_policy),
    )


def test_registry_returns_definitions_for_canonical_names() -> None:
    """Canonical-name lookup should resolve the stored definition."""
    registry = SymbologyRegistry()
    definition = _build_definition("code128")

    registry.register(definition)

    resolved = registry.get_definition(" CODE128 ")

    assert resolved.name == "code128"
    assert resolved.aliases == ()
    assert registry.get_parser("code128") is resolved.parser
    assert registry.get_encoder("code128") is resolved.encoder
    assert registry.get_profile("code128") is resolved.profile


def test_registry_returns_definitions_for_aliases() -> None:
    """Aliases should normalize to the same canonical definition."""
    registry = SymbologyRegistry()
    definition = _build_definition("code128", aliases=("code-128",))

    registry.register(definition)

    canonical = registry.get_definition("code128")
    alias = registry.get_definition(" CODE-128 ")

    assert alias is canonical
    assert alias.aliases == ("code-128",)


def test_registry_raises_for_unknown_names() -> None:
    """Unknown normalized names should raise SymbologyNotFoundError."""
    registry = SymbologyRegistry()

    with pytest.raises(SymbologyNotFoundError, match="missing"):
        registry.get_definition(" missing ")


def test_registry_rejects_duplicate_canonical_names() -> None:
    """Canonical-name collisions should fail before mutating the registry."""
    registry = SymbologyRegistry()
    registry.register(_build_definition("code128"))

    with pytest.raises(ValueError, match="code128"):
        registry.register(_build_definition(" CODE128 "))


def test_registry_rejects_duplicate_aliases() -> None:
    """Alias collisions should fail before mutating the registry."""
    registry = SymbologyRegistry()
    registry.register(_build_definition("code128", aliases=("code-128",)))

    with pytest.raises(ValueError, match="code-128"):
        registry.register(_build_definition("ean13", aliases=(" code-128 ",)))


def test_registry_derives_text_policy_from_the_profile() -> None:
    """The registry should expose the profile-owned text policy directly."""
    registry = SymbologyRegistry()
    text_policy = TestTextPolicy()
    definition = _build_definition("code128", text_policy=text_policy)

    registry.register(definition)

    assert "text_policy" not in {field.name for field in fields(SymbologyDefinition)}
    assert registry.get_text_policy("code128") is registry.get_profile("code128").text_policy
    assert registry.get_text_policy("code128") is text_policy


@pytest.mark.parametrize(
    ("name", "expected_alias", "expected_quiet_zone"),
    [
        ("code128", "code-128", 20.0),
        ("ean13", "ean-13", 22.0),
        ("upca", "upc-a", 18.0),
        ("upce", "upc-e", 18.0),
    ],
)
def test_default_registry_bootstrap_registers_canonical_names_and_aliases(
    name: str,
    expected_alias: str,
    expected_quiet_zone: float,
) -> None:
    """The default bootstrap should publish all canonical ids and aliases."""
    registry = build_default_registry()

    canonical = registry.get_definition(name)
    alias = registry.get_definition(expected_alias)

    assert alias is canonical
    assert canonical.name == name
    assert canonical.aliases == (expected_alias,)
    assert canonical.profile.name == name
    assert canonical.profile.capabilities == _expected_capabilities()

    if name == "code128":
        _assert_code128_profile(canonical.profile)
    else:
        _assert_ean_upc_profile(canonical.profile, quiet_zone=expected_quiet_zone)


def test_default_service_bootstrap_wires_registry_and_options_resolver() -> None:
    """The default service bootstrap should wire a fresh registry and resolver."""
    service = build_default_service()

    assert isinstance(service, BarcodeService)
    assert isinstance(service.registry, SymbologyRegistry)
    assert isinstance(service.options_resolver, OptionsResolver)
    assert service.registry.get_definition("upce").name == "upce"


def _expected_capabilities() -> SymbologyCapabilities:
    return SymbologyCapabilities(
        gs1_support="unsupported",
        eci_support="unsupported",
        structured_append_support="unsupported",
        binary_input_support="unsupported",
        rendering_outputs=("svg",),
    )


def _expected_defaults(
    *,
    quiet_zone: float,
    module_height: float = 10.0,
) -> ResolvedRenderOptions:
    return ResolvedRenderOptions(
        scale=1.0,
        dpi=300,
        module_width=2.0,
        module_height=module_height,
        quiet_zone=quiet_zone,
        foreground_color="#111111",
        background_color="#fefefe",
        transparent_background=False,
        show_text=True,
        font_family="Fira Sans",
        font_size=8.0,
    )


def _assert_code128_profile(profile: SymbologyProfile) -> None:
    assert profile.status == "beta"
    assert profile.defaults == _expected_defaults(quiet_zone=20.0)
    assert profile.spec_references
    assert profile.known_limitations
    assert any("Code Set B" in item for item in profile.spec_references)
    assert any("checksum" in item for item in profile.spec_references)
    assert any("stop pattern" in item for item in profile.spec_references)
    assert any("GS1" in item for item in profile.known_limitations)
    assert any("ECI" in item for item in profile.known_limitations)
    assert any("bytes / binary input" in item for item in profile.known_limitations)
    assert any("Code Set A/C" in item for item in profile.known_limitations)
    assert any("Shift" in item for item in profile.known_limitations)
    assert any("switching" in item for item in profile.known_limitations)
    assert any("SVG backend" in item for item in profile.known_limitations)
    assert any("quiet_zone overrides" in item for item in profile.known_limitations)
    assert not any("not implemented yet" in item for item in profile.spec_references)


def _assert_ean_upc_profile(
    profile: SymbologyProfile,
    *,
    quiet_zone: float,
) -> None:
    assert profile.status == "beta"
    assert profile.defaults == _expected_defaults(
        quiet_zone=quiet_zone,
        module_height=138.5,
    )
    assert profile.spec_references
    assert profile.known_limitations
    assert any("ISO/IEC 15420:2009" in item for item in profile.spec_references)
    assert any("5X below data bars" in item for item in profile.spec_references)
    assert any("Bar/space compensation" in item for item in profile.known_limitations)
    assert any("Symmetric quiet zone" in item for item in profile.known_limitations)
    assert any("GS1, ECI, and binary input" in item for item in profile.known_limitations)
    assert any("EAN-2 and EAN-5" in item for item in profile.known_limitations)
    assert not any("not implemented yet" in item for item in profile.spec_references)
    assert not any("not implemented yet" in item for item in profile.known_limitations)
