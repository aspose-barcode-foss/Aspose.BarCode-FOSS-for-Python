"""Base text layout policy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol
from aspose_barcode_foss._internal.models.text import TextLayout


class TextLayoutPolicy(ABC):
    """Abstract interface for symbology-specific text layout."""

    @abstractmethod
    def create_layout(
        self,
        symbol: EncodedSymbol,
        *,
        options: ResolvedRenderOptions,
    ) -> TextLayout:
        """Create logical text layout for an encoded symbol."""
        raise NotImplementedError
