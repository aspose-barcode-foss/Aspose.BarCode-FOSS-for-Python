"""Code 39 profile."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.profiles.base import SymbologyProfile


@dataclass(slots=True, frozen=True)
class Code39Profile(SymbologyProfile):
    """Profile for Code 39 defaults and text behavior."""
