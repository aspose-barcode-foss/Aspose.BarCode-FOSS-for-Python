"""Base encoder interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from aspose_barcode_foss._internal.models.options import EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol


class SymbologyEncoder(ABC):
    """Abstract interface implemented by all symbology encoders."""

    @abstractmethod
    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: EncodeOptions | None = None,
    ) -> EncodedSymbol:
        """Encode normalized input data into a logical symbol."""
        raise NotImplementedError
