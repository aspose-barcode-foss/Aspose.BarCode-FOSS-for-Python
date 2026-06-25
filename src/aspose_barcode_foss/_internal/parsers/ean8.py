"""EAN-8 input parser."""

from __future__ import annotations

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import Ean8Options, EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.standards.ean import compute_check_digit


class Ean8InputParser(InputParser):
    """Validate and normalize EAN-8 input."""

    def parse(
        self,
        data: str | bytes,
        *,
        options: Ean8Options | EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce an EAN-8 payload."""
        normalized_options = self._coerce_options(options)

        if isinstance(data, bytes):
            msg = "EAN-8 does not support bytes input"
            raise UnsupportedCapabilityError(msg)
        if not isinstance(data, str):
            msg = "EAN-8 data must be a text string"
            raise InvalidInputError(msg)

        self._validate_capabilities(normalized_options)

        stripped = data.strip()
        if not stripped:
            msg = "EAN-8 data must not be empty"
            raise InvalidInputError(msg)

        self._validate_digits(stripped)

        digits8 = self._resolve_digits(stripped, normalized_options)
        return NormalizedPayload(symbology="ean8", data=digits8, input_kind="text")

    def _coerce_options(self, options: Ean8Options | EncodeOptions | None) -> Ean8Options:
        """Normalize supported option containers into Ean8Options."""
        if options is None:
            return Ean8Options()
        if isinstance(options, Ean8Options):
            return Ean8Options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                allow_check_digit_input=options.allow_check_digit_input,
            )
        if isinstance(options, EncodeOptions):
            return Ean8Options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
            )
        msg = "encode options must be Ean8Options, EncodeOptions, or None"
        raise InvalidInputError(msg)

    def _validate_capabilities(self, options: Ean8Options) -> None:
        """Reject capability requests that are unsupported for EAN-8."""
        if options.gs1_enabled is True:
            msg = "EAN-8 does not support GS1"
            raise UnsupportedCapabilityError(msg)
        if options.eci_assignment_number is not None:
            msg = "EAN-8 does not support ECI"
            raise UnsupportedCapabilityError(msg)

    def _validate_digits(self, data: str) -> None:
        """Reject input containing non-digit characters, reporting the first offending position."""
        for index, character in enumerate(data, start=1):
            if not "0" <= character <= "9":
                msg = f"EAN-8 data must contain only digits; non-digit character at position {index}: {character!r}"
                raise InvalidInputError(msg)

    def _resolve_digits(self, digits: str, options: Ean8Options) -> str:
        """Return an 8-digit string with a valid check digit, or raise InvalidInputError."""
        length = len(digits)

        if length == 7:
            check = compute_check_digit(digits, start_weight=3)
            return digits + str(check)

        if length == 8:
            if options.allow_check_digit_input is not True:
                msg = "8-digit input requires allow_check_digit_input=True"
                raise InvalidInputError(msg)
            expected = compute_check_digit(digits[:7], start_weight=3)
            if int(digits[7]) != expected:
                msg = f"EAN-8 check digit mismatch: expected {expected}, got {digits[7]}"
                raise InvalidInputError(msg)
            return digits

        msg = f"EAN-8 data must be 7 or 8 digits, got {length}"
        raise InvalidInputError(msg)
