"""QR format-information and version-information bit strings with BCH self-check.

Computes the 15-bit format-information strings (EC level + mask, BCH(15,5), masked) and the
18-bit version-information strings (version number, BCH(18,6)) for QR Code symbols, and
self-checks the derived strings against the normative tables at import time — mirroring
the derive-and-assert pattern used by ``galois.py``.

References: ISO/IEC 18004 §7.9 / Table C.1 (format-information strings) and
§7.10 / Table D.1 (version-information strings).
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Format information — (15-bit strings, BCH(15,5))
# ---------------------------------------------------------------------------

# EC-level 2-bit indicators: L = 01, M = 00, Q = 11, H = 10.
_EC_INDICATOR: Final[dict[str, int]] = {"L": 0b01, "M": 0b00, "Q": 0b11, "H": 0b10}

# BCH(15,5) generator (degree 10) and the format-information mask constant.
_FORMAT_BCH_GENERATOR: Final[int] = 0b10100110111
_FORMAT_MASK: Final[int] = 0b101010000010010


def _bch_remainder(data: int, generator: int, degree: int) -> int:
    """Return the ``degree``-bit BCH remainder of ``data`` against ``generator``.

    Standard polynomial long division over GF(2): shift ``data`` up by ``degree`` bits, then
    repeatedly XOR ``generator`` aligned to the value's highest set bit while its bit length
    exceeds ``degree``. The leftover ``degree``-bit value is the remainder.
    """
    value = data << degree
    while value.bit_length() > degree:
        value ^= generator << (value.bit_length() - generator.bit_length())
    return value


def format_info(ecc_letter: str, mask: int) -> str:
    """Return the 15-char MSB-first format-information bit string for ``ecc_letter``/``mask``.

    ``ecc_letter`` is one of ``"L"/"M"/"Q"/"H"``; ``mask`` is 0..7.
    """
    data = (_EC_INDICATOR[ecc_letter] << 3) | mask  # 5 data bits: 2-bit EC + 3-bit mask.
    remainder = _bch_remainder(data, _FORMAT_BCH_GENERATOR, 10)
    codeword = ((data << 10) | remainder) ^ _FORMAT_MASK
    return format(codeword, "015b")


# format-information strings, keyed by (ecc_letter, mask), transcribed verbatim.
# fmt: off
FORMAT_INFO: Final[dict[tuple[str, int], str]] = {
    ("L", 0): "111011111000100",
    ("L", 1): "111001011110011",
    ("L", 2): "111110110101010",
    ("L", 3): "111100010011101",
    ("L", 4): "110011000101111",
    ("L", 5): "110001100011000",
    ("L", 6): "110110001000001",
    ("L", 7): "110100101110110",
    ("M", 0): "101010000010010",
    ("M", 1): "101000100100101",
    ("M", 2): "101111001111100",
    ("M", 3): "101101101001011",
    ("M", 4): "100010111111001",
    ("M", 5): "100000011001110",
    ("M", 6): "100111110010111",
    ("M", 7): "100101010100000",
    ("Q", 0): "011010101011111",
    ("Q", 1): "011000001101000",
    ("Q", 2): "011111100110001",
    ("Q", 3): "011101000000110",
    ("Q", 4): "010010010110100",
    ("Q", 5): "010000110000011",
    ("Q", 6): "010111011011010",
    ("Q", 7): "010101111101101",
    ("H", 0): "001011010001001",
    ("H", 1): "001001110111110",
    ("H", 2): "001110011100111",
    ("H", 3): "001100111010000",
    ("H", 4): "000011101100010",
    ("H", 5): "000001001010101",
    ("H", 6): "000110100001100",
    ("H", 7): "000100000111011",
}
# fmt: on


# Design invariant: derive AND assert equal to . Runs at import.
for _ecc, _mask in FORMAT_INFO:
    assert format_info(_ecc, _mask) == FORMAT_INFO[(_ecc, _mask)], (
        f"format_info({_ecc!r}, {_mask}) does not match table"
    )
del _ecc, _mask


# ---------------------------------------------------------------------------
# Version information — (18-bit strings, BCH(18,6), versions 7–40)
# ---------------------------------------------------------------------------

# BCH(18,6) generator (degree 12) for version information.
_VERSION_BCH_GENERATOR: Final[int] = 0b1111100100101


def version_info(version: int) -> str | None:
    """Return the 18-char MSB-first version-information bit string for ``version`` (7–40).

    Versions 1–6 carry no version information; return ``None`` for them.
    """
    if version < 7:
        return None
    remainder = _bch_remainder(version, _VERSION_BCH_GENERATOR, 12)
    codeword = (version << 12) | remainder
    return format(codeword, "018b")


# version-information strings, keyed by version (7–40), transcribed verbatim.
# fmt: off
VERSION_INFO: Final[dict[int, str]] = {
    7: "000111110010010100",
    8: "001000010110111100",
    9: "001001101010011001",
    10: "001010010011010011",
    11: "001011101111110110",
    12: "001100011101100010",
    13: "001101100001000111",
    14: "001110011000001101",
    15: "001111100100101000",
    16: "010000101101111000",
    17: "010001010001011101",
    18: "010010101000010111",
    19: "010011010100110010",
    20: "010100100110100110",
    21: "010101011010000011",
    22: "010110100011001001",
    23: "010111011111101100",
    24: "011000111011000100",
    25: "011001000111100001",
    26: "011010111110101011",
    27: "011011000010001110",
    28: "011100110000011010",
    29: "011101001100111111",
    30: "011110110101110101",
    31: "011111001001010000",
    32: "100000100111010101",
    33: "100001011011110000",
    34: "100010100010111010",
    35: "100011011110011111",
    36: "100100101100001011",
    37: "100101010000101110",
    38: "100110101001100100",
    39: "100111010101000001",
    40: "101000110001101001",
}
# fmt: on


# Design invariant: derive AND assert equal to . Runs at import.
for _version in VERSION_INFO:
    assert version_info(_version) == VERSION_INFO[_version], f"version_info({_version}) does not match table"
del _version
