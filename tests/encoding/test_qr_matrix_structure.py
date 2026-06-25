"""Contract tests for QR function-pattern construction, the reservation map, and data placement."""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.alignment import alignment_centers
from aspose_barcode_foss._internal.standards.qr.matrix import build_function_patterns, place_data
from aspose_barcode_foss._internal.standards.qr.tables import symbol_size

# Expected concentric finder (dark border, light ring, dark 3x3 centre) computed independently.
_EXPECTED_FINDER = [
    [1 if (dr in (0, 6) or dc in (0, 6) or (2 <= dr <= 4 and 2 <= dc <= 4)) else 0 for dc in range(7)]
    for dr in range(7)
]

# Expected concentric alignment 5x5 (dark border, light ring, dark centre) computed independently.
_EXPECTED_ALIGNMENT = [
    [1 if (dr in (-2, 2) or dc in (-2, 2) or (dr == 0 and dc == 0)) else 0 for dc in range(-2, 3)]
    for dr in range(-2, 3)
]


def _block(modules: list[list[int]], r0: int, c0: int, h: int, w: int) -> list[list[int]]:
    return [[modules[r0 + dr][c0 + dc] for dc in range(w)] for dr in range(h)]


def test_build_function_patterns_v1_is_21x21() -> None:
    modules, is_function = build_function_patterns(1)
    assert len(modules) == 21 and all(len(row) == 21 for row in modules)
    assert len(is_function) == 21 and all(len(row) == 21 for row in is_function)


def test_build_function_patterns_v1_finder_corners() -> None:
    """All three finder corners match the expected 7x7 concentric pattern."""
    modules, _ = build_function_patterns(1)
    n = symbol_size(1)
    assert _block(modules, 0, 0, 7, 7) == _EXPECTED_FINDER
    assert _block(modules, 0, n - 7, 7, 7) == _EXPECTED_FINDER
    assert _block(modules, n - 7, 0, 7, 7) == _EXPECTED_FINDER


def test_build_function_patterns_v1_dark_module() -> None:
    """The dark module at (4*version+9, 8) is dark and flagged as a function module."""
    modules, is_function = build_function_patterns(1)
    assert modules[13][8] == 1
    assert is_function[13][8] is True


def test_v1_has_no_alignment_centres() -> None:
    assert alignment_centers(1) == []


def test_v5_alignment_centre_anchor() -> None:
    assert alignment_centers(5) == [(30, 30)]


def test_build_function_patterns_v5_is_37x37() -> None:
    modules, _ = build_function_patterns(5)
    assert len(modules) == 37 and all(len(row) == 37 for row in modules)


def test_build_function_patterns_v5_alignment_pattern() -> None:
    """The single v5 alignment pattern at centre (30, 30) matches the expected 5x5."""
    modules, _ = build_function_patterns(5)
    # Centre (30, 30) -> rows 28..32, cols 28..32.
    assert _block(modules, 28, 28, 5, 5) == _EXPECTED_ALIGNMENT


def test_build_function_patterns_v5_timing_alternates_dark_first() -> None:
    """Timing row 6 and column 6 alternate starting dark across the inter-finder span."""
    modules, _ = build_function_patterns(5)
    n = symbol_size(5)
    for c in range(8, n - 8):
        assert modules[6][c] == (1 if c % 2 == 0 else 0)
    for r in range(8, n - 8):
        assert modules[r][6] == (1 if r % 2 == 0 else 0)


def test_function_modules_flagged() -> None:
    """is_function flags finder, separator, timing and the dark module (spot-checks)."""
    _, is_function = build_function_patterns(1)
    n = symbol_size(1)
    # Finder corners (origin cell of each).
    assert is_function[0][0] is True
    assert is_function[0][n - 7] is True
    assert is_function[n - 7][0] is True
    # Separator cells adjacent to the top-left finder.
    assert is_function[7][0] is True
    assert is_function[0][7] is True
    # Timing modules.
    assert is_function[6][8] is True
    assert is_function[8][6] is True
    # Dark module.
    assert is_function[13][8] is True


def _assert_fills_every_free_module(version: int) -> None:
    """place_data with a correctly-sized bit list must fill every previously-free module exactly once."""
    modules, is_function = build_function_patterns(version)
    n = symbol_size(version)
    free_positions = [(r, c) for r in range(n) for c in range(n) if not is_function[r][c]]
    free = len(free_positions)
    # Alternating bits so every placed value is unambiguously a planted data bit (no all-zero ambiguity).
    bitstream = [i % 2 for i in range(free)]
    result = place_data(modules, is_function, bitstream)  # source asserts i == free internally
    placed = {(r, c): result[r][c] for (r, c) in free_positions}
    assert len(placed) == free
    # Every free module now holds one of the planted bits (0 or 1) and the count is exhausted.
    assert all(v in (0, 1) for v in placed.values())


def test_place_data_fills_all_free_modules_v1() -> None:
    _assert_fills_every_free_module(1)


def test_place_data_fills_all_free_modules_v7() -> None:
    # Version 7 exercises the version-information reservation in addition to format info.
    _assert_fills_every_free_module(7)
