"""Capability metadata used by profiles and support-matrix reporting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SupportLevel = Literal["unsupported", "partial", "full"]
SymbologyStatus = Literal["stable", "beta", "planned"]


@dataclass(slots=True, frozen=True)
class SymbologyCapabilities:
    """Capability metadata for one symbology."""

    gs1_support: SupportLevel
    eci_support: SupportLevel
    structured_append_support: SupportLevel
    binary_input_support: SupportLevel
    rendering_outputs: tuple[str, ...]
