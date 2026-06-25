"""QR Code input parser."""

from __future__ import annotations

from numbers import Integral

from aspose_barcode_foss._internal.exceptions import InvalidInputError, UnsupportedCapabilityError
from aspose_barcode_foss._internal.models.options import (
    EncodeOptions,
    QrEncodeMode,
    QrErrorCorrectionLevel,
    QrOptions,
)
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.standards.qr import QrMode, data_codewords, encoding_bit_length
from aspose_barcode_foss._internal.standards.qr.segments import (
    is_alphanumeric,
    is_numeric,
    shift_jis_double_byte,
)

_QR_BYTE_MODE_MAX_CODE = 255
_QR_MIN_VERSION = 1
_QR_MAX_VERSION = 40
_QR_MIN_MASK = 0
_QR_MAX_MASK = 7
_QR_MIN_ECI = 0
_QR_MAX_ECI = 999999

_EC_LEVELS: dict[str, QrErrorCorrectionLevel] = {
    "L": QrErrorCorrectionLevel.L,
    "M": QrErrorCorrectionLevel.M,
    "Q": QrErrorCorrectionLevel.Q,
    "H": QrErrorCorrectionLevel.H,
}

_ENCODE_MODES: dict[str, QrEncodeMode] = {
    "auto": QrEncodeMode.AUTO,
    "numeric": QrEncodeMode.NUMERIC,
    "alphanumeric": QrEncodeMode.ALPHANUMERIC,
    "byte": QrEncodeMode.BYTE,
    "kanji": QrEncodeMode.KANJI,
}


class QrInputParser(InputParser):
    """Validate and normalize QR Code input."""

    def __init__(self, *, symbology_name: str = "qr") -> None:
        """Store the emitted symbology name."""
        self._symbology_name = symbology_name

    def parse(
        self,
        data: str | bytes,
        *,
        options: QrOptions | EncodeOptions | None = None,
    ) -> NormalizedPayload:
        """Validate public input and produce a QR payload."""
        normalized_options = self._coerce_options(options)

        if isinstance(data, bytes):
            msg = "QR accepts text only"
            raise UnsupportedCapabilityError(msg)
        if not isinstance(data, str):
            msg = "QR data must be a text string"
            raise InvalidInputError(msg)

        self._validate_capabilities(normalized_options)

        if not data:
            msg = "QR input text must not be empty"
            raise InvalidInputError(msg)

        mode = self._normalize_encoding_mode(normalized_options.encoding_mode)
        eci = normalized_options.eci_assignment_number

        if mode in (QrEncodeMode.BYTE, QrEncodeMode.AUTO):
            self._validate_byte_mode_text(data)

        self._validate_forced_mode(data, mode)
        self._validate_eci_mode_combination(mode, eci)

        error_correction_level = normalized_options.error_correction_level
        ec_letter = error_correction_level.name
        version = self._resolve_version(
            data,
            ec_letter,
            normalized_options.version,
            mode,
            eci,
        )

        return NormalizedPayload(
            symbology=self._symbology_name,
            data=data,
            input_kind="text",
            qr_error_correction_level=error_correction_level,
            qr_version=version,
            qr_mask=normalized_options.mask,
            qr_encoding_mode=mode,
            qr_eci_assignment_number=eci,
        )

    def _coerce_options(
        self,
        options: QrOptions | EncodeOptions | None,
    ) -> QrOptions:
        """Normalize supported option containers into a resolved QrOptions."""
        if options is None:
            return self._build_options(
                gs1_enabled=None,
                eci_assignment_number=None,
                error_correction_level=None,
                version=None,
                mask=None,
                encoding_mode=None,
            )
        if isinstance(options, QrOptions):
            return self._build_options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                error_correction_level=options.error_correction_level,
                version=options.version,
                mask=options.mask,
                encoding_mode=options.encoding_mode,
            )
        if isinstance(options, EncodeOptions):
            return self._build_options(
                gs1_enabled=options.gs1_enabled,
                eci_assignment_number=options.eci_assignment_number,
                error_correction_level=None,
                version=None,
                mask=None,
                encoding_mode=None,
            )

        msg = "encode options must be QrOptions, EncodeOptions, or None"
        raise InvalidInputError(msg)

    def _build_options(
        self,
        *,
        gs1_enabled: object,
        eci_assignment_number: object,
        error_correction_level: object,
        version: object,
        mask: object,
        encoding_mode: object,
    ) -> QrOptions:
        """Validate option value types before capability checks run."""
        return QrOptions(
            gs1_enabled=self._normalize_gs1_enabled(gs1_enabled),
            eci_assignment_number=self._normalize_eci_assignment_number(eci_assignment_number),
            error_correction_level=self._normalize_error_correction_level(error_correction_level),
            version=self._normalize_version(version),
            mask=self._normalize_mask(mask),
            encoding_mode=encoding_mode,
        )

    def _normalize_gs1_enabled(self, value: object) -> bool | None:
        """Validate the GS1 flag shape."""
        if value is None or type(value) is bool:
            return value

        msg = "gs1_enabled must be a boolean"
        raise InvalidInputError(msg)

    def _normalize_eci_assignment_number(self, value: object) -> int | None:
        """Validate the optional ECI assignment number shape and range."""
        if value is None:
            return None
        if not isinstance(value, Integral) or isinstance(value, bool):
            msg = "eci_assignment_number must be an integer"
            raise InvalidInputError(msg)
        number = int(value)
        if not (_QR_MIN_ECI <= number <= _QR_MAX_ECI):
            msg = f"eci_assignment_number must be between {_QR_MIN_ECI} and {_QR_MAX_ECI}"
            raise InvalidInputError(msg)
        return number

    def _normalize_error_correction_level(self, value: object) -> QrErrorCorrectionLevel:
        """Resolve the error correction level to a concrete enum (default M)."""
        if value is None:
            return QrErrorCorrectionLevel.M
        if isinstance(value, QrErrorCorrectionLevel):
            return value
        if isinstance(value, str):
            letter = value.upper()
            if letter in _EC_LEVELS:
                return _EC_LEVELS[letter]
            msg = "error_correction_level must be one of 'L', 'M', 'Q', 'H'"
            raise InvalidInputError(msg)

        msg = "error_correction_level must be a QrErrorCorrectionLevel, str, or None"
        raise InvalidInputError(msg)

    def _normalize_version(self, value: object) -> int | None:
        """Validate the optional forced version (1-40, rejecting bool)."""
        if value is None:
            return None
        if not isinstance(value, Integral) or isinstance(value, bool):
            msg = "version must be an integer"
            raise InvalidInputError(msg)
        version = int(value)
        if not (_QR_MIN_VERSION <= version <= _QR_MAX_VERSION):
            msg = f"version must be between {_QR_MIN_VERSION} and {_QR_MAX_VERSION}"
            raise InvalidInputError(msg)
        return version

    def _normalize_mask(self, value: object) -> int | None:
        """Validate the optional forced mask (0-7, rejecting bool)."""
        if value is None:
            return None
        if not isinstance(value, Integral) or isinstance(value, bool):
            msg = "mask must be an integer"
            raise InvalidInputError(msg)
        mask = int(value)
        if not (_QR_MIN_MASK <= mask <= _QR_MAX_MASK):
            msg = f"mask must be between {_QR_MIN_MASK} and {_QR_MAX_MASK}"
            raise InvalidInputError(msg)
        return mask

    def _normalize_encoding_mode(self, value: object) -> QrEncodeMode:
        """Resolve the optional encoding mode to a concrete enum (default AUTO)."""
        if value is None:
            return QrEncodeMode.AUTO
        if isinstance(value, QrEncodeMode):
            return value
        if isinstance(value, str):
            name = value.lower()
            if name in _ENCODE_MODES:
                return _ENCODE_MODES[name]
            msg = "encoding_mode must be one of 'auto', 'numeric', 'alphanumeric', 'byte', 'kanji'"
            raise InvalidInputError(msg)

        msg = "encoding_mode must be a QrEncodeMode, str, or None"
        raise InvalidInputError(msg)

    def _validate_capabilities(self, options: QrOptions) -> None:
        """Reject capability requests that QR Code does not support."""
        if options.gs1_enabled is True:
            msg = "QR Code does not support GS1"
            raise UnsupportedCapabilityError(msg)

    def _validate_byte_mode_text(self, data: str) -> None:
        """Reject characters outside Latin-1 code points 0-255."""
        for index, character in enumerate(data, start=1):
            if ord(character) > _QR_BYTE_MODE_MAX_CODE:
                msg = (
                    "QR byte mode only supports Latin-1 code points 0 through 255; "
                    f"code point > 255 not representable in byte mode at position {index}: {character!r}"
                )
                raise InvalidInputError(msg)

    def _validate_forced_mode(self, data: str, mode: QrEncodeMode) -> None:
        """Verify every character is representable in a forced explicit mode.

        BYTE and AUTO are gated by ``_validate_byte_mode_text`` in ``parse`` instead.
        ``QrMode[mode.name]`` mirrors the encoder's forced-segment mapping, but the
        per-character predicates give clearer positional messages.
        """
        if mode in (QrEncodeMode.BYTE, QrEncodeMode.AUTO):
            return

        qr_mode = QrMode[mode.name]

        if qr_mode is QrMode.NUMERIC:
            for index, character in enumerate(data, start=1):
                if not is_numeric(character):
                    msg = (
                        "QR numeric mode only supports digits 0 through 9; "
                        f"non-digit at position {index}: {character!r}"
                    )
                    raise InvalidInputError(msg)
            return

        if qr_mode is QrMode.ALPHANUMERIC:
            for index, character in enumerate(data, start=1):
                if not is_alphanumeric(character):
                    msg = (
                        "QR alphanumeric mode only supports the 45-character set "
                        "(0-9 A-Z space $ % * + - . / :); "
                        f"unsupported character at position {index}: {character!r}"
                    )
                    raise InvalidInputError(msg)
            return

        if qr_mode is QrMode.KANJI:
            for index, character in enumerate(data, start=1):
                if shift_jis_double_byte(character) is None:
                    msg = (
                        "QR Kanji mode only supports Shift-JIS double-byte characters; "
                        f"unsupported character at position {index}: {character!r}"
                    )
                    raise InvalidInputError(msg)
            return

    def _validate_eci_mode_combination(self, mode: QrEncodeMode, eci: int | None) -> None:
        """Reject ECI combined with a forced non-byte mode."""
        if eci is None:
            return
        if mode in (QrEncodeMode.NUMERIC, QrEncodeMode.ALPHANUMERIC, QrEncodeMode.KANJI):
            msg = (
                "ECI is only supported with byte or auto encoding modes; "
                f"it has no defined effect on {mode.name.lower()} mode"
            )
            raise InvalidInputError(msg)

    def _resolve_version(
        self,
        text: str,
        ec_letter: str,
        forced_version: int | None,
        mode: QrEncodeMode,
        eci: int | None,
    ) -> int:
        """Select the smallest fitting version, or validate the forced version's capacity."""
        if forced_version is None:
            for candidate in range(_QR_MIN_VERSION, _QR_MAX_VERSION + 1):
                if data_codewords(candidate, ec_letter) * 8 >= encoding_bit_length(text, candidate, mode, eci):
                    return candidate
            msg = f"data too large for QR at EC level {ec_letter}"
            raise InvalidInputError(msg)

        if data_codewords(forced_version, ec_letter) * 8 < encoding_bit_length(text, forced_version, mode, eci):
            msg = f"data too large for forced version {forced_version} at EC level {ec_letter}"
            raise InvalidInputError(msg)
        return forced_version
