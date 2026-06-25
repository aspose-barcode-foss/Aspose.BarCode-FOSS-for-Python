"""Alignment-pattern centre coordinates and expansion to concrete centres.

Provides the per-version list of alignment-pattern centre coordinates (verbatim
from the ISO/IEC 18004 table, ISO/IEC 18004 Annex E) and a helper that forms
the Cartesian product of those centres on both axes, omitting the three corner
combinations whose 5x5 footprint overlaps a finder pattern.

References: ISO/IEC 18004 (alignment-pattern centres).
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# alignment-pattern centre coordinates (ISO/IEC 18004 Annex E), versions 1-40.
# Each value is a centre coordinate on BOTH axes; v1 has no alignment patterns.
# fmt: off
ALIGNMENT_CENTERS: Final[dict[int, tuple[int, ...]]] = {
    1: (),
    2: (6, 18),
    3: (6, 22),
    4: (6, 26),
    5: (6, 30),
    6: (6, 34),
    7: (6, 22, 38),
    8: (6, 24, 42),
    9: (6, 26, 46),
    10: (6, 28, 50),
    11: (6, 30, 54),
    12: (6, 32, 58),
    13: (6, 34, 62),
    14: (6, 26, 46, 66),
    15: (6, 26, 48, 70),
    16: (6, 26, 50, 74),
    17: (6, 30, 54, 78),
    18: (6, 30, 56, 82),
    19: (6, 30, 58, 86),
    20: (6, 34, 62, 90),
    21: (6, 28, 50, 72, 94),
    22: (6, 26, 50, 74, 98),
    23: (6, 30, 54, 78, 102),
    24: (6, 28, 54, 80, 106),
    25: (6, 32, 58, 84, 110),
    26: (6, 30, 58, 86, 114),
    27: (6, 34, 62, 90, 118),
    28: (6, 26, 50, 74, 98, 122),
    29: (6, 30, 54, 78, 102, 126),
    30: (6, 26, 52, 78, 104, 130),
    31: (6, 30, 56, 82, 108, 134),
    32: (6, 34, 60, 86, 112, 138),
    33: (6, 30, 58, 86, 114, 142),
    34: (6, 34, 62, 90, 118, 146),
    35: (6, 30, 54, 78, 102, 126, 150),
    36: (6, 24, 50, 76, 102, 128, 154),
    37: (6, 28, 54, 80, 106, 132, 158),
    38: (6, 32, 58, 84, 110, 136, 162),
    39: (6, 26, 54, 82, 110, 138, 166),
    40: (6, 30, 58, 86, 114, 142, 170),
}
# fmt: on


def alignment_centers(version: int) -> list[tuple[int, int]]:
    """Return the concrete alignment-pattern centres for ``version`` as (row, col) pairs.

    Forms the Cartesian product of the centre values on both axes (row-major,
    ascending), omitting the three combinations whose 5x5 footprint overlaps a
    finder pattern: ``(6, 6)``, ``(6, max)`` and ``(max, 6)`` where ``max`` is the
    largest listed centre value. Version 1 has no alignment patterns and returns
    an empty list.
    """
    centers = ALIGNMENT_CENTERS[version]
    if not centers:
        return []
    coords = sorted(centers)
    largest = coords[-1]
    skipped = {(6, 6), (6, largest), (largest, 6)}
    return [(row, col) for row in coords for col in coords if (row, col) not in skipped]
