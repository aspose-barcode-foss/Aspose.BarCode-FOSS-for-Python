"""UPC-E input parser."""

from __future__ import annotations

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import EncodeOptions, UpceOptions
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.standards.ean import compute_check_digit, upce_zero_suppress


class UpceInputParser(InputParser):
    """Validate and normalize UPC-E input."""

    def parse(
        self,
        data: str | bytes,
        *,
        options: UpceOptions | EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce a UPC-E payload."""
        normalized_options = self._coerce_options(options)

        if isinstance(data, bytes):
            msg = "UPC-E does not support bytes input"
            raise UnsupportedCapabilityError(msg)
        if not isinstance(data, str):
            msg = "UPC-E data must be a text string"
            raise InvalidInputError(msg)

        self._validate_capabilities(normalized_options)
        self._validate_number_system(normalized_options)

        stripped = data.strip()
        if not stripped:
            msg = "UPC-E data must not be empty"
            raise InvalidInputError(msg)

        self._validate_digits(stripped)

        digits12 = self._resolve_digits(stripped, normalized_options)

        if digits12[0] != "0":
            msg = f"UPC-E requires number system digit 0 (D1='0'); got {digits12[0]!r}"
            raise InvalidInputError(msg)

        suppressed = upce_zero_suppress(digits12)
        if suppressed is None:
            msg = (
                f"UPC-E input {digits12!r} cannot be zero-suppressed: "
                "it does not satisfy any of the zero-suppression rules (2a, 2b, 2c, 2d)"
            )
            raise InvalidInputError(msg)

        return NormalizedPayload(symbology="upce", data=digits12, input_kind="text")

    def _coerce_options(self, options: UpceOptions | EncodeOptions | None) -> UpceOptions:
        """Normalize supported option containers into UpceOptions."""
        if options is None:
            return UpceOptions()
        if isinstance(options, UpceOptions):
            return UpceOptions(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                number_system=options.number_system,
                allow_check_digit_input=options.allow_check_digit_input,
            )
        if isinstance(options, EncodeOptions):
            return UpceOptions(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
            )
        msg = "encode options must be UpceOptions, EncodeOptions, or None"
        raise InvalidInputError(msg)

    def _validate_capabilities(self, options: UpceOptions) -> None:
        """Reject capability requests that are unsupported for UPC-E."""
        if options.gs1_enabled is True:
            msg = "UPC-E does not support GS1"
            raise UnsupportedCapabilityError(msg)
        if options.eci_assignment_number is not None:
            msg = "UPC-E does not support ECI"
            raise UnsupportedCapabilityError(msg)

    def _validate_number_system(self, options: UpceOptions) -> None:
        """Reject number_system values other than None or '0'."""
        if options.number_system is not None and options.number_system != "0":
            msg = f"UPC-E only supports number system '0'; got {options.number_system!r}"
            raise InvalidInputError(msg)

    def _validate_digits(self, data: str) -> None:
        """Reject input containing non-digit characters, reporting the first offending position."""
        for index, character in enumerate(data, start=1):
            if not "0" <= character <= "9":
                msg = f"UPC-E data must contain only digits; non-digit character at position {index}: {character!r}"
                raise InvalidInputError(msg)

    def _resolve_digits(self, digits: str, options: UpceOptions) -> str:
        """Return a 12-digit GTIN-12 string with a valid check digit, or raise InvalidInputError."""
        length = len(digits)

        if length == 11:
            check = compute_check_digit(digits, start_weight=3)
            return digits + str(check)

        if length == 12:
            if options.allow_check_digit_input is not True:
                msg = "12-digit input requires allow_check_digit_input=True"
                raise InvalidInputError(msg)
            expected = compute_check_digit(digits[:11], start_weight=3)
            if int(digits[11]) != expected:
                msg = f"UPC-E check digit mismatch: expected {expected}, got {digits[11]}"
                raise InvalidInputError(msg)
            return digits

        msg = f"UPC-E data must be 11 or 12 digits, got {length}"
        raise InvalidInputError(msg)
