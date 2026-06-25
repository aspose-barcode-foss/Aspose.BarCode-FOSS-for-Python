"""Reed-Solomon error-correction encoding over GF(256) for QR Code.

Implements the validated high-to-low (leading-coefficient-first) polynomial
division algorithm. The coefficient ordering must NOT be inverted — that is the
classic RS bug.

References: ISO/IEC 18004 (RS Annex I anchor and
polynomial-division algorithm).
"""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.galois import gmul, rs_generator_poly


def rs_encode(data_codewords: list[int], ec_count: int) -> list[int]:
    """Return the ec_count Reed-Solomon error-correction codewords for the data."""
    g = rs_generator_poly(ec_count)
    res = list(data_codewords) + [0] * ec_count
    for i in range(len(data_codewords)):
        coef = res[i]
        if coef != 0:
            for j in range(len(g)):
                res[i + j] ^= gmul(g[j], coef)
    return res[len(data_codewords) :]
