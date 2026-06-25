"""QR Code standards package: GF(256)/Reed-Solomon, tables, alignment, info-strings, bitstream."""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.alignment import alignment_centers
from aspose_barcode_foss._internal.standards.qr.bitstream import build_data_codewords
from aspose_barcode_foss._internal.standards.qr.galois import gmul, rs_generator_poly
from aspose_barcode_foss._internal.standards.qr.info_strings import format_info, version_info
from aspose_barcode_foss._internal.standards.qr.masking import (
    MASK_PREDICATES,
    apply_mask,
    penalty,
    select_best_mask,
)
from aspose_barcode_foss._internal.standards.qr.matrix import (
    assemble,
    build_function_patterns,
    place_data,
    write_format_info,
    write_version_info,
)
from aspose_barcode_foss._internal.standards.qr.reed_solomon import rs_encode
from aspose_barcode_foss._internal.standards.qr.segmentation import (
    encoding_bit_length,
    forced_segments,
    segment_optimal,
    segments_bit_length,
)
from aspose_barcode_foss._internal.standards.qr.segments import QrMode, Segment
from aspose_barcode_foss._internal.standards.qr.tables import (
    block_structure,
    byte_count_bits,
    data_codewords,
    ec_per_block,
    remainder_bits,
    symbol_size,
    total_codewords,
)

__all__ = [
    "MASK_PREDICATES",
    "QrMode",
    "Segment",
    "alignment_centers",
    "apply_mask",
    "assemble",
    "block_structure",
    "build_data_codewords",
    "build_function_patterns",
    "byte_count_bits",
    "data_codewords",
    "ec_per_block",
    "encoding_bit_length",
    "forced_segments",
    "format_info",
    "gmul",
    "penalty",
    "place_data",
    "remainder_bits",
    "rs_encode",
    "rs_generator_poly",
    "segment_optimal",
    "segments_bit_length",
    "select_best_mask",
    "symbol_size",
    "total_codewords",
    "version_info",
    "write_format_info",
    "write_version_info",
]
