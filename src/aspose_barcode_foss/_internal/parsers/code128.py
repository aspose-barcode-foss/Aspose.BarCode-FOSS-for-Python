"""Code 128 input parser."""

from __future__ import annotations

from numbers import Integral
from typing import Final

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import (
    Code128EncodeMode,
    Code128Options,
    EncodeOptions,
)
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.standards.code128 import (
    CODE128_CODE_SET_B,
    FNC1_SENTINEL,
    FNC2_SENTINEL,
    FNC3_SENTINEL,
    FNC4_SENTINEL,
)

_CODE128_ASCII_MAX_CODE_A = 95
_CODE128_ASCII_MAX_CODE_AB = 126
_CODE128_FNC_SENTINELS: Final = frozenset((FNC1_SENTINEL, FNC2_SENTINEL, FNC3_SENTINEL, FNC4_SENTINEL))


class Code128InputParser(InputParser):
    """Validate and normalize Code 128 input."""

    def parse(
        self,
        data: str | bytes,
        *,
        options: Code128Options | EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce a Code 128 payload."""
        normalized_options = self._coerce_options(options)

        if isinstance(data, bytes):
            msg = "Code 128 does not support bytes input"
            raise UnsupportedCapabilityError(msg)
        if not isinstance(data, str):
            msg = "Code 128 data must be a text string"
            raise InvalidInputError(msg)

        self._validate_capabilities(normalized_options)
        self._validate_text(data, normalized_options.encode_mode)

        return NormalizedPayload(
            symbology="code128",
            data=data,
            input_kind="text",
            code128_encode_mode=normalized_options.encode_mode,
        )

    def _coerce_options(
        self,
        options: Code128Options | EncodeOptions | None,
    ) -> Code128Options:
        """Normalize supported option containers into Code128Options."""
        if options is None:
            return Code128Options()
        if isinstance(options, Code128Options):
            return self._build_options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                encode_mode=options.encode_mode,
            )
        if isinstance(options, EncodeOptions):
            return self._build_options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                encode_mode=Code128EncodeMode.AUTO,
            )

        msg = "encode options must be Code128Options, EncodeOptions, or None"
        raise InvalidInputError(msg)

    def _build_options(
        self,
        *,
        gs1_enabled: object,
        eci_assignment_number: object,
        encode_mode: object,
    ) -> Code128Options:
        """Validate option value types before capability checks run."""
        return Code128Options(
            gs1_enabled=self._normalize_gs1_enabled(gs1_enabled),
            eci_assignment_number=self._normalize_eci_assignment_number(eci_assignment_number),
            encode_mode=self._normalize_encode_mode(encode_mode),
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

    def _normalize_encode_mode(self, value: object) -> Code128EncodeMode:
        """Validate the typed Code 128 encode-mode request."""
        if not isinstance(value, Code128EncodeMode):
            msg = "encode_mode must be a Code128EncodeMode value"
            raise InvalidInputError(msg)
        return value

    def _validate_capabilities(self, options: Code128Options) -> None:
        """Reject capability requests that are still unsupported."""
        if options.gs1_enabled is True:
            msg = "Code 128 does not support GS1"
            raise UnsupportedCapabilityError(msg)
        if options.eci_assignment_number is not None:
            msg = "Code 128 does not support ECI"
            raise UnsupportedCapabilityError(msg)

    def _validate_text(self, data: str, mode: Code128EncodeMode) -> None:
        """Reject text that the requested Code 128 mode cannot represent."""
        if not data:
            msg = "Code 128 text must not be empty"
            raise InvalidInputError(msg)

        if mode is Code128EncodeMode.CODE_C:
            self._validate_code_c_text(data)
            return
        if mode in (Code128EncodeMode.CODE_A, Code128EncodeMode.CODE_AC):
            self._validate_ascii_range_text(
                data,
                maximum_ordinal=_CODE128_ASCII_MAX_CODE_A,
                mode=mode,
            )
            return
        if mode in (Code128EncodeMode.CODE_B, Code128EncodeMode.CODE_BC):
            self._validate_code_b_text(data, mode=mode)
            return
        if mode in (Code128EncodeMode.AUTO, Code128EncodeMode.CODE_AB):
            self._validate_ascii_range_text(
                data,
                maximum_ordinal=_CODE128_ASCII_MAX_CODE_AB,
                mode=mode,
            )
            return

        msg = f"unsupported Code 128 encode_mode: {mode!r}"
        raise InvalidInputError(msg)

    def _validate_code_b_text(self, data: str, *, mode: Code128EncodeMode) -> None:
        """Reject characters outside printable Code Set B."""
        for index, character in enumerate(data, start=1):
            if character in _CODE128_FNC_SENTINELS:
                continue  # FNC sentinels are valid in Code Set B
            if character not in CODE128_CODE_SET_B:
                msg = (
                    f"Code 128 encode_mode {mode.name} only supports printable "
                    "Code Set B characters; unsupported character at position "
                    f"{index}: "
                    f"{character!r}"
                )
                raise InvalidInputError(msg)

    def _validate_ascii_range_text(
        self,
        data: str,
        *,
        maximum_ordinal: int,
        mode: Code128EncodeMode,
    ) -> None:
        """Reject characters outside the ASCII range allowed by the mode."""
        for index, character in enumerate(data, start=1):
            if character in _CODE128_FNC_SENTINELS:
                continue  # FNC sentinels are valid in all A/AB/AC/AUTO modes
            if ord(character) > maximum_ordinal:
                msg = (
                    f"Code 128 encode_mode {mode.name} only supports ASCII code "
                    f"points 0 through {maximum_ordinal}; unsupported character "
                    f"at position {index}: {character!r}"
                )
                raise InvalidInputError(msg)

    def _validate_code_c_text(self, data: str) -> None:
        """Reject Code C text that is not an even-length digit string."""
        if not data.isdigit() or len(data) % 2 != 0:
            msg = "Code 128 encode_mode CODE_C requires an even-length digit string"
            raise InvalidInputError(msg)
