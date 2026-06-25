"""QR data-mask predicates, mask application, the four ISO penalty features, and best-mask selection.

Implements the eight data masks (ISO/IEC 18004 §7.8.1), ``apply_mask`` (XOR-toggle of
non-function modules), the four mask-penalty features N1..N4 (§7.8.3), their total, and
``select_best_mask`` which evaluates a candidate-grid builder over masks 0..7 and returns the
lowest-penalty mask (ties resolved to the lowest mask number).

References: ISO/IEC 18004 (data masks, mask penalty, best-mask
selection).
"""

from __future__ import annotations

from typing import Final
from collections.abc import Callable, Sequence

Grid = Sequence[Sequence[int]]

# ---------------------------------------------------------------------------
# data-mask predicates: (i, j) -> bool. i = row (0 top), j = col (0 left).
# The mask INVERTS a data module wherever its condition is true.
# ---------------------------------------------------------------------------

MASK_PREDICATES: Final[tuple[Callable[[int, int], bool], ...]] = (
    lambda i, j: (i + j) % 2 == 0,
    lambda i, j: i % 2 == 0,
    lambda i, j: j % 3 == 0,
    lambda i, j: (i + j) % 3 == 0,
    lambda i, j: (i // 2 + j // 3) % 2 == 0,
    lambda i, j: (i * j) % 2 + (i * j) % 3 == 0,
    lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0,
    lambda i, j: ((i + j) % 2 + (i * j) % 3) % 2 == 0,
)


def apply_mask(modules: Grid, mask_id: int, is_function: Sequence[Sequence[bool]]) -> list[list[int]]:
    """Return a NEW grid with every non-function module XOR-toggled where the mask predicate holds.

    ``is_function[i][j]`` is the reservation map; function modules are never toggled.
    """
    predicate = MASK_PREDICATES[mask_id]
    result = [list(row) for row in modules]
    n = len(result)
    for i in range(n):
        for j in range(n):
            if not is_function[i][j] and predicate(i, j):
                result[i][j] ^= 1
    return result


# ---------------------------------------------------------------------------
# penalty features, evaluated on the masked, fully-assembled grid.
# ---------------------------------------------------------------------------


def _line_penalty_n1(line: Sequence[int]) -> int:
    """N1 contribution for a single row or column: each run of >=5 adds 3 + (runLength - 5)."""
    total = 0
    run_colour = line[0]
    run_length = 1
    for value in line[1:]:
        if value == run_colour:
            run_length += 1
        else:
            if run_length >= 5:
                total += 3 + (run_length - 5)
            run_colour = value
            run_length = 1
    if run_length >= 5:
        total += 3 + (run_length - 5)
    return total


def penalty_n1(modules: Grid) -> int:
    """N1: for each row and each column, every run of >=5 same-colour adds 3 + (runLength - 5)."""
    n = len(modules)
    total = 0
    for row in modules:
        total += _line_penalty_n1(row)
    for j in range(n):
        column = [modules[i][j] for i in range(n)]
        total += _line_penalty_n1(column)
    return total


def penalty_n2(modules: Grid) -> int:
    """N2: each 2x2 block of one colour adds 3 (every overlapping 2x2 sub-block counted)."""
    n = len(modules)
    total = 0
    for i in range(n - 1):
        for j in range(n - 1):
            value = modules[i][j]
            if value == modules[i][j + 1] == modules[i + 1][j] == modules[i + 1][j + 1]:
                total += 3
    return total


_N3_PATTERN_A: Final[tuple[int, ...]] = (1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0)
_N3_PATTERN_B: Final[tuple[int, ...]] = (0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1)
_N3_LEN: Final[int] = len(_N3_PATTERN_A)


def _line_penalty_n3(line: Sequence[int]) -> int:
    """N3 contribution for a single row or column: 40 per occurrence of either 11-module pattern."""
    total = 0
    n = len(line)
    for start in range(n - _N3_LEN + 1):
        window = tuple(line[start : start + _N3_LEN])
        if window == _N3_PATTERN_A or window == _N3_PATTERN_B:
            total += 40
    return total


def penalty_n3(modules: Grid) -> int:
    """N3: each occurrence of `10111010000` or `00001011101` in any row/column adds 40."""
    n = len(modules)
    total = 0
    for row in modules:
        total += _line_penalty_n3(row)
    for j in range(n):
        column = [modules[i][j] for i in range(n)]
        total += _line_penalty_n3(column)
    return total


def penalty_n4(modules: Grid) -> int:
    """N4: dark-ratio deviation from 50%; add 10*k for k = min(|prev-50|, |next-50|) // 5."""
    n = len(modules)
    total = n * n
    dark = sum(value for row in modules for value in row)
    ratio = dark * 100 // total
    prev = (ratio // 5) * 5
    nxt = prev if prev == ratio else prev + 5
    k = min(abs(prev - 50), abs(nxt - 50)) // 5
    return 10 * k


def penalty(modules: Grid) -> int:
    """Total mask penalty: N1 + N2 + N3 + N4 on the masked, fully-assembled grid."""
    return penalty_n1(modules) + penalty_n2(modules) + penalty_n3(modules) + penalty_n4(modules)


def select_best_mask(build_for_mask: Callable[[int], Grid]) -> int:
    """Return the lowest-penalty mask id over 0..7; ties resolved to the lowest mask number.

    ``build_for_mask(mask_id)`` must return the fully-assembled masked grid (data masked plus
    format/version information written) for that candidate mask.
    """
    best_mask = 0
    best_penalty = penalty(build_for_mask(0))
    for mask_id in range(1, 8):
        candidate = penalty(build_for_mask(mask_id))
        if candidate < best_penalty:
            best_penalty = candidate
            best_mask = mask_id
    return best_mask
