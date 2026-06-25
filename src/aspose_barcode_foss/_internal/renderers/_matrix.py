"""Shared matrix helpers for renderers."""

from __future__ import annotations


def _iter_dark_runs(row: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    """Return contiguous dark module ranges for a matrix row."""
    runs: list[tuple[int, int]] = []
    run_start: int | None = None

    for index, module in enumerate(row):
        if module == 1 and run_start is None:
            run_start = index
            continue

        if module == 0 and run_start is not None:
            runs.append((run_start, index - run_start))
            run_start = None

    if run_start is not None:
        runs.append((run_start, len(row) - run_start))

    return tuple(runs)
