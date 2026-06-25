"""Golden-vector tests for Code 128 encoding."""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.encoders.code128 import Code128Encoder
from aspose_barcode_foss._internal.models.options import Code128EncodeMode
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from tests.encoding.vectors.code128 import (
    CODE128_A,
    CODE128_AUTO_SWITCHING_GOLDEN_VECTORS,
    CODE128_CODE_SET_A_GOLDEN_VECTORS,
    CODE128_CODE_SET_B_GOLDEN_VECTORS,
    CODE128_CODE_SET_C_GOLDEN_VECTORS,
    CODE128_FNC_GOLDEN_VECTORS,
    CODE128_INVALID_TEXT_VECTORS,
    CODE128_REFERENCE_BEHAVIOR_GOLDEN_VECTORS,
    Code128Vector,
)

# Code 128 start-character module patterns (ISO/IEC 15417 Table 1).
START_A_PATTERN = "11010000100"
START_B_PATTERN = "11010010000"


def _build_payload(
    text: str,
    *,
    encode_mode: Code128EncodeMode = Code128EncodeMode.CODE_B,
) -> NormalizedPayload:
    """Return the standard Code 128 test payload shape."""
    return NormalizedPayload(
        symbology="code128",
        data=text,
        input_kind="text",
        code128_encode_mode=encode_mode,
    )


def _render_modules(
    vector: Code128Vector,
    *,
    encode_mode: Code128EncodeMode = Code128EncodeMode.CODE_B,
) -> tuple[str, ...]:
    """Encode one vector and flatten the module rows for assertion."""
    encoder = Code128Encoder()
    symbol = encoder.encode(_build_payload(vector.input_data, encode_mode=encode_mode))
    return tuple("".join(str(module) for module in row) for row in symbol.matrix.modules)


def test_code128_encoder_matches_golden_modules() -> None:
    """Code 128 encoding should match a known-good module sequence."""
    symbol = Code128Encoder().encode(_build_payload(CODE128_A.input_data))
    actual_rows = tuple("".join(str(module) for module in row) for row in symbol.matrix.modules)

    assert actual_rows == CODE128_A.expected_modules
    assert symbol.metadata.display_text == CODE128_A.input_data
    assert symbol.matrix.height == 1


@pytest.mark.parametrize(
    "vector",
    CODE128_CODE_SET_B_GOLDEN_VECTORS,
    ids=lambda vector: vector.input_data.encode("unicode_escape").decode("ascii"),
)
def test_code128_encoder_matches_additional_code_set_b_golden_modules(
    vector: Code128Vector,
) -> None:
    """Current Code Set B encoding should match the added golden fixtures."""
    symbol = Code128Encoder().encode(_build_payload(vector.input_data))

    assert _render_modules(vector) == vector.expected_modules
    assert symbol.metadata.display_text == vector.input_data
    assert symbol.matrix.height == 1


@pytest.mark.parametrize(
    "vector",
    CODE128_REFERENCE_BEHAVIOR_GOLDEN_VECTORS,
    ids=lambda vector: vector.input_data.encode("unicode_escape").decode("ascii"),
)
def test_code128_encoder_reference_behavior_vectors(
    vector: Code128Vector,
) -> None:
    """AUTO-mode reference fixtures should match their known-good module sequence."""
    assert _render_modules(vector, encode_mode=Code128EncodeMode.AUTO) == vector.expected_modules


def test_code128_auto_encodes_single_space_via_code_set_b() -> None:
    """A lone space should be encoded through Code Set B (START_B), not Code Set A.

    A single space is representable in both Code Set A and Code Set B; the standards-correct
    minimization selects Code Set B. AUTO must therefore produce the same symbol as an explicit
    Code Set B request and begin with the START_B pattern (not START_A).
    """
    encoder = Code128Encoder()
    auto_symbol = encoder.encode(_build_payload(" ", encode_mode=Code128EncodeMode.AUTO))
    code_b_symbol = encoder.encode(_build_payload(" ", encode_mode=Code128EncodeMode.CODE_B))

    auto_rows = tuple("".join(str(module) for module in row) for row in auto_symbol.matrix.modules)
    code_b_rows = tuple("".join(str(module) for module in row) for row in code_b_symbol.matrix.modules)

    assert auto_rows == code_b_rows
    assert auto_rows[0].startswith(START_B_PATTERN)
    assert not auto_rows[0].startswith(START_A_PATTERN)
    assert auto_symbol.matrix.height == 1


@pytest.mark.parametrize(
    "mode",
    [
        Code128EncodeMode.AUTO,
        Code128EncodeMode.CODE_AB,
        Code128EncodeMode.CODE_B,
        Code128EncodeMode.CODE_BC,
    ],
)
def test_code128_encoder_supports_code_set_b_compatible_modes(
    mode: Code128EncodeMode,
) -> None:
    """CODE_B-compatible modes should encode 'A' with the same START_B plan."""
    payload = _build_payload(CODE128_A.input_data, encode_mode=mode)

    symbol = Code128Encoder().encode(payload)
    actual_rows = tuple("".join(str(module) for module in row) for row in symbol.matrix.modules)

    assert actual_rows == CODE128_A.expected_modules


@pytest.mark.parametrize(
    "payload",
    [
        NormalizedPayload(
            symbology="upca",
            data=CODE128_A.input_data,
            input_kind="text",
            code128_encode_mode=Code128EncodeMode.CODE_B,
        ),
        NormalizedPayload(
            symbology="code128",
            data=CODE128_A.input_data.encode("ascii"),
            input_kind="binary",
            code128_encode_mode=Code128EncodeMode.CODE_B,
        ),
        NormalizedPayload(
            symbology="code128",
            data=CODE128_A.input_data,
            input_kind="text",
            code128_encode_mode=None,
        ),
        NormalizedPayload(
            symbology="code128",
            data="",
            input_kind="text",
            code128_encode_mode=Code128EncodeMode.CODE_B,
        ),
        NormalizedPayload(
            symbology="code128",
            data=CODE128_A.input_data,
            input_kind="text",
            code128_encode_mode="CODE_B",  # type: ignore[arg-type]
        ),
    ],
)
def test_code128_encoder_rejects_invalid_payload_contract(
    payload: NormalizedPayload,
) -> None:
    """Encoder contract violations should raise invalid-input errors."""
    with pytest.raises(InvalidInputError):
        Code128Encoder().encode(payload)


@pytest.mark.parametrize(
    "input_data",
    ["\n", "\x7f"],
    ids=lambda value: value.encode("unicode_escape").decode("ascii"),
)
def test_code128_encoder_rejects_unsupported_text_characters(input_data: str) -> None:
    """Unsupported characters should fail with the typed input error."""
    payload = _build_payload(input_data)

    with pytest.raises(InvalidInputError, match="character"):
        Code128Encoder().encode(payload)


@pytest.mark.parametrize(
    "input_data",
    CODE128_INVALID_TEXT_VECTORS,
    ids=lambda value: value.encode("unicode_escape").decode("ascii"),
)
def test_code128_encoder_rejects_reference_invalid_text_cases(
    input_data: str,
) -> None:
    """Non-Code-128 Unicode inputs from the fixture pack should fail predictably."""
    with pytest.raises(InvalidInputError, match="unsupported Code 128 character"):
        Code128Encoder().encode(_build_payload(input_data))


def test_code128_encoder_rejects_code_c_non_digit_input() -> None:
    """CODE_C mode with non-digit input should raise InvalidInputError from the parser."""
    payload = _build_payload("A", encode_mode=Code128EncodeMode.CODE_C)
    with pytest.raises(InvalidInputError):
        Code128Encoder().encode(payload)


@pytest.mark.parametrize(
    "vector",
    CODE128_CODE_SET_C_GOLDEN_VECTORS,
    ids=lambda vector: vector.input_data.encode("unicode_escape").decode("ascii"),
)
def test_code128_encoder_matches_code_set_c_golden_vectors(
    vector: Code128Vector,
) -> None:
    """Code Set C encoding should match BWIPP golden fixtures."""
    actual = _render_modules(vector, encode_mode=Code128EncodeMode.CODE_C)
    assert actual == vector.expected_modules


@pytest.mark.parametrize(
    "vector",
    CODE128_CODE_SET_A_GOLDEN_VECTORS,
    ids=lambda vector: vector.input_data.encode("unicode_escape").decode("ascii"),
)
def test_code128_encoder_matches_code_set_a_golden_vectors(
    vector: Code128Vector,
) -> None:
    """Code Set A encoding should match BWIPP golden fixtures and escape-render control chars."""
    encoder = Code128Encoder()
    symbol = encoder.encode(_build_payload(vector.input_data, encode_mode=Code128EncodeMode.CODE_A))
    actual_rows = tuple("".join(str(m) for m in row) for row in symbol.matrix.modules)

    assert actual_rows == vector.expected_modules
    assert "\x00" not in symbol.metadata.display_text
    assert "<" in symbol.metadata.display_text


@pytest.mark.parametrize(
    "vector, encode_mode",
    [
        (CODE128_FNC_GOLDEN_VECTORS[0], Code128EncodeMode.CODE_B),
        (CODE128_FNC_GOLDEN_VECTORS[1], Code128EncodeMode.CODE_A),
    ],
    ids=["fnc1_code_b", "nul_fnc1_code_a"],
)
def test_code128_encoder_matches_fnc_golden_vectors(
    vector: Code128Vector,
    encode_mode: Code128EncodeMode,
) -> None:
    """FNC sentinel encoding should match BWIPP golden fixtures."""
    encoder = Code128Encoder()
    symbol = encoder.encode(_build_payload(vector.input_data, encode_mode=encode_mode))
    actual_rows = tuple("".join(str(m) for m in row) for row in symbol.matrix.modules)

    assert actual_rows == vector.expected_modules
    assert "<FNC1>" in symbol.metadata.display_text


@pytest.mark.parametrize(
    "vector",
    CODE128_AUTO_SWITCHING_GOLDEN_VECTORS,
    ids=lambda vector: vector.input_data.encode("unicode_escape").decode("ascii"),
)
def test_code128_encoder_matches_auto_switching_golden_vectors(
    vector: Code128Vector,
) -> None:
    """AUTO mode with inter-set switching should match BWIPP golden fixtures."""
    actual = _render_modules(vector, encode_mode=Code128EncodeMode.AUTO)
    assert actual == vector.expected_modules


def test_code128_encoder_rejects_code_c_odd_length_input() -> None:
    """CODE_C mode with odd-length digit input should raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        Code128Encoder().encode(_build_payload("123", encode_mode=Code128EncodeMode.CODE_C))


def test_code128_encoder_rejects_code_a_lowercase() -> None:
    """CODE_A mode with a lowercase character (Code Set B-only) should raise InvalidInputError."""
    with pytest.raises(InvalidInputError):
        Code128Encoder().encode(_build_payload("a", encode_mode=Code128EncodeMode.CODE_A))


def test_code128_encoder_rejects_auto_del_character() -> None:
    """AUTO mode with DEL (0x7F) should raise InvalidInputError — DEL is not in any Code 128 code set."""
    with pytest.raises(InvalidInputError):
        Code128Encoder().encode(_build_payload("\x7f", encode_mode=Code128EncodeMode.AUTO))
