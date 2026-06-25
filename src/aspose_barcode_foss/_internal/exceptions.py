"""Internal exception hierarchy."""


class BarcodeError(Exception):
    """Base exception for the barcode library."""


class SymbologyNotFoundError(BarcodeError):
    """Raised when a requested symbology is not registered."""


class EncodingError(BarcodeError):
    """Raised when encoding fails."""


class RenderingError(BarcodeError):
    """Raised when rendering fails."""


class InvalidInputError(BarcodeError):
    """Raised when the provided input is technically invalid."""


class UnsupportedFeatureError(BarcodeError):
    """Raised when a requested feature is not supported by the library."""


class UnsupportedCapabilityError(BarcodeError):
    """Raised when a symbology does not support a requested capability."""
