"""Contract tests for render-option resolution."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.capabilities import SymbologyCapabilities
from aspose_barcode_foss._internal.models.options import (
    RenderOptions,
    ResolvedRenderOptions,
)
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout
from aspose_barcode_foss._internal.profiles.base import SymbologyProfile
from aspose_barcode_foss._internal.resolver import OptionsResolver
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


class StaticTextLayoutPolicy(TextLayoutPolicy):
    """Minimal policy double for direct profile construction in tests."""

    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        return TextLayout()


def _build_defaults() -> ResolvedRenderOptions:
    return ResolvedRenderOptions(
        scale=2.0,
        dpi=300,
        module_width=1.5,
        module_height=24.0,
        quiet_zone=6.0,
        foreground_color="#111111",
        background_color="#f8f8f8",
        transparent_background=False,
        show_text=True,
        font_family="Fira Sans",
        font_size=9.0,
    )


def _build_profile(defaults: ResolvedRenderOptions | None = None) -> SymbologyProfile:
    return SymbologyProfile(
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
        text_policy=StaticTextLayoutPolicy(),
    )


def test_options_resolver_uses_profile_defaults_when_options_are_missing() -> None:
    """Resolution with no user options should mirror the profile defaults."""
    profile = _build_profile()

    resolved = OptionsResolver().resolve(profile, options=None)

    assert resolved == ResolvedRenderOptions(
        scale=2.0,
        dpi=300,
        module_width=1.5,
        module_height=24.0,
        quiet_zone=6.0,
        foreground_color="#111111",
        background_color="#f8f8f8",
        transparent_background=False,
        show_text=True,
        font_family="Fira Sans",
        font_size=9.0,
    )


@pytest.mark.parametrize(
    "options",
    [
        RenderOptions(
            scale=3.0,
            foreground_color=" #222222 ",
            background_color=" #f0f0f0 ",
            font_family=" IBM Plex Sans ",
        ),
    ],
)
def test_options_resolver_coerces_inputs_to_normalized_render_options(
    options: RenderOptions,
) -> None:
    """Coercion should normalize RenderOptions into trimmed RenderOptions."""
    coerced = OptionsResolver().coerce_options(options)

    assert coerced == RenderOptions(
        scale=3.0,
        foreground_color="#222222",
        background_color="#f0f0f0",
        font_family="IBM Plex Sans",
    )


def test_options_resolver_coerce_options_returns_none_for_empty_overrides() -> None:
    """Empty override layers should normalize to None."""
    resolver = OptionsResolver()

    assert resolver.coerce_options(RenderOptions()) is None
    assert resolver.coerce_options(RenderOptions(scale=None, show_text=None)) is None


@pytest.mark.parametrize(
    "options",
    [
        RenderOptions(
            scale=3.0,
            module_width=2.0,
            foreground_color="#222222",
            font_family="IBM Plex Sans",
            font_size=11.0,
        ),
    ],
)
def test_options_resolver_applies_render_options_overrides(
    options: RenderOptions,
) -> None:
    """RenderOptions should override the resolved fields they provide."""
    profile = _build_profile()

    resolved = OptionsResolver().resolve(profile, options=options)

    assert resolved == ResolvedRenderOptions(
        scale=3.0,
        dpi=300,
        module_width=2.0,
        module_height=24.0,
        quiet_zone=6.0,
        foreground_color="#222222",
        background_color="#f8f8f8",
        transparent_background=False,
        show_text=True,
        font_family="IBM Plex Sans",
        font_size=11.0,
    )


@pytest.mark.parametrize(
    "options",
    [
        RenderOptions(foreground_color=" "),
        RenderOptions(font_family=" "),
    ],
)
def test_options_resolver_coerce_options_rejects_blank_string_values(
    options: RenderOptions,
) -> None:
    """Coercion should fail fast for blank string overrides."""
    with pytest.raises(InvalidInputError):
        OptionsResolver().coerce_options(options)


def test_options_resolver_treats_none_fields_as_not_provided() -> None:
    """Fields set to None should fall back to the profile defaults."""
    profile = _build_profile()

    resolved = OptionsResolver().resolve(
        profile,
        options=RenderOptions(
            scale=None,
            foreground_color=None,
            show_text=None,
        ),
    )

    assert resolved == ResolvedRenderOptions(
        scale=2.0,
        dpi=300,
        module_width=1.5,
        module_height=24.0,
        quiet_zone=6.0,
        foreground_color="#111111",
        background_color="#f8f8f8",
        transparent_background=False,
        show_text=True,
        font_family="Fira Sans",
        font_size=9.0,
    )


def test_options_resolver_forces_background_to_none_for_transparency() -> None:
    """Transparent backgrounds should always resolve to a None background color."""
    profile = _build_profile()

    resolved = OptionsResolver().resolve(
        profile,
        options=RenderOptions(
            background_color="#ffffff",
            transparent_background=True,
        ),
    )

    assert resolved.transparent_background is True
    assert resolved.background_color is None


def test_options_resolver_merge_options_applies_later_layer_precedence() -> None:
    """Later overrides should replace earlier values field by field."""
    merged = OptionsResolver().merge_options(
        RenderOptions(
            scale=2.0,
            foreground_color=" #111111 ",
            show_text=False,
        ),
        RenderOptions(
            scale=3.0,
            foreground_color=None,
            show_text=True,
            font_family=" IBM Plex Sans ",
        ),
    )

    assert merged == RenderOptions(
        scale=3.0,
        foreground_color="#111111",
        show_text=True,
        font_family="IBM Plex Sans",
    )


def test_options_resolver_merge_options_returns_none_for_empty_layers() -> None:
    """Merging empty override layers should keep the result unset."""
    resolver = OptionsResolver()

    assert resolver.merge_options(None, None) is None
    assert resolver.merge_options(RenderOptions(), RenderOptions(scale=None)) is None


@pytest.mark.parametrize(
    "options",
    [
        RenderOptions(scale=0.0),
        RenderOptions(module_width=0.0),
        RenderOptions(module_height=0.0),
        RenderOptions(font_size=0.0),
        RenderOptions(quiet_zone=-0.1),
        RenderOptions(dpi=0),
    ],
)
def test_options_resolver_rejects_invalid_numeric_ranges(
    options: RenderOptions,
) -> None:
    """Numeric render settings must respect the documented range constraints."""
    profile = _build_profile()

    with pytest.raises(InvalidInputError):
        OptionsResolver().resolve(profile, options=options)


@pytest.mark.parametrize(
    "options",
    [
        RenderOptions(foreground_color=" "),
        RenderOptions(background_color="\t"),
        RenderOptions(font_family=" "),
    ],
)
def test_options_resolver_rejects_blank_string_values(options: RenderOptions) -> None:
    """String render settings should reject empty-or-whitespace-only values."""
    profile = _build_profile()

    with pytest.raises(InvalidInputError):
        OptionsResolver().resolve(profile, options=options)


@pytest.mark.parametrize(
    "options",
    [
        RenderOptions(show_text="yes"),  # type: ignore[arg-type]
        RenderOptions(transparent_background="no"),  # type: ignore[arg-type]
        RenderOptions(scale=object()),  # type: ignore[arg-type]
    ],
)
def test_options_resolver_rejects_invalid_value_types(
    options: RenderOptions,
) -> None:
    """Resolver input must reject runtime types that do not match the contract."""
    profile = _build_profile()

    with pytest.raises(InvalidInputError):
        OptionsResolver().resolve(profile, options=options)


@pytest.mark.parametrize("options", [object(), [], {}, 3.14])
def test_options_resolver_rejects_unsupported_option_containers(
    options: object,
) -> None:
    """Resolver input should reject any non-RenderOptions container."""
    profile = _build_profile()

    with pytest.raises(InvalidInputError, match="RenderOptions"):
        OptionsResolver().resolve(profile, options=options)  # type: ignore[arg-type]


def test_options_resolver_preserves_dpi_in_resolved_options() -> None:
    """DPI should remain part of the resolved contract for future backends."""
    profile = _build_profile()

    resolved = OptionsResolver().resolve(profile, options=RenderOptions(dpi=600))

    assert resolved.dpi == 600
