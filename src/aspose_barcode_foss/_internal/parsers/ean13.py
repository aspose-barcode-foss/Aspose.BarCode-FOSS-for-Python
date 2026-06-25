"""EAN-13 input parser."""

from __future__ import annotations

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import Ean13Options, EncodeOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.standards.ean import compute_check_digit


class Ean13InputParser(InputParser):
    """Validate and normalize EAN-13 input."""

    def parse(
        self,
        data: str | bytes,
        *,
        options: Ean13Options | EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce an EAN-13 payload."""
        normalized_options = self._coerce_options(options)

        if isinstance(data, bytes):
            msg = "EAN-13 does not support bytes input"
            raise UnsupportedCapabilityError(msg)
        if not isinstance(data, str):
            msg = "EAN-13 data must be a text string"
            raise InvalidInputError(msg)

        self._validate_capabilities(normalized_options)

        stripped = data.strip()
        if not stripped:
            msg = "EAN-13 data must not be empty"
            raise InvalidInputError(msg)

        self._validate_digits(stripped)

        digits13 = self._resolve_digits(stripped, normalized_options)
        return NormalizedPayload(symbology="ean13", data=digits13, input_kind="text")

    def _coerce_options(self, options: Ean13Options | EncodeOptions | None) -> Ean13Options:
        """Normalize supported option containers into Ean13Options."""
        if options is None:
            return Ean13Options()
        if isinstance(options, Ean13Options):
            return Ean13Options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                allow_check_digit_input=options.allow_check_digit_input,
            )
        if isinstance(options, EncodeOptions):
            return Ean13Options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
            )
        msg = "encode options must be Ean13Options, EncodeOptions, or None"
        raise InvalidInputError(msg)

    def _validate_capabilities(self, options: Ean13Options) -> None:
        """Reject capability requests that are unsupported for EAN-13."""
        if options.gs1_enabled is True:
            msg = "EAN-13 does not support GS1"
            raise UnsupportedCapabilityError(msg)
        if options.eci_assignment_number is not None:
            msg = "EAN-13 does not support ECI"
            raise UnsupportedCapabilityError(msg)

    def _validate_digits(self, data: str) -> None:
        """Reject input containing non-digit characters, reporting the first offending position."""
        for index, character in enumerate(data, start=1):
            if not "0" <= character <= "9":
                msg = f"EAN-13 data must contain only digits; non-digit character at position {index}: {character!r}"
                raise InvalidInputError(msg)

    def _resolve_digits(self, digits: str, options: Ean13Options) -> str:
        """Return a 13-digit string with a valid check digit, or raise InvalidInputError."""
        length = len(digits)

        if length == 12:
            check = compute_check_digit(digits, start_weight=1)
            return digits + str(check)

        if length == 13:
            if options.allow_check_digit_input is not True:
                msg = "13-digit input requires allow_check_digit_input=True"
                raise InvalidInputError(msg)
            expected = compute_check_digit(digits[:12], start_weight=1)
            if int(digits[12]) != expected:
                msg = f"EAN-13 check digit mismatch: expected {expected}, got {digits[12]}"
                raise InvalidInputError(msg)
            return digits

        msg = f"EAN-13 data must be 12 or 13 digits, got {length}"
        raise InvalidInputError(msg)
