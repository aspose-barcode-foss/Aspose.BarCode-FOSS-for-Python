"""Logical text layout models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class TextSegment:
    """One segment of human-readable text.

    Renderers consume ``anchor`` values of ``"start"``, ``"middle"``, and
    ``"end"``.

    ``offset_x`` and ``offset_y`` are expressed in resolved SVG user units
    after option scaling and before quiet-zone translation. The coordinate
    origin is the top-left corner of the module area, not the full canvas.

    ``offset_y`` represents the top of the text box rather than a baseline,
    which is why the SVG backend emits ``dominant-baseline="hanging"``.
    Text policies are responsible for positioning text below the bars when
    desired and for choosing coordinates that fit within the targeted width.
    """

    text: str
    anchor: str
    offset_x: float
    offset_y: float


@dataclass(slots=True, frozen=True)
class TextLayout:
    """Logical text layout derived from a symbol and rendering options.

    Renderers treat each segment as an already-resolved placement instruction.
    They do not measure text, wrap text, or widen the canvas to make a layout
    fit.
    """

    segments: tuple[TextSegment, ...] = field(default_factory=tuple)
