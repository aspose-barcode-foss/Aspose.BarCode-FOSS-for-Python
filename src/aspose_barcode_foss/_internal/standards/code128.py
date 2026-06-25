"""Code 128 standards lookup tables and helpers."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

FNC_3: Final = 96
FNC_2: Final = 97
SHIFT: Final = 98
CODE_C: Final = 99
CODE_B: Final = 100
CODE_A: Final = 101
FNC_4_B: Final = CODE_B
FNC_4_A: Final = CODE_A
FNC_1: Final = 102
START_A: Final = 103
START_B: Final = 104
START_C: Final = 105
STOP: Final = 106

# FNC sentinel characters — Private Use Area code points embedded in str input
# to represent FNC1–FNC4 tokens. These code points (U+F001–U+F004) are
# guaranteed never to appear in normal data.
FNC1_SENTINEL: Final = "\uf001"
FNC2_SENTINEL: Final = "\uf002"
FNC3_SENTINEL: Final = "\uf003"
FNC4_SENTINEL: Final = "\uf004"

CODE128_CODE_SET_B: Final[Mapping[str, int]] = MappingProxyType(
    {
        " ": 0,
        "!": 1,
        '"': 2,
        "#": 3,
        "$": 4,
        "%": 5,
        "&": 6,
        "'": 7,
        "(": 8,
        ")": 9,
        "*": 10,
        "+": 11,
        ",": 12,
        "-": 13,
        ".": 14,
        "/": 15,
        "0": 16,
        "1": 17,
        "2": 18,
        "3": 19,
        "4": 20,
        "5": 21,
        "6": 22,
        "7": 23,
        "8": 24,
        "9": 25,
        ":": 26,
        ";": 27,
        "<": 28,
        "=": 29,
        ">": 30,
        "?": 31,
        "@": 32,
        "A": 33,
        "B": 34,
        "C": 35,
        "D": 36,
        "E": 37,
        "F": 38,
        "G": 39,
        "H": 40,
        "I": 41,
        "J": 42,
        "K": 43,
        "L": 44,
        "M": 45,
        "N": 46,
        "O": 47,
        "P": 48,
        "Q": 49,
        "R": 50,
        "S": 51,
        "T": 52,
        "U": 53,
        "V": 54,
        "W": 55,
        "X": 56,
        "Y": 57,
        "Z": 58,
        "[": 59,
        "\\": 60,
        "]": 61,
        "^": 62,
        "_": 63,
        "`": 64,
        "a": 65,
        "b": 66,
        "c": 67,
        "d": 68,
        "e": 69,
        "f": 70,
        "g": 71,
        "h": 72,
        "i": 73,
        "j": 74,
        "k": 75,
        "l": 76,
        "m": 77,
        "n": 78,
        "o": 79,
        "p": 80,
        "q": 81,
        "r": 82,
        "s": 83,
        "t": 84,
        "u": 85,
        "v": 86,
        "w": 87,
        "x": 88,
        "y": 89,
        "z": 90,
        "{": 91,
        "|": 92,
        "}": 93,
        "~": 94,
    }
)

CODE128_CODE_SET_A: Final[Mapping[str, int]] = MappingProxyType(
    {
        "\x00": 64,  # NUL
        "\x01": 65,  # SOH
        "\x02": 66,  # STX
        "\x03": 67,  # ETX
        "\x04": 68,  # EOT
        "\x05": 69,  # ENQ
        "\x06": 70,  # ACK
        "\x07": 71,  # BEL
        "\x08": 72,  # BS
        "\x09": 73,  # HT
        "\x0a": 74,  # LF
        "\x0b": 75,  # VT
        "\x0c": 76,  # FF
        "\x0d": 77,  # CR
        "\x0e": 78,  # SO
        "\x0f": 79,  # SI
        "\x10": 80,  # DLE
        "\x11": 81,  # DC1
        "\x12": 82,  # DC2
        "\x13": 83,  # DC3
        "\x14": 84,  # DC4
        "\x15": 85,  # NAK
        "\x16": 86,  # SYN
        "\x17": 87,  # ETB
        "\x18": 88,  # CAN
        "\x19": 89,  # EM
        "\x1a": 90,  # SUB
        "\x1b": 91,  # ESC
        "\x1c": 92,  # FS
        "\x1d": 93,  # GS
        "\x1e": 94,  # RS
        "\x1f": 95,  # US
        " ": 0,
        "!": 1,
        '"': 2,
        "#": 3,
        "$": 4,
        "%": 5,
        "&": 6,
        "'": 7,
        "(": 8,
        ")": 9,
        "*": 10,
        "+": 11,
        ",": 12,
        "-": 13,
        ".": 14,
        "/": 15,
        "0": 16,
        "1": 17,
        "2": 18,
        "3": 19,
        "4": 20,
        "5": 21,
        "6": 22,
        "7": 23,
        "8": 24,
        "9": 25,
        ":": 26,
        ";": 27,
        "<": 28,
        "=": 29,
        ">": 30,
        "?": 31,
        "@": 32,
        "A": 33,
        "B": 34,
        "C": 35,
        "D": 36,
        "E": 37,
        "F": 38,
        "G": 39,
        "H": 40,
        "I": 41,
        "J": 42,
        "K": 43,
        "L": 44,
        "M": 45,
        "N": 46,
        "O": 47,
        "P": 48,
        "Q": 49,
        "R": 50,
        "S": 51,
        "T": 52,
        "U": 53,
        "V": 54,
        "W": 55,
        "X": 56,
        "Y": 57,
        "Z": 58,
        "[": 59,
        "\\": 60,
        "]": 61,
        "^": 62,
        "_": 63,
    }
)

# Module patterns indexed by codeword value.
CODE128_PATTERNS: Final[tuple[str, ...]] = (
    "11011001100",  # 0
    "11001101100",  # 1
    "11001100110",  # 2
    "10010011000",  # 3
    "10010001100",  # 4
    "10001001100",  # 5
    "10011001000",  # 6
    "10011000100",  # 7
    "10001100100",  # 8
    "11001001000",  # 9
    "11001000100",  # 10
    "11000100100",  # 11
    "10110011100",  # 12
    "10011011100",  # 13
    "10011001110",  # 14
    "10111001100",  # 15
    "10011101100",  # 16
    "10011100110",  # 17
    "11001110010",  # 18
    "11001011100",  # 19
    "11001001110",  # 20
    "11011100100",  # 21
    "11001110100",  # 22
    "11101101110",  # 23
    "11101001100",  # 24
    "11100101100",  # 25
    "11100100110",  # 26
    "11101100100",  # 27
    "11100110100",  # 28
    "11100110010",  # 29
    "11011011000",  # 30
    "11011000110",  # 31
    "11000110110",  # 32
    "10100011000",  # 33
    "10001011000",  # 34
    "10001000110",  # 35
    "10110001000",  # 36
    "10001101000",  # 37
    "10001100010",  # 38
    "11010001000",  # 39
    "11000101000",  # 40
    "11000100010",  # 41
    "10110111000",  # 42
    "10110001110",  # 43
    "10001101110",  # 44
    "10111011000",  # 45
    "10111000110",  # 46
    "10001110110",  # 47
    "11101110110",  # 48
    "11010001110",  # 49
    "11000101110",  # 50
    "11011101000",  # 51
    "11011100010",  # 52
    "11011101110",  # 53
    "11101011000",  # 54
    "11101000110",  # 55
    "11100010110",  # 56
    "11101101000",  # 57
    "11101100010",  # 58
    "11100011010",  # 59
    "11101111010",  # 60
    "11001000010",  # 61
    "11110001010",  # 62
    "10100110000",  # 63
    "10100001100",  # 64
    "10010110000",  # 65
    "10010000110",  # 66
    "10000101100",  # 67
    "10000100110",  # 68
    "10110010000",  # 69
    "10110000100",  # 70
    "10011010000",  # 71
    "10011000010",  # 72
    "10000110100",  # 73
    "10000110010",  # 74
    "11000010010",  # 75
    "11001010000",  # 76
    "11110111010",  # 77
    "11000010100",  # 78
    "10001111010",  # 79
    "10100111100",  # 80
    "10010111100",  # 81
    "10010011110",  # 82
    "10111100100",  # 83
    "10011110100",  # 84
    "10011110010",  # 85
    "11110100100",  # 86
    "11110010100",  # 87
    "11110010010",  # 88
    "11011011110",  # 89
    "11011110110",  # 90
    "11110110110",  # 91
    "10101111000",  # 92
    "10100011110",  # 93
    "10001011110",  # 94
    "10111101000",  # 95
    "10111100010",  # 96
    "11110101000",  # 97
    "11110100010",  # 98
    "10111011110",  # 99
    "10111101110",  # 100
    "11101011110",  # 101
    "11110101110",  # 102
    "11010000100",  # 103
    "11010010000",  # 104
    "11010011100",  # 105
    "1100011101011",  # 106
)


def get_code128_code_set_b_value(character: str) -> int:
    """Return the Code Set B codeword value for one printable character."""
    if not isinstance(character, str) or len(character) != 1:
        raise ValueError("character must be a single text character")

    try:
        return CODE128_CODE_SET_B[character]
    except KeyError as exc:
        raise ValueError(f"unsupported Code Set B character: {character!r}") from exc


def get_code128_code_set_c_value(pair: str) -> int:
    """Return the Code Set C codeword value for a two-digit pair.

    Input contract: exactly two ASCII digit characters ('0'–'9'),
    representing values 00–99. Returns int(pair) (range 0–99).
    Raises ValueError for non-two-digit input.
    """
    if not isinstance(pair, str) or len(pair) != 2 or not pair.isdigit():
        raise ValueError(f"Code Set C requires a two-digit pair: {pair!r}")
    return int(pair)


def get_code128_code_set_a_value(character: str) -> int:
    """Return the Code Set A codeword value for one character.

    Accepts ASCII 0–95 (control characters NUL–US and printable ASCII
    space through underscore). Raises ValueError for other input.
    """
    if not isinstance(character, str) or len(character) != 1:
        raise ValueError("character must be a single text character")
    try:
        return CODE128_CODE_SET_A[character]
    except KeyError as exc:
        raise ValueError(f"unsupported Code Set A character: {character!r}") from exc


def get_code128_pattern(codeword: int) -> str:
    """Return the module pattern for one Code 128 codeword value."""
    if not isinstance(codeword, int) or isinstance(codeword, bool):
        raise ValueError("codeword must be an integer")
    if codeword < 0 or codeword >= len(CODE128_PATTERNS):
        raise ValueError(f"unsupported Code 128 codeword: {codeword!r}")

    return CODE128_PATTERNS[codeword]


__all__ = [
    "CODE_A",
    "CODE_B",
    "CODE_C",
    "CODE128_CODE_SET_A",
    "CODE128_CODE_SET_B",
    "CODE128_PATTERNS",
    "FNC_1",
    "FNC_2",
    "FNC_3",
    "FNC_4_A",
    "FNC_4_B",
    "FNC1_SENTINEL",
    "FNC2_SENTINEL",
    "FNC3_SENTINEL",
    "FNC4_SENTINEL",
    "SHIFT",
    "START_A",
    "START_B",
    "START_C",
    "STOP",
    "get_code128_code_set_a_value",
    "get_code128_code_set_b_value",
    "get_code128_code_set_c_value",
    "get_code128_pattern",
]
