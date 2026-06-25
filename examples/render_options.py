"""Control output appearance with RenderOptions and a custom renderer."""

from __future__ import annotations

from pathlib import Path

from aspose_barcode_foss import RenderOptions, SvgRenderer, code128

OUTPUT_DIR = Path(__file__).parent


def main() -> None:
    """Render the same barcode through the convenience wrapper and an explicit renderer."""
    barcode = code128("Hello-World")

    options = RenderOptions(
        scale=2.0,
        foreground_color="#224466",
        background_color="#fff8f0",
        show_text=True,
        font_size=9.0,
    )

    # to_svg() is a convenience wrapper around render(SvgRenderer(), ...).
    svg = barcode.to_svg(options=options)
    artifact = barcode.render(SvgRenderer(), options=options)
    assert artifact.data == svg

    (OUTPUT_DIR / "styled.output.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote styled.output.svg ({len(svg)} chars)")


if __name__ == "__main__":
    main()
