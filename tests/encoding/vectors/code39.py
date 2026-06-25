"""Code 39 golden vectors used by encoding tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Code39Vector:
    """One known-good Code 39 fixture."""

    input_data: str
    full_ascii: bool
    add_check_digit: bool
    expected_modules: tuple[str, ...]


CODE39_BASE_GOLDEN_VECTORS = (
    Code39Vector(
        input_data="A",
        full_ascii=False,
        add_check_digit=False,
        expected_modules=("100010111011101011101010001011101000101110111010",),
    ),
    Code39Vector(
        input_data="0",
        full_ascii=False,
        add_check_digit=False,
        expected_modules=("100010111011101010100011101110101000101110111010",),
    ),
    Code39Vector(
        input_data="CODE 39",
        full_ascii=False,
        add_check_digit=False,
        expected_modules=(
            "100010111011101011101110100010101110101110100010101011100010111011101011100010101000111010111010111011100010101010111000101110101000101110111010",
        ),
    ),
    Code39Vector(
        input_data="TEST8052",
        full_ascii=False,
        add_check_digit=False,
        expected_modules=(
            "1000101110111010101011101110001011101011100010101011101011100010101011101110001011101000101110101010001110111010111010001110101010111000101011101000101110111010",
        ),
    ),
    Code39Vector(
        input_data="Z-. $/+%",
        full_ascii=False,
        add_check_digit=False,
        expected_modules=(
            "1000101110111010100011101110101010001010111011101110001010111010100011101011101010001000100010101000100010100010100010100010001010100010001000101000101110111010",
        ),
    ),
    Code39Vector(
        input_data="CODE 39",
        full_ascii=False,
        add_check_digit=True,
        expected_modules=(
            "1000101110111010111011101000101011101011101000101010111000101110111010111000101010001110101110101110111000101010101110001011101011101010111000101000101110111010",
        ),
    ),
    Code39Vector(
        input_data="A",
        full_ascii=False,
        add_check_digit=True,
        expected_modules=("1000101110111010111010100010111011101010001011101000101110111010",),
    ),
)


CODE39EXT_GOLDEN_VECTORS = (
    Code39Vector(
        input_data="a",
        full_ascii=True,
        add_check_digit=False,
        expected_modules=("1000101110111010100010100010001011101010001011101000101110111010",),
    ),
    Code39Vector(
        input_data="abc",
        full_ascii=True,
        add_check_digit=False,
        expected_modules=(
            "10001011101110101000101000100010111010100010111010001010001000101011101000101110100010100010001011101110100010101000101110111010",
        ),
    ),
    Code39Vector(
        input_data="@",
        full_ascii=True,
        add_check_digit=False,
        expected_modules=("1000101110111010101000100010001010001110101011101000101110111010",),
    ),
    Code39Vector(
        input_data="Test123",
        full_ascii=True,
        add_check_digit=False,
        expected_modules=(
            "100010111011101010101110111000101000101000100010111010111000101010001010001000101011101011100010100010100010001010101110111000101110100010101110101110001010111011101110001010101000101110111010",
        ),
    ),
    Code39Vector(
        input_data="Hello, World!",
        full_ascii=True,
        add_check_digit=False,
        expected_modules=(
            "1000101110111010111010100011101010001010001000101110101110001010100010100010001010111010100011101000101000100010101110101000111010001010001000101110101110100010100010001010001010111010100011101000111010111010111000111010101010001010001000101110101110100010100010100010001011101010111000101000101000100010101110101000111010001010001000101010111000101110100010001010001011101010001011101000101110111010",
        ),
    ),
    Code39Vector(
        input_data=chr(9),
        full_ascii=True,
        add_check_digit=False,
        expected_modules=("1000101110111010100010001000101010111010001110101000101110111010",),
    ),
    Code39Vector(
        input_data=chr(127),
        full_ascii=True,
        add_check_digit=False,
        expected_modules=("1000101110111010101000100010001010101110111000101000101110111010",),
    ),
)
