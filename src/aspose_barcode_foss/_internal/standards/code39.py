"""Code 39 (ISO/IEC 16388:2017) standards lookup tables and helpers."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

# Start/stop frame character. Frames every symbol; never part of data; never
# assigned a check value; never shown in human-readable text (NF-1).
START_STOP: Final = "*"

# Wide element = 3 modules, narrow element = 1 module (NF-3/NF-7).
WIDE_NARROW_RATIO: Final = 3

# One narrow-space (1X) gap separates adjacent characters (NF-3/NF-7).
INTER_CHARACTER_GAP_MODULES: Final = 1

# Canonical value order of the 43 base characters (NF-1). Position == mod-43 value.
_CODE39_ALPHABET: Final = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%"

# Source: ISO/IEC 16388:2017 §4.1, Table 1 (NF-1/NF-2 "Value" column).
CODE39_VALUES: Final[Mapping[str, int]] = MappingProxyType({char: value for value, char in enumerate(_CODE39_ALPHABET)})

# 9-bit wide/narrow patterns: 1=wide, 0=narrow; element order is
# bar,space,bar,space,bar,space,bar,space,bar. Exactly three of nine are wide.
# Source: ISO/IEC 16388:2017 §4.3.2, Table 1 (NF-2 "9-bit (1=wide)" column).
CODE39_PATTERNS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "0": "000110100",
        "1": "100100001",
        "2": "001100001",
        "3": "101100000",
        "4": "000110001",
        "5": "100110000",
        "6": "001110000",
        "7": "000100101",
        "8": "100100100",
        "9": "001100100",
        "A": "100001001",
        "B": "001001001",
        "C": "101001000",
        "D": "000011001",
        "E": "100011000",
        "F": "001011000",
        "G": "000001101",
        "H": "100001100",
        "I": "001001100",
        "J": "000011100",
        "K": "100000011",
        "L": "001000011",
        "M": "101000010",
        "N": "000010011",
        "O": "100010010",
        "P": "001010010",
        "Q": "000000111",
        "R": "100000110",
        "S": "001000110",
        "T": "000010110",
        "U": "110000001",
        "V": "011000001",
        "W": "111000000",
        "X": "010010001",
        "Y": "110010000",
        "Z": "011010000",
        "-": "010000101",
        ".": "110000100",
        " ": "011000100",
        "$": "010101000",
        "/": "010100010",
        "+": "010001010",
        "%": "000101010",
        "*": "010010100",  # start/stop, no value
    }
)

# Full-ASCII (Extended) mapping: each ASCII code point 0–127 to its 1- or
# 2-character base Code 39 sequence. The 43 base chars that map to themselves
# are digits 0–9, uppercase A–Z, space, '-', and '.'; all others are two-char
# shift sequences using '$', '%', '+', '/'.
# Source: ISO/IEC 16388:2017 Annex A.3.1, Table A.2 (NF-5).
FULL_ASCII_MAP: Final[Mapping[str, str]] = MappingProxyType(
    {
        chr(0): "%U",
        chr(1): "$A",
        chr(2): "$B",
        chr(3): "$C",
        chr(4): "$D",
        chr(5): "$E",
        chr(6): "$F",
        chr(7): "$G",
        chr(8): "$H",
        chr(9): "$I",
        chr(10): "$J",
        chr(11): "$K",
        chr(12): "$L",
        chr(13): "$M",
        chr(14): "$N",
        chr(15): "$O",
        chr(16): "$P",
        chr(17): "$Q",
        chr(18): "$R",
        chr(19): "$S",
        chr(20): "$T",
        chr(21): "$U",
        chr(22): "$V",
        chr(23): "$W",
        chr(24): "$X",
        chr(25): "$Y",
        chr(26): "$Z",
        chr(27): "%A",
        chr(28): "%B",
        chr(29): "%C",
        chr(30): "%D",
        chr(31): "%E",
        " ": " ",
        "!": "/A",
        '"': "/B",
        "#": "/C",
        "$": "/D",
        "%": "/E",
        "&": "/F",
        "'": "/G",
        "(": "/H",
        ")": "/I",
        "*": "/J",
        "+": "/K",
        ",": "/L",
        "-": "-",
        ".": ".",
        "/": "/O",
        "0": "0",
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        ":": "/Z",
        ";": "%F",
        "<": "%G",
        "=": "%H",
        ">": "%I",
        "?": "%J",
        "@": "%V",
        "A": "A",
        "B": "B",
        "C": "C",
        "D": "D",
        "E": "E",
        "F": "F",
        "G": "G",
        "H": "H",
        "I": "I",
        "J": "J",
        "K": "K",
        "L": "L",
        "M": "M",
        "N": "N",
        "O": "O",
        "P": "P",
        "Q": "Q",
        "R": "R",
        "S": "S",
        "T": "T",
        "U": "U",
        "V": "V",
        "W": "W",
        "X": "X",
        "Y": "Y",
        "Z": "Z",
        "[": "%K",
        "\\": "%L",
        "]": "%M",
        "^": "%N",
        "_": "%O",
        "`": "%W",
        "a": "+A",
        "b": "+B",
        "c": "+C",
        "d": "+D",
        "e": "+E",
        "f": "+F",
        "g": "+G",
        "h": "+H",
        "i": "+I",
        "j": "+J",
        "k": "+K",
        "l": "+L",
        "m": "+M",
        "n": "+N",
        "o": "+O",
        "p": "+P",
        "q": "+Q",
        "r": "+R",
        "s": "+S",
        "t": "+T",
        "u": "+U",
        "v": "+V",
        "w": "+W",
        "x": "+X",
        "y": "+Y",
        "z": "+Z",
        "{": "%P",
        "|": "%Q",
        "}": "%R",
        "~": "%S",
        chr(127): "%T",
    }
)

# Reverse map from value (0–42) to its base character, built once at load.
_VALUE_TO_CHAR: Final[Mapping[int, str]] = MappingProxyType({value: char for char, value in CODE39_VALUES.items()})


def get_code39_pattern(char: str) -> str:
    """Return the 9-bit wide/narrow pattern for a base character or '*'."""
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError(f"unsupported Code 39 character: {char!r}")
    try:
        return CODE39_PATTERNS[char]
    except KeyError as exc:
        raise ValueError(f"unsupported Code 39 character: {char!r}") from exc


def get_code39_value(char: str) -> int:
    """Return the modulo-43 value (0–42) for a base character.

    The start/stop character '*' has no value and raises ValueError.
    """
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError(f"unsupported Code 39 character: {char!r}")
    try:
        return CODE39_VALUES[char]
    except KeyError as exc:
        raise ValueError(f"unsupported Code 39 character: {char!r}") from exc


def expand_full_ascii(text: str) -> str:
    """Expand *text* into a base Code 39 sequence via the Full-ASCII map.

    Raises ValueError for any character whose code point exceeds 127.
    """
    parts: list[str] = []
    for i, char in enumerate(text):
        if ord(char) > 127:
            raise ValueError(f"non-ASCII character at position {i}: {char!r}")
        parts.append(FULL_ASCII_MAP[char])
    return "".join(parts)


def code39_checksum(base_chars: str) -> int:
    """Return the modulo-43 check value over a base-character string (NF-4)."""
    return sum(get_code39_value(char) for char in base_chars) % 43


def checksum_char(value: int) -> str:
    """Return the base character whose modulo-43 value equals *value* (0–42)."""
    if not isinstance(value, int) or isinstance(value, bool) or value not in _VALUE_TO_CHAR:
        raise ValueError(f"check value must be an integer in 0–42, got {value!r}")
    return _VALUE_TO_CHAR[value]


__all__ = [
    "CODE39_PATTERNS",
    "CODE39_VALUES",
    "FULL_ASCII_MAP",
    "INTER_CHARACTER_GAP_MODULES",
    "START_STOP",
    "WIDE_NARROW_RATIO",
    "checksum_char",
    "code39_checksum",
    "expand_full_ascii",
    "get_code39_pattern",
    "get_code39_value",
]
