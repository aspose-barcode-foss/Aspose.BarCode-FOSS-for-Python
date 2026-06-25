"""Public success-path tests for the Code 128 symbology."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import aspose_barcode_foss as barcode


SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def test_generate_returns_a_public_code128_barcode() -> None:
    """The generic public entrypoint should return a real Code 128 barcode."""
    barcode_obj = barcode.generate("code128", "A")

    assert isinstance(barcode_obj, barcode.Barcode)
    assert barcode_obj.profile.name == "code128"
    assert barcode_obj.symbol.metadata.display_text == "A"


def test_code128_helper_returns_a_public_code128_barcode() -> None:
    """The dedicated helper should return the same public result shape."""
    barcode_obj = barcode.code128("A")

    assert isinstance(barcode_obj, barcode.Barcode)
    assert barcode_obj.profile.name == "code128"
    assert barcode_obj.symbol.metadata.display_text == "A"


def test_code128_public_result_renders_to_svg() -> None:
    """The public Code 128 result should render directly to SVG."""
    svg = barcode.code128("A").to_svg()

    root = ET.fromstring(svg)
    text = root.find(f".//{{{SVG_NAMESPACE}}}text")

    assert root.tag == f"{{{SVG_NAMESPACE}}}svg"
    assert text is not None
    assert text.text == "A"
