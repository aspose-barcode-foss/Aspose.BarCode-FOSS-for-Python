"""Renderable output artifacts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RenderedArtifact:
    """Backend output produced by a renderer."""

    data: str | bytes
    media_type: str
    backend: str
