"""Contract tests for QR data-mask predicates, the four penalty features, and best-mask selection."""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.masking import (
    MASK_PREDICATES,
    penalty_n1,
    penalty_n2,
    penalty_n3,
    penalty_n4,
    select_best_mask,
)


def _expected_predicate(mask_id: int, i: int, j: int) -> bool:
    """Recompute the mask condition for (i, j) directly, independent of the module under test."""
    if mask_id == 0:
        return (i + j) % 2 == 0
    if mask_id == 1:
        return i % 2 == 0
    if mask_id == 2:
        return j % 3 == 0
    if mask_id == 3:
        return (i + j) % 3 == 0
    if mask_id == 4:
        return (i // 2 + j // 3) % 2 == 0
    if mask_id == 5:
        return (i * j) % 2 + (i * j) % 3 == 0
    if mask_id == 6:
        return ((i * j) % 2 + (i * j) % 3) % 2 == 0
    if mask_id == 7:
        return ((i + j) % 2 + (i * j) % 3) % 2 == 0
    raise ValueError(mask_id)


def test_mask_predicates_match_section_k_formulas() -> None:
    """Each MASK_PREDICATES entry must equal the formula over a spread of (i, j) pairs."""
    for mask_id in range(8):
        for i in range(17):
            for j in range(17):
                assert MASK_PREDICATES[mask_id](i, j) == _expected_predicate(mask_id, i, j), (
                    f"mask {mask_id} disagrees at ({i}, {j})"
                )


def _grid_with_dark_count(n: int, dark: int) -> list[list[int]]:
    """Build an n*n grid holding exactly ``dark`` dark modules (row-major fill)."""
    flat = [1] * dark + [0] * (n * n - dark)
    return [flat[r * n : (r + 1) * n] for r in range(n)]


def test_penalty_n4_all_light_scores_100() -> None:
    # 100 modules, 0 dark -> ratio 0 -> k = min(50, 50)//5 = 10 -> 10*10 = 100.
    assert penalty_n4(_grid_with_dark_count(10, 0)) == 100


def test_penalty_n4_balanced_scores_zero() -> None:
    # 100 modules, 50 dark -> ratio 50 -> k = 0 -> 0.
    assert penalty_n4(_grid_with_dark_count(10, 50)) == 0


def test_penalty_n4_45_percent_scores_10() -> None:
    # 100 modules, 45 dark -> ratio 45 -> k = min(5, 5)//5 = 1 -> 10.
    assert penalty_n4(_grid_with_dark_count(10, 45)) == 10


def test_penalty_n4_55_percent_scores_10() -> None:
    # 100 modules, 55 dark -> ratio 55 -> k = min(5, 5)//5 = 1 -> 10.
    assert penalty_n4(_grid_with_dark_count(10, 55)) == 10


def _checkerboard(n: int) -> list[list[int]]:
    """A strictly alternating grid: no run >=2 in any row/column, no monochrome 2x2, no §N3 pattern."""
    return [[(r + c) % 2 for c in range(n)] for r in range(n)]


def test_penalty_n1_run_of_five_adds_three() -> None:
    """Forcing one row to a run of exactly 5 (over a checkerboard base) adds exactly 3.

    The base is a checkerboard so no row or column has a run >=5; the only deviation is one row
    set to a constant value, isolating a single horizontal run of length n. We therefore use an
    n=5 grid: the planted row contributes one run of 5 (-> 3). Columns are unaffected because each
    column already alternated and the single planted row only changes one cell per column (no new
    column run >=5 is created in a height-5 grid).
    """
    base = _checkerboard(5)
    base_penalty = penalty_n1(base)
    grid = [list(row) for row in base]
    grid[2] = [1, 1, 1, 1, 1]  # one horizontal run of exactly 5
    assert penalty_n1(grid) - base_penalty == 3


def test_penalty_n1_run_of_six_adds_four() -> None:
    """A run of length 6 adds 3 + (6 - 5) = 4 over the checkerboard base (delta isolates the run)."""
    base = _checkerboard(6)
    base_penalty = penalty_n1(base)
    grid = [list(row) for row in base]
    grid[2] = [1, 1, 1, 1, 1, 1]  # one horizontal run of exactly 6
    assert penalty_n1(grid) - base_penalty == 4


def test_penalty_n2_single_solid_block_adds_three() -> None:
    """One monochrome 2x2 block planted into a checkerboard adds exactly 3.

    The checkerboard base has no monochrome 2x2 block (every 2x2 holds two of each colour). We
    flip a single cell so that one 2x2 sub-block becomes solid. Flipping grid[0][0] to match its
    diagonal neighbour makes exactly the (0,0) 2x2 monochrome and creates no other monochrome 2x2.
    """
    base = _checkerboard(6)
    assert penalty_n2(base) == 0
    grid = [list(row) for row in base]
    # base 2x2 at (0,0): [[0,1],[1,0]]; set (0,0)->1 and (1,1)->1 makes it [[1,1],[1,1]] solid.
    grid[0][0] = 1
    grid[1][1] = 1
    assert penalty_n2(grid) == 3


def test_penalty_n3_pattern_in_row_adds_40() -> None:
    """A row containing the 11-module §N3 pattern adds exactly 40, with no accidental column hit.

    We build a checkerboard tall/wide enough to hold the 11-module pattern, plant the pattern in
    one row, and pad the rest of that row so no second occurrence forms. Columns cannot form the
    pattern because only one row deviates from the alternating base (a vertical 11-window needs
    eleven specific rows, impossible with a single planted row over a checkerboard).
    """
    pattern = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
    n = 13
    grid = _checkerboard(n)
    grid[5] = pattern + [0, 1]  # 11-pattern then two trailing modules; only one occurrence
    assert penalty_n3(grid) == 40


def test_select_best_mask_breaks_tie_to_lower_id() -> None:
    """When two masks tie for the global-minimum penalty, the lower mask id wins."""
    # Low-penalty grid: balanced dark ratio, no runs/blocks/patterns -> total penalty 0.
    low = _checkerboard(8)
    # High-penalty grid: all-light 8x8 -> n4 contributes (ratio 0 -> k=10 -> 100), plus n1 runs.
    high = [[0] * 8 for _ in range(8)]

    def build_for_mask(mask_id: int) -> list[list[int]]:
        # Masks 2 and 5 share the minimum penalty (the low grid); all others score higher.
        if mask_id in (2, 5):
            return [list(row) for row in low]
        return [list(row) for row in high]

    assert select_best_mask(build_for_mask) == 2
