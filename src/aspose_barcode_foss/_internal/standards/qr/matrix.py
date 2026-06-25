"""QR function-pattern construction, reservation map, zig-zag data placement, and matrix assembly.

Builds the function patterns (finder, separators, timing, dark module, alignment) and the module
reservation map, places the interleaved data+EC bit stream by the zig-zag rule, writes the
format-information and version-information bits, applies a chosen data mask, and
assembles the immutable final N*N grid (N = symbol_size(version)).

The placement/geometry follows the canonical (Nayuki) convention and is validated to reproduce the
independent oracle worked-example matrices exactly.

References: ISO/IEC 18004 (symbol geometry, function patterns, format and version
information, codeword placement and masking).
"""

from __future__ import annotations

from aspose_barcode_foss._internal.standards.qr.alignment import alignment_centers
from aspose_barcode_foss._internal.standards.qr.info_strings import format_info, version_info
from aspose_barcode_foss._internal.standards.qr.masking import MASK_PREDICATES
from aspose_barcode_foss._internal.standards.qr.tables import symbol_size


def _set(modules: list[list[int]], is_function: list[list[bool]], row: int, col: int, value: int) -> None:
    """Set a function/reserved module: writes both the value and the reservation flag."""
    modules[row][col] = value
    is_function[row][col] = True


def _place_finder(modules: list[list[int]], is_function: list[list[bool]], r0: int, c0: int) -> None:
    """Place a 7x7 finder pattern (dark border, light ring, dark 3x3 centre) at origin (r0, c0)."""
    for dr in range(7):
        for dc in range(7):
            dark = dr in (0, 6) or dc in (0, 6) or (2 <= dr <= 4 and 2 <= dc <= 4)
            _set(modules, is_function, r0 + dr, c0 + dc, 1 if dark else 0)


def build_function_patterns(version: int) -> tuple[list[list[int]], list[list[bool]]]:
    """Build the function patterns and reservation map for ``version``.

    Returns ``(modules, is_function)`` parallel N*N grids. ``modules`` holds 0/1 with all function
    patterns drawn (finder, separators, timing, dark module, alignment); ``is_function`` marks every
    function/reserved position (including the format-info and, for v>=7, version-info areas).
    """
    n = symbol_size(version)
    modules = [[0] * n for _ in range(n)]
    is_function = [[False] * n for _ in range(n)]

    # Finder patterns at the three corners.
    _place_finder(modules, is_function, 0, 0)
    _place_finder(modules, is_function, 0, n - 7)
    _place_finder(modules, is_function, n - 7, 0)

    # Separators: 1-module light ring on the interior-facing sides of each finder.
    for k in range(8):
        _set(modules, is_function, 7, k, 0)  # top-left, horizontal
        _set(modules, is_function, k, 7, 0)  # top-left, vertical
        _set(modules, is_function, 7, n - 1 - k, 0)  # top-right, horizontal
        _set(modules, is_function, k, n - 8, 0)  # top-right, vertical
        _set(modules, is_function, n - 8, k, 0)  # bottom-left, horizontal
        _set(modules, is_function, n - 1 - k, 7, 0)  # bottom-left, vertical

    # Timing patterns: row 6 and column 6, alternating dark/light by coordinate parity.
    for c in range(8, n - 8):
        _set(modules, is_function, 6, c, 1 if c % 2 == 0 else 0)
    for r in range(8, n - 8):
        _set(modules, is_function, r, 6, 1 if r % 2 == 0 else 0)

    # Alignment patterns: 5x5 (dark border, light ring, dark centre) at each centre.
    for cr, cc in alignment_centers(version):
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                dark = dr in (-2, 2) or dc in (-2, 2) or (dr == 0 and dc == 0)
                _set(modules, is_function, cr + dr, cc + dc, 1 if dark else 0)

    # Dark module: always dark.
    _set(modules, is_function, 4 * version + 9, 8, 1)

    _reserve_format_info(modules, is_function, n)
    if version >= 7:
        _reserve_version_info(modules, is_function, n)

    return modules, is_function


def _reserve_format_info(modules: list[list[int]], is_function: list[list[bool]], n: int) -> None:
    """Reserve the 15 format-information positions in both copies; values written later."""
    for i in range(6):
        is_function[i][8] = True
    is_function[7][8] = True
    is_function[8][8] = True
    is_function[8][7] = True
    for i in range(9, 15):
        is_function[8][14 - i] = True
    for i in range(8):
        is_function[8][n - 1 - i] = True
    for i in range(8, 15):
        is_function[n - 15 + i][8] = True


def _reserve_version_info(modules: list[list[int]], is_function: list[list[bool]], n: int) -> None:
    """Reserve the two 3x6 version-information blocks (v>=7 only,); values written later."""
    for i in range(18):
        a = n - 11 + (i % 3)
        b = i // 3
        is_function[b][a] = True
        is_function[a][b] = True


def place_data(modules: list[list[int]], is_function: list[list[bool]], bitstream: list[int]) -> list[list[int]]:
    """Place ``bitstream`` into the non-reserved modules by the zig-zag rule (mutates/returns modules).

    Starts bottom-right, fills 2-module-wide columns leftward (skipping column 6), zig-zagging
    right-then-left within a column and upward in odd column-pairs / downward in even pairs. Each bit
    1 => dark, 0 => light (pre-mask). Asserts the bitstream fills every free module exactly.
    """
    n = len(modules)
    i = 0
    col = n - 1
    while col >= 1:
        if col == 6:
            col = 5
        for vert in range(n):
            for j in (0, 1):
                x = col - j
                upward = ((col + 1) & 2) == 0
                y = (n - 1 - vert) if upward else vert
                if not is_function[y][x]:
                    modules[y][x] = bitstream[i]
                    i += 1
        col -= 2
    free = sum(not is_function[r][c] for r in range(n) for c in range(n))
    assert i == free, f"bitstream consumed {i} bits but {free} free modules exist"
    return modules


def write_format_info(modules: list[list[int]], ecc_letter: str, mask: int) -> list[list[int]]:
    """Write the 15-bit format-information string into both reserved areas in order (mutates/returns)."""
    n = len(modules)
    fmt = format_info(ecc_letter, mask)
    # First copy (around the top-left finder).
    for i in range(6):
        modules[i][8] = int(fmt[14 - i])
    modules[7][8] = int(fmt[14 - 6])
    modules[8][8] = int(fmt[14 - 7])
    modules[8][7] = int(fmt[14 - 8])
    for i in range(9, 15):
        modules[8][14 - i] = int(fmt[14 - i])
    # Second copy (top-right and bottom-left).
    for i in range(8):
        modules[8][n - 1 - i] = int(fmt[14 - i])
    for i in range(8, 15):
        modules[n - 15 + i][8] = int(fmt[14 - i])
    return modules


def write_version_info(modules: list[list[int]], version: int) -> list[list[int]]:
    """Write the 18-bit version-information string into both reserved 3x6 blocks in order (v>=7)."""
    vstr = version_info(version)
    if vstr is None:
        return modules
    n = len(modules)
    for i in range(18):
        bit = int(vstr[17 - i])
        a = n - 11 + (i % 3)
        b = i // 3
        modules[b][a] = bit
        modules[a][b] = bit
    return modules


def assemble(version: int, ecc_letter: str, bitstream: list[int], mask: int) -> tuple[tuple[int, ...], ...]:
    """Assemble the final immutable QR grid for ``version``/``ecc_letter``/``mask``.

    Builds function patterns, places the data bit stream, applies the data mask to non-function
    modules, writes format and (v>=7) version information, and returns the grid as a
    tuple of tuples. Called once per candidate mask during selection and once for the chosen mask.
    """
    modules, is_function = build_function_patterns(version)
    place_data(modules, is_function, bitstream)

    predicate = MASK_PREDICATES[mask]
    n = len(modules)
    for i in range(n):
        for j in range(n):
            if not is_function[i][j] and predicate(i, j):
                modules[i][j] ^= 1

    write_format_info(modules, ecc_letter, mask)
    write_version_info(modules, version)

    return tuple(tuple(row) for row in modules)
