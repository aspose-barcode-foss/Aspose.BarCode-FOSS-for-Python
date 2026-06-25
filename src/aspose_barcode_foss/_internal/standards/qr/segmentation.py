"""Optimal mode-segmentation engine for QR Code (ISO/IEC 18004:2015 §7.4).

Owns the AUTO optimal mode-segmentation dynamic program, the forced single-mode
segment builder (the encoder-side defensive backstop, raising ``InvalidInputError`` on
ineligible characters), and the bit-cost functions the parser's version search calls.

The cost model is the sum of the verbatim rules supplied by
``standards.qr.segments``; this module never re-derives a spec rule. ``segments_bit_length``
includes the ECI header but EXCLUDES the terminator / bit-pad / pad-codeword tail, exactly
mirroring the retiring ``required_bits`` semantics so the parser's version loop is a drop-in
replacement.

This module is PURE and SIDE-EFFECT-FREE: no printing, no I/O, no mutation of inputs.

References: ISO/IEC 18004 (boundary DP).
"""

from __future__ import annotations

from collections.abc import Callable

from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import QrEncodeMode
from aspose_barcode_foss._internal.standards.qr.bitstream import latin1_bytes
from aspose_barcode_foss._internal.standards.qr.segments import (
    QrMode,
    Segment,
    alphanumeric_data_bits,
    byte_data_bits,
    count_indicator_bits,
    is_alphanumeric,
    is_numeric,
    kanji_data_bits,
    numeric_data_bits,
    shift_jis_double_byte,
)

# ---------------------------------------------------------------------------
# Per-mode eligibility predicates and data-bit cost functions.
#
# Byte eligibility = the character is representable in the active byte
# interpretation (default Latin-1), i.e. code point <= 255. The byte fallback
# therefore always exists for Latin-1 input, so AUTO can always segment it.
# ---------------------------------------------------------------------------


def _is_byte(ch: str) -> bool:
    """Return True if ch is byte-eligible: representable in Latin-1 (code point <= 255)."""
    return ord(ch) <= 255


def _is_kanji(ch: str) -> bool:
    """Return True if ch is Kanji-eligible: a Shift-JIS double byte."""
    return shift_jis_double_byte(ch) is not None


# Mode -> (eligibility predicate, data-bit cost function over a run length).
# The data-bit cost for a run of n characters in a mode is data_bits(mode, n).
_MODE_SPEC: dict[QrMode, tuple[Callable[[str], bool], Callable[[int], int]]] = {
    QrMode.NUMERIC: (is_numeric, numeric_data_bits),
    QrMode.ALPHANUMERIC: (is_alphanumeric, alphanumeric_data_bits),
    QrMode.BYTE: (_is_byte, byte_data_bits),
    QrMode.KANJI: (_is_kanji, kanji_data_bits),
}

# Lexicographic mode order for the deterministic tie-break:
# numeric < alphanumeric < byte < kanji.
_MODE_RANK: dict[QrMode, int] = {
    QrMode.NUMERIC: 0,
    QrMode.ALPHANUMERIC: 1,
    QrMode.BYTE: 2,
    QrMode.KANJI: 3,
}

# DP enumeration order (matches the rank order so equal-key candidates are stable).
_DP_MODES: tuple[QrMode, ...] = (QrMode.NUMERIC, QrMode.ALPHANUMERIC, QrMode.BYTE, QrMode.KANJI)

# Map public encode modes to the internal forced data mode.
_FORCED_MODE: dict[QrEncodeMode, QrMode] = {
    QrEncodeMode.NUMERIC: QrMode.NUMERIC,
    QrEncodeMode.ALPHANUMERIC: QrMode.ALPHANUMERIC,
    QrEncodeMode.BYTE: QrMode.BYTE,
    QrEncodeMode.KANJI: QrMode.KANJI,
}


# ---------------------------------------------------------------------------
# Forced single-mode builder (encoder-side defensive backstop).
# ---------------------------------------------------------------------------


def forced_segments(text: str, mode: QrMode) -> list[Segment]:
    """Return a single ``Segment(mode, text)`` after validating every character is eligible.

    Raises ``InvalidInputError`` naming the mode, the offending character (via ``!r``), and
    its 0-based position on the first ineligible character. Empty text is allowed and yields
    ``[Segment(mode, "")]``. This is the encoder-side defensive backstop; the parser is the
    primary eligibility gate.
    """
    eligible, _ = _MODE_SPEC[mode]
    for position, ch in enumerate(text):
        if not eligible(ch):
            msg = f"character {ch!r} at position {position} is not eligible for {mode.value} mode"
            raise InvalidInputError(msg)
    return [Segment(mode, text)]


# ---------------------------------------------------------------------------
# AUTO optimal mode segmentation (boundary dynamic program).
# ---------------------------------------------------------------------------


def segment_optimal(text: str, version: int) -> list[Segment]:
    """Return the minimal-bit segment sequence for text at version (the boundary DP).

    O(N^2 * 4) authoritative formulation. ``best[i]`` is the minimal total header + count +
    data bits to encode the first ``i`` characters; ``best[0] = 0``; the answer is ``best[N]``.

    Transition: for every mode and split point ``j < i`` such that *every* character in
    ``text[j:i]`` is eligible for that mode,
    ``best[i] = best[j] + 4 + count_indicator_bits(mode, version) + data_bits(mode, i - j)``.

    Determinism is enforced by a comparison key ``(bits, segment_count, mode_rank_path)`` per
    prefix: fewer total bits, then fewer segments, then the lexicographically-earliest mode
    sequence (numeric < alphanumeric < byte < kanji). After backtracking, adjacent same-mode
    spans are coalesced into a single ``Segment`` (canonical minimal-segment form).
    """
    n = len(text)
    if n == 0:
        return []

    # key[i] = (bits, segment_count, mode_rank_path_tuple) for the best encoding of text[:i].
    # parent[i] = (mode, j) backpointer for that best encoding.
    key: list[tuple[int, int, tuple[int, ...]] | None] = [None] * (n + 1)
    parent: list[tuple[QrMode, int] | None] = [None] * (n + 1)
    key[0] = (0, 0, ())

    # Per-mode prefix eligibility: longest_eligible_from[mode][j] is the furthest end index
    # i such that text[j:i] is entirely eligible for mode (built incrementally below).
    for i in range(1, n + 1):
        for mode in _DP_MODES:
            eligible, data_bits = _MODE_SPEC[mode]
            header = 4 + count_indicator_bits(mode, version)
            # Walk split points j from i-1 down to 0; stop as soon as text[j] is ineligible
            # for mode (every shorter run would also include this ineligible character).
            for j in range(i - 1, -1, -1):
                if not eligible(text[j]):
                    break
                base = key[j]
                if base is None:
                    continue
                run_length = i - j
                candidate_bits = base[0] + header + data_bits(run_length)
                candidate_key = (
                    candidate_bits,
                    base[1] + 1,
                    base[2] + (_MODE_RANK[mode],),
                )
                current = key[i]
                if current is None or candidate_key < current:
                    key[i] = candidate_key
                    parent[i] = (mode, j)

    # Backtrack to recover (mode, j, i) spans, then coalesce adjacent same-mode spans.
    spans: list[tuple[QrMode, int, int]] = []
    i = n
    while i > 0:
        step = parent[i]
        assert step is not None  # best[n] is always reachable (byte fallback for Latin-1).
        mode, j = step
        spans.append((mode, j, i))
        i = j
    spans.reverse()

    segments: list[Segment] = []
    for mode, start, end in spans:
        if segments and segments[-1].mode is mode:
            previous = segments[-1]
            segments[-1] = Segment(mode, previous.text + text[start:end])
        else:
            segments.append(Segment(mode, text[start:end]))
    return segments


# ---------------------------------------------------------------------------
# Bit-cost functions for the parser's version search.
# ---------------------------------------------------------------------------


def _eci_header_bits(assignment_number: int) -> int:
    """Return the ECI header bit length for assignment_number by range (8 / 16 / 24).

    Range is NOT re-validated here (that is the parser's job); the length is selected purely
    by which band the number falls in.
    """
    if assignment_number <= 127:
        return 8
    if assignment_number <= 16383:
        return 16
    return 24


def _segment_char_count(segment: Segment) -> int:
    """Return the character-count value for segment: Latin-1 bytes for byte mode, else chars."""
    if segment.mode is QrMode.BYTE:
        return len(latin1_bytes(segment.text))
    return len(segment.text)


def segments_bit_length(
    segments: list[Segment],
    version: int,
    *,
    eci_assignment_number: int | None,
) -> int:
    """Return the total data-bit length of segments at version (headers + counts + data).

    Sums ``4 + count_indicator_bits(seg.mode, version) + data_bits(seg.mode, count)`` over the
    segments, plus the ECI header bits when ``eci_assignment_number is not None``. EXCLUDES
    the terminator and pad bits (mirrors the retiring ``required_bits`` semantics).
    """
    total = 0
    for segment in segments:
        _, data_bits = _MODE_SPEC[segment.mode]
        total += 4 + count_indicator_bits(segment.mode, version) + data_bits(_segment_char_count(segment))
    if eci_assignment_number is not None:
        total += _eci_header_bits(eci_assignment_number)
    return total


def encoding_bit_length(text: str, version: int, mode: QrEncodeMode, eci: int | None) -> int:
    """Return the data-bit length for text at version under mode (the parser's version-search entry).

    For ``QrEncodeMode.AUTO`` the optimal segmentation is computed via ``segment_optimal``;
    otherwise the input is forced into the single mapped data mode (raising
    ``InvalidInputError`` on ineligible characters). The result is delegated to
    ``segments_bit_length`` with the ECI header included when ``eci is not None``.

    Because ``count_indicator_bits`` depends on the version group, this MUST be called per
    candidate version by the parser; do not cache a single group's cost.
    """
    if mode is QrEncodeMode.AUTO:
        segments = segment_optimal(text, version)
    else:
        segments = forced_segments(text, _FORCED_MODE[mode])
    return segments_bit_length(segments, version, eci_assignment_number=eci)
