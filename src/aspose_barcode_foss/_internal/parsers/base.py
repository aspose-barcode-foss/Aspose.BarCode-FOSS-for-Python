"""Base interfaces for the parse / validate layer."""

from __future__ import annotations

from abc import ABC, abstractmethod

from aspose_barcode_foss._internal.models.options import EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload


class InputParser(ABC):
    """Abstract parser that validates and normalizes public input."""

    @abstractmethod
    def parse(
        self,
        data: str | bytes,
        *,
        options: EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce a normalized payload."""
        raise NotImplementedError
