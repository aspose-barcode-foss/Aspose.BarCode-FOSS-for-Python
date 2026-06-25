"""Code 128 golden vectors used by encoding tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Code128Vector:
    """One known-good Code 128 fixture."""

    input_data: str
    expected_modules: tuple[str, ...]


CODE128_A = Code128Vector(
    input_data="A",
    expected_modules=(("1101001000010100011000100010110001100011101011"),),
)


CODE128_CODE_SET_B_GOLDEN_VECTORS = (
    Code128Vector(
        input_data="0",
        expected_modules=(("1101001000010011101100100111001101100011101011"),),
    ),
    Code128Vector(
        input_data="a",
        expected_modules=(("1101001000010010110000100100001101100011101011"),),
    ),
    Code128Vector(
        input_data="abcdfghij",
        expected_modules=(
            (
                "11010010000100101100001001000011010000101100100001001101011000010010011010000100110000101000011010010000110010100011001001100011101011"
            ),
        ),
    ),
    Code128Vector(
        input_data=",",
        expected_modules=(("1101001000010110011100100110111001100011101011"),),
    ),
    Code128Vector(
        input_data="!@#$%^&*()",
        expected_modules=(
            (
                "1101001000011001101100110001101101001001100010010001100100010011001111000101010011001000110010001001000110010011001001000110111010001100011101011"
            ),
        ),
    ),
    Code128Vector(
        input_data="a1.z2#",
        expected_modules=(
            ("11010010000100101100001001110011010011001110110111101101100111001010010011000101111010001100011101011"),
        ),
    ),
)


CODE128_REFERENCE_BEHAVIOR_GOLDEN_VECTORS = (
    Code128Vector(
        input_data="0123456789",
        expected_modules=(
            ("110100111001100110110011101101110101110110001000010110011011011110100001101001100011101011"),
        ),
    ),
)


CODE128_CODE_SET_C_GOLDEN_VECTORS: tuple[Code128Vector, ...] = (
    Code128Vector(
        input_data="00",
        expected_modules=("1101001110011011001100110011001101100011101011",),
    ),
    Code128Vector(
        input_data="0199",
        expected_modules=("110100111001100110110010111011110111101000101100011101011",),
    ),
    Code128Vector(
        input_data="0123456789",
        expected_modules=(
            ("110100111001100110110011101101110101110110001000010110011011011110100001101001100011101011"),
        ),
    ),
)


CODE128_CODE_SET_A_GOLDEN_VECTORS: tuple[Code128Vector, ...] = (
    Code128Vector(
        input_data="\x00",
        expected_modules=("1101000010010100001100101000011001100011101011",),
    ),
    Code128Vector(
        input_data="\x1d",
        expected_modules=("1101000010010100011110101000111101100011101011",),
    ),
    Code128Vector(
        input_data="\r",
        expected_modules=("1101000010011110111010111101110101100011101011",),
    ),
)


CODE128_FNC_GOLDEN_VECTORS: tuple[Code128Vector, ...] = (
    Code128Vector(
        input_data="\uf001A",
        expected_modules=("110100100001111010111010100011000100100001101100011101011",),
    ),
    Code128Vector(
        input_data="\x00\uf001",
        expected_modules=("110100001001010000110011110101110111100010101100011101011",),
    ),
)


CODE128_AUTO_SWITCHING_GOLDEN_VECTORS: tuple[Code128Vector, ...] = (
    Code128Vector(
        input_data="ABC1234DEF",
        expected_modules=(
            "1101001000010100011000100010110001000100011010111011110101100111001000101100010111101110101100010001000110100010001100010101111000101100011101011",
        ),
    ),
    Code128Vector(
        input_data="\x01ABC",
        expected_modules=("1101000010010010110000101000110001000101100010001000110101000011001100011101011",),
    ),
    Code128Vector(
        input_data="ABCD1234",
        expected_modules=(
            "1101001000010100011000100010110001000100011010110001000101110111101011001110010001011000111011011101100011101011",
        ),
    ),
)


CODE128_INVALID_TEXT_VECTORS = (
    "\u0306\u01fd\u03b2\U0004fcff",
    "1\u0306a\ufffd.",
)
