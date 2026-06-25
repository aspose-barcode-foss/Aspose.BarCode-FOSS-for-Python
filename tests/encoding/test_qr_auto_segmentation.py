"""Pure-unit tests for the QR Code AUTO mode-segmentation engine (ISO/IEC 18004:2015 §7.4,).

These tests lock down AUTO correctness directly, without any rendering or external tooling.
They assert two things directly from ``encoding_bit_length`` / ``segment_optimal``:

* AUTO optimality -- ``bits(AUTO) <= bits(forced m)`` for every forced single mode ``m`` in
  which the input is *representable* (a forced mode that cannot encode a character raises
  ``InvalidInputError`` from ``encoding_bit_length``; that is a "not representable" signal,
  not a comparison), and
* boundary-DP correctness -- the data-bit formulas and the Table 3
  count-indicator widths compose into the pinned, hand-computed bit totals.
"""

from __future__ import annotations

import pytest

from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import QrEncodeMode
from aspose_barcode_foss._internal.standards.qr import (
    QrMode,
    Segment,
    encoding_bit_length,
    segment_optimal,
    segments_bit_length,
)
from aspose_barcode_foss._internal.standards.qr.segments import (
    alphanumeric_data_bits,
    byte_data_bits,
    count_indicator_bits,
    kanji_data_bits,
    numeric_data_bits,
)

_FORCED_MODES: tuple[QrEncodeMode, ...] = (
    QrEncodeMode.NUMERIC,
    QrEncodeMode.ALPHANUMERIC,
    QrEncodeMode.BYTE,
    QrEncodeMode.KANJI,
)


def _assert_auto_optimal(text: str, version: int) -> None:
    """Assert AUTO is no worse than any forced mode the input is representable in.

    Forced modes that raise ``InvalidInputError`` (ineligible characters) are skipped: they
    cannot encode ``text`` at all, so there is nothing to compare against. At least one forced
    mode must be representable (BYTE for Latin-1, KANJI for Shift-JIS runs).
    """
    auto_bits = encoding_bit_length(text, version, QrEncodeMode.AUTO, None)
    representable = 0
    for mode in _FORCED_MODES:
        try:
            forced_bits = encoding_bit_length(text, version, mode, None)
        except InvalidInputError:
            continue  # input not representable in this forced single mode
        representable += 1
        assert auto_bits <= forced_bits, f"AUTO {auto_bits} > forced {mode.name} {forced_bits} for {text!r}"
    assert representable >= 1


# ---------------------------------------------------------------------------
# 1. worked-example pin.
# ---------------------------------------------------------------------------


def test_example_5_segment_optimal_split() -> None:
    """AUTO splits ``A123456789`` into an alnum head and a numeric tail (Example 5)."""
    assert segment_optimal("A123456789", 1) == [
        Segment(QrMode.ALPHANUMERIC, "A"),
        Segment(QrMode.NUMERIC, "123456789"),
    ]


def test_example_5_pinned_bit_lengths() -> None:
    """The worked-example AUTO/forced bit totals match the hand-computed values."""
    assert encoding_bit_length("A123456789", 1, QrEncodeMode.AUTO, None) == 63
    assert encoding_bit_length("A123456789", 1, QrEncodeMode.ALPHANUMERIC, None) == 68
    assert encoding_bit_length("A123456789", 1, QrEncodeMode.BYTE, None) == 92


def test_example_5_auto_no_worse_than_representable_modes() -> None:
    """AUTO (63) is <= both representable single modes; forced NUMERIC is not representable."""
    auto_bits = encoding_bit_length("A123456789", 1, QrEncodeMode.AUTO, None)
    alpha_bits = encoding_bit_length("A123456789", 1, QrEncodeMode.ALPHANUMERIC, None)
    byte_bits = encoding_bit_length("A123456789", 1, QrEncodeMode.BYTE, None)
    assert auto_bits <= alpha_bits
    assert auto_bits <= byte_bits
    _assert_auto_optimal("A123456789", 1)


def test_example_5_forced_numeric_raises() -> None:
    """The leading ``A`` is not numeric, so forced NUMERIC reports "not representable"."""
    with pytest.raises(InvalidInputError):
        encoding_bit_length("A123456789", 1, QrEncodeMode.NUMERIC, None)


# ---------------------------------------------------------------------------
# 2. Per-winner optimality fixtures (each uses the representable-only helper).
# ---------------------------------------------------------------------------


def test_numeric_wins() -> None:
    """A pure-digit run collapses to one numeric segment and AUTO stays optimal."""
    assert segment_optimal("0123456789012", 1) == [Segment(QrMode.NUMERIC, "0123456789012")]
    _assert_auto_optimal("0123456789012", 1)


def test_alphanumeric_wins() -> None:
    """An alnum run collapses to one alphanumeric segment and AUTO stays optimal."""
    assert segment_optimal("HELLO-WORLD", 1) == [Segment(QrMode.ALPHANUMERIC, "HELLO-WORLD")]
    _assert_auto_optimal("HELLO-WORLD", 1)


def test_byte_wins() -> None:
    """Lower-case/punctuation forces a single byte segment and AUTO stays optimal."""
    assert segment_optimal("Hello, world!", 1) == [Segment(QrMode.BYTE, "Hello, world!")]
    _assert_auto_optimal("Hello, world!", 1)


def test_kanji_wins() -> None:
    """A pure Shift-JIS run is Kanji-only; the three non-Kanji forced modes are unrepresentable."""
    assert segment_optimal("点茗点茗", 1) == [Segment(QrMode.KANJI, "点茗点茗")]
    _assert_auto_optimal("点茗点茗", 1)

    # The characters are code point > 255, so only KANJI can represent them.
    for mode in (QrEncodeMode.NUMERIC, QrEncodeMode.ALPHANUMERIC, QrEncodeMode.BYTE):
        with pytest.raises(InvalidInputError):
            encoding_bit_length("点茗点茗", 1, mode, None)

    auto_bits = encoding_bit_length("点茗点茗", 1, QrEncodeMode.AUTO, None)
    kanji_bits = encoding_bit_length("点茗点茗", 1, QrEncodeMode.KANJI, None)
    assert auto_bits == kanji_bits


def test_segmented_wins() -> None:
    """The worked-example split is the AUTO winner and remains optimal over representable modes."""
    assert segment_optimal("A123456789", 1) == [
        Segment(QrMode.ALPHANUMERIC, "A"),
        Segment(QrMode.NUMERIC, "123456789"),
    ]
    _assert_auto_optimal("A123456789", 1)


# ---------------------------------------------------------------------------
# 3. Boundary-DP composition checks.
# ---------------------------------------------------------------------------


def test_data_bit_formulas() -> None:
    """The mode data-bit formulas match the hand-computed counts."""
    assert numeric_data_bits(8) == 27
    assert alphanumeric_data_bits(5) == 28
    assert kanji_data_bits(2) == 26
    assert byte_data_bits(3) == 24


def test_segments_bit_length_composes_header_count_data() -> None:
    """``segments_bit_length`` adds the 4-bit header, the count indicator, and the data bits."""
    assert (
        segments_bit_length([Segment(QrMode.NUMERIC, "01234567")], 1, eci_assignment_number=None)
        == 4 + count_indicator_bits(QrMode.NUMERIC, 1) + numeric_data_bits(8)
        == 41
    )
    assert (
        segments_bit_length([Segment(QrMode.ALPHANUMERIC, "AC-42")], 1, eci_assignment_number=None)
        == 4 + count_indicator_bits(QrMode.ALPHANUMERIC, 1) + alphanumeric_data_bits(5)
        == 41
    )
    assert (
        segments_bit_length([Segment(QrMode.KANJI, "点茗")], 1, eci_assignment_number=None)
        == 4 + count_indicator_bits(QrMode.KANJI, 1) + kanji_data_bits(2)
        == 38
    )


# ---------------------------------------------------------------------------
# 4. Per-version width sensitivity.
# ---------------------------------------------------------------------------


def test_numeric_count_width_group_boundary() -> None:
    """The same 13-digit input costs +2 bits at V10 vs V9: exactly the numeric count-width change."""
    bits_v9 = encoding_bit_length("0123456789012", 9, QrEncodeMode.AUTO, None)
    bits_v10 = encoding_bit_length("0123456789012", 10, QrEncodeMode.AUTO, None)
    assert bits_v9 == 58
    assert bits_v10 == 60
    width_delta = count_indicator_bits(QrMode.NUMERIC, 10) - count_indicator_bits(QrMode.NUMERIC, 9)
    assert width_delta == 12 - 10 == 2
    assert bits_v10 - bits_v9 == width_delta


# ---------------------------------------------------------------------------
# 5. Tie-break determinism.
# ---------------------------------------------------------------------------


def test_tie_break_prefers_fewer_segments() -> None:
    """``000a`` is a genuine equal-bit tie resolved in favour of a single byte segment.

    A single byte segment ``[byte "000a"]`` costs ``4 + 8 + 32 = 44`` bits, and the two-segment
    split ``numeric "000" + byte "a"`` also costs ``24 + 20 = 44`` bits. Both totals are 44, so
    the DP's tie-break (fewer segments first) must select the single byte segment.
    """
    assert segment_optimal("000a", 1) == [Segment(QrMode.BYTE, "000a")]
    assert encoding_bit_length("000a", 1, QrEncodeMode.AUTO, None) == 44
