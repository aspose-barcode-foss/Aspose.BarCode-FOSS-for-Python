"""Code 39 input parser."""

from __future__ import annotations

from numbers import Integral

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import (
    Code39EncodeMode,
    Code39Options,
    EncodeOptions,
)
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.standards.code39 import CODE39_VALUES

_CODE39_ASCII_MAX_CODE = 127


class Code39InputParser(InputParser):
    """Validate and normalize Code 39 input."""

    def __init__(self, *, default_full_ascii: bool, symbology_name: str) -> None:
        """Store the definition's default mode and emitted symbology name."""
        self._default_full_ascii = default_full_ascii
        self._symbology_name = symbology_name

    def parse(
        self,
        data: str | bytes,
        *,
        options: Code39Options | EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce a Code 39 payload."""
        normalized_options = self._coerce_options(options)

        if isinstance(data, bytes):
            msg = "Code 39 does not support bytes input"
            raise UnsupportedCapabilityError(msg)
        if not isinstance(data, str):
            msg = "Code 39 data must be a text string"
            raise InvalidInputError(msg)

        self._validate_capabilities(normalized_options)

        if not data:
            msg = "Code 39 text must not be empty"
            raise InvalidInputError(msg)

        full_ascii = (
            normalized_options.full_ascii if normalized_options.full_ascii is not None else self._default_full_ascii
        )
        mode = Code39EncodeMode.FULL_ASCII if full_ascii else Code39EncodeMode.BASE

        if mode is Code39EncodeMode.FULL_ASCII:
            self._validate_full_ascii_text(data)
        else:
            self._validate_base_text(data)

        add_check = normalized_options.add_check_digit is True

        return NormalizedPayload(
            symbology=self._symbology_name,
            data=data,
            input_kind="text",
            code39_encode_mode=mode,
            code39_add_check_digit=add_check,
        )

    def _coerce_options(
        self,
        options: Code39Options | EncodeOptions | None,
    ) -> Code39Options:
        """Normalize supported option containers into Code39Options."""
        if options is None:
            return Code39Options()
        if isinstance(options, Code39Options):
            return self._build_options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                full_ascii=options.full_ascii,
                add_check_digit=options.add_check_digit,
            )
        if isinstance(options, EncodeOptions):
            return self._build_options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                full_ascii=None,
                add_check_digit=None,
            )

        msg = "encode options must be Code39Options, EncodeOptions, or None"
        raise InvalidInputError(msg)

    def _build_options(
        self,
        *,
        gs1_enabled: object,
        eci_assignment_number: object,
        full_ascii: object,
        add_check_digit: object,
    ) -> Code39Options:
        """Validate option value types before capability checks run."""
        return Code39Options(
            gs1_enabled=self._normalize_gs1_enabled(gs1_enabled),
            eci_assignment_number=self._normalize_eci_assignment_number(eci_assignment_number),
            full_ascii=self._normalize_bool_flag(full_ascii, "full_ascii"),
            add_check_digit=self._normalize_bool_flag(add_check_digit, "add_check_digit"),
        )

    def _normalize_gs1_enabled(self, value: object) -> bool | None:
        """Validate the GS1 flag shape."""
        if value is None or type(value) is bool:
            return value

        msg = "gs1_enabled must be a boolean"
        raise InvalidInputError(msg)

    def _normalize_eci_assignment_number(self, value: object) -> int | None:
        """Validate the optional ECI assignment number shape."""
        if value is None:
            return None
        if not isinstance(value, Integral) or isinstance(value, bool):
            msg = "eci_assignment_number must be an integer"
            raise InvalidInputError(msg)
        return int(value)

    def _normalize_bool_flag(self, value: object, name: str) -> bool | None:
        """Validate an optional boolean option flag."""
        if value is None or type(value) is bool:
            return value

        msg = f"{name} must be a boolean"
        raise InvalidInputError(msg)

    def _validate_capabilities(self, options: Code39Options) -> None:
        """Reject capability requests that Code 39 does not support."""
        if options.gs1_enabled is True:
            msg = "Code 39 does not support GS1"
            raise UnsupportedCapabilityError(msg)
        if options.eci_assignment_number is not None:
            msg = "Code 39 does not support ECI"
            raise UnsupportedCapabilityError(msg)

    def _validate_base_text(self, data: str) -> None:
        """Reject characters outside the 43-character base set (NF-1/NF-6)."""
        for index, character in enumerate(data, start=1):
            if character not in CODE39_VALUES:
                msg = (
                    "Code 39 base mode only supports the 43-character set; "
                    f"unsupported character at position {index}: {character!r}"
                )
                raise InvalidInputError(msg)

    def _validate_full_ascii_text(self, data: str) -> None:
        """Reject characters outside ASCII code points 0-127 (NF-1/NF-6)."""
        for index, character in enumerate(data, start=1):
            if ord(character) > _CODE39_ASCII_MAX_CODE:
                msg = (
                    "Code 39 Full-ASCII mode only supports ASCII code points 0 "
                    f"through 127; unsupported character at position {index}: {character!r}"
                )
                raise InvalidInputError(msg)
