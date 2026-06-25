"""Generate a Code 128 and a QR code, then save them as SVG and PNG."""

from __future__ import annotations

from pathlib import Path

from aspose_barcode_foss import code128, qr

OUTPUT_DIR = Path(__file__).parent


def main() -> None:
    """Render two barcodes and write them next to this script."""
    svg = code128("ABC-12345").to_svg()
    (OUTPUT_DIR / "code128.output.svg").write_text(svg, encoding="utf-8")

    png = qr("https://example.com").to_png()
    (OUTPUT_DIR / "qr.output.png").write_bytes(png)

    print(f"Wrote code128.output.svg ({len(svg)} chars) and qr.output.png ({len(png)} bytes)")


if __name__ == "__main__":
    main()
