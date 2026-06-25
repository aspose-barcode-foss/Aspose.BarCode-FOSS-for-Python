"""Public API entry points."""

from __future__ import annotations

from functools import lru_cache

from aspose_barcode_foss._internal.bootstrap import build_default_service
from aspose_barcode_foss._internal.models.options import (
    Code128Options,
    Code39Options,
    Ean8Options,
    Ean13Options,
    EncodeOptions,
    QrOptions,
    RenderOptions,
    UpcaOptions,
    UpceOptions,
)
from aspose_barcode_foss._internal.service import BarcodeService
from aspose_barcode_foss.result import Barcode


@lru_cache(maxsize=1)
def _get_default_service() -> BarcodeService:
    """Return the lazily initialized default barcode service."""
    return build_default_service()


def generate(
    symbology: str,
    data: str | bytes,
    *,
    encode: EncodeOptions | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create a barcode for the requested symbology."""
    return _get_default_service().generate(
        symbology,
        data,
        encode=encode,
        render=render,
    )


def code128(
    data: str | bytes,
    *,
    encode: Code128Options | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create a Code 128 barcode."""
    return generate("code128", data, encode=encode, render=render)


def code39(
    data: str | bytes,
    *,
    encode: Code39Options | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create a Code 39 (base, 43-character set) barcode."""
    return generate("code39", data, encode=encode, render=render)


def code39ext(
    data: str | bytes,
    *,
    encode: Code39Options | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create an Extended / Full-ASCII Code 39 barcode."""
    return generate("code39ext", data, encode=encode, render=render)


def ean13(
    data: str | bytes,
    *,
    encode: Ean13Options | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create an EAN-13 barcode."""
    return generate("ean13", data, encode=encode, render=render)


def ean8(
    data: str | bytes,
    *,
    encode: Ean8Options | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create an EAN-8 barcode."""
    return generate("ean8", data, encode=encode, render=render)


def upca(
    data: str | bytes,
    *,
    encode: UpcaOptions | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create a UPC-A barcode."""
    return generate("upca", data, encode=encode, render=render)


def upce(
    data: str | bytes,
    *,
    encode: UpceOptions | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create a UPC-E barcode."""
    return generate("upce", data, encode=encode, render=render)


def qr(
    data: str | bytes,
    *,
    encode: QrOptions | None = None,
    render: RenderOptions | None = None,
) -> Barcode:
    """Create a QR Code (Model 2) barcode."""
    return generate("qr", data, encode=encode, render=render)
