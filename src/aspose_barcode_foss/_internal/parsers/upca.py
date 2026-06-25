"""UPC-A input parser."""

from __future__ import annotations

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import EncodeOptions, UpcaOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.standards.ean import compute_check_digit

_GTIN12_START_WEIGHT = 3


class UpcaInputParser(InputParser):
    """Validate and normalize UPC-A input."""

    def parse(
        self,
        data: str | bytes,
        *,
        options: UpcaOptions | EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce a UPC-A payload."""
        if isinstance(data, bytes):
            raise UnsupportedCapabilityError("UPC-A does not support bytes input")
        if not isinstance(data, str):
            raise InvalidInputError("UPC-A data must be a text string")

        normalized_options = self._coerce_options(options)

        if normalized_options.gs1_enabled is True:
            raise UnsupportedCapabilityError("UPC-A does not support GS1 mode")
        if normalized_options.eci_assignment_number is not None:
            raise UnsupportedCapabilityError("UPC-A does not support ECI")

        stripped = data.strip()
        if not stripped:
            raise InvalidInputError("UPC-A data must not be empty")

        for index, ch in enumerate(stripped):
            if not "0" <= ch <= "9":
                raise InvalidInputError(
                    f"UPC-A data must contain only digits; non-digit character at position {index + 1}: {ch!r}"
                )

        length = len(stripped)

        if length == 11:
            check = compute_check_digit(stripped, start_weight=_GTIN12_START_WEIGHT)
            digits12 = stripped + str(check)
        elif length == 12:
            if normalized_options.allow_check_digit_input is not True:
                raise InvalidInputError("12-digit input requires allow_check_digit_input=True")
            expected = compute_check_digit(stripped[:11], start_weight=_GTIN12_START_WEIGHT)
            if int(stripped[11]) != expected:
                raise InvalidInputError(f"UPC-A check digit mismatch: expected {expected}, got {stripped[11]}")
            digits12 = stripped
        else:
            raise InvalidInputError(f"UPC-A data must be 11 or 12 digits, got {length}")

        return NormalizedPayload(symbology="upca", data=digits12, input_kind="text")

    def _coerce_options(self, options: UpcaOptions | EncodeOptions | None) -> UpcaOptions:
        """Normalize supported option containers into UpcaOptions."""
        if options is None:
            return UpcaOptions()
        if isinstance(options, UpcaOptions):
            return options
        if isinstance(options, EncodeOptions):
            return UpcaOptions(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
            )
        raise InvalidInputError("encode options must be UpcaOptions, EncodeOptions, or None")
