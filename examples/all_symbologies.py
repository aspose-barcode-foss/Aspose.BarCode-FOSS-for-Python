"""Generate every supported symbology through its dedicated helper."""

from __future__ import annotations

from aspose_barcode_foss import code128, code39, code39ext, ean8, ean13, qr, upca, upce

SAMPLES = [
    ("Code 128", code128, "ABC-12345"),
    ("Code 39", code39, "ABC-123"),
    ("Code 39 Extended", code39ext, "Item #42"),
    ("EAN-13", ean13, "590123412345"),
    ("EAN-8", ean8, "1234567"),
    ("UPC-A", upca, "01234567890"),
    ("UPC-E", upce, "01234500005"),
    ("QR Code", qr, "https://example.com"),
]


def main() -> None:
    """Encode one sample per symbology and print the resulting module grid size."""
    for label, factory, data in SAMPLES:
        matrix = factory(data).symbol.matrix
        print(f"{label:18} {data!r:18} -> {matrix.width}x{matrix.height} modules")


if __name__ == "__main__":
    main()
