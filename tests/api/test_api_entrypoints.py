"""Contract tests for public API helper delegation."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

import aspose_barcode_foss.api as api
from aspose_barcode_foss._internal.models.options import EncodeOptions, RenderOptions


@dataclass
class RecordingService:
    """Service double that records public API delegation inputs."""

    result: object = field(default_factory=object)
    calls: list[
        tuple[
            str,
            str | bytes,
            EncodeOptions | None,
            RenderOptions | None,
        ]
    ] = field(default_factory=list)

    def generate(
        self,
        symbology: str,
        data: str | bytes,
        *,
        encode: EncodeOptions | None = None,
        render: RenderOptions | None = None,
    ) -> object:
        self.calls.append((symbology, data, encode, render))
        return self.result


def test_generate_delegates_to_the_default_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The top-level generator should forward all inputs unchanged."""
    service = RecordingService()
    encode_options = EncodeOptions(eci_assignment_number=26)
    render_options = RenderOptions(scale=2.0)

    monkeypatch.setattr(api, "_get_default_service", lambda: service)

    result = api.generate(
        " CODE-128 ",
        b"ABC123",
        encode=encode_options,
        render=render_options,
    )

    assert result is service.result
    assert service.calls == [(" CODE-128 ", b"ABC123", encode_options, render_options)]


@pytest.mark.parametrize(
    ("helper_name", "expected_symbology"),
    [
        ("code128", "code128"),
        ("ean13", "ean13"),
        ("upca", "upca"),
        ("upce", "upce"),
    ],
)
def test_symbology_helpers_delegate_with_canonical_ids(
    monkeypatch: pytest.MonkeyPatch,
    helper_name: str,
    expected_symbology: str,
) -> None:
    """Symbology-specific helpers should route through generate() with canonical ids."""
    calls: list[
        tuple[
            str,
            str | bytes,
            EncodeOptions | None,
            RenderOptions | None,
        ]
    ] = []
    expected_result = object()
    encode_options = EncodeOptions(eci_assignment_number=7)
    render_options = RenderOptions(foreground_color="#202020")

    def fake_generate(
        symbology: str,
        data: str | bytes,
        *,
        encode: EncodeOptions | None = None,
        render: RenderOptions | None = None,
    ) -> object:
        calls.append((symbology, data, encode, render))
        return expected_result

    monkeypatch.setattr(api, "generate", fake_generate)

    helper = getattr(api, helper_name)
    result = helper("ABC123", encode=encode_options, render=render_options)

    assert result is expected_result
    assert calls == [
        (expected_symbology, "ABC123", encode_options, render_options),
    ]
