"""Normalized payload models produced by the parser layer."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from aspose_barcode_foss._internal.models.options import (
    Code128EncodeMode,
    Code39EncodeMode,
    QrEncodeMode,
    QrErrorCorrectionLevel,
)
from aspose_barcode_foss._internal.standards.eci import EciDesignator
from aspose_barcode_foss._internal.standards.gs1 import Gs1Message


InputKind = Literal["text", "binary"]


@dataclass(slots=True, frozen=True)
class NormalizedPayload:
    """Validated payload ready for the encoding layer."""

    symbology: str
    data: str | bytes
    input_kind: InputKind
    gs1_message: Gs1Message | None = None
    eci_designator: EciDesignator | None = None
    code128_encode_mode: Code128EncodeMode | None = None
    code39_encode_mode: Code39EncodeMode | None = None
    code39_add_check_digit: bool | None = None
    qr_error_correction_level: QrErrorCorrectionLevel | None = None
    qr_version: int | None = None
    qr_mask: int | None = None
    qr_encoding_mode: QrEncodeMode | None = None
    qr_eci_assignment_number: int | None = None
    metadata: Mapping[str, object] | None = None
