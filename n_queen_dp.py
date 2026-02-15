"""
N-Queens Problem — Bitmask Dynamic Programming Approach
=======================================================
Solves the N-Queens problem for board sizes 5×5 through 8×8 using
bitmask DP.  At each row we track three bitmasks (columns, left
diagonals, right diagonals) representing attacked positions, and
expand only safe placements — effectively a DP over rows with a
compact state representation.
"""

import time
from typing import List, Tuple


# ---------------------------------------------------------------------------
#  Core solver – bitmask DP
# ---------------------------------------------------------------------------

def solve_n_queens(n: int) -> List[List[int]]:
    """
    Return every solution for an n×n board.

    Each solution is a list of length *n* where solution[row] = col
    indicates a queen is placed at (row, col).

    The algorithm processes one row at a time.  The DP state is the
    triple (cols, left_diags, right_diags) encoded as bitmasks:
      • cols        – columns already occupied
      • left_diags  – left-going diagonals (↙) already attacked
      • right_diags – right-going diagonals (↘) already attacked

    At each row the available positions are computed in O(1) with
    bitwise operations, and we branch only on valid placements.
    """
    all_columns = (1 << n) - 1  # mask with the lowest n bits set
    solutions: List[List[int]] = []

    def dp(row: int, cols: int, left_diag: int, right_diag: int,
           placement: List[int]) -> None:
        if row == n:
            solutions.append(placement[:])
            return

        # available positions: bits that are 0 in all three masks
        available = all_columns & ~(cols | left_diag | right_diag)

        while available:
            # isolate the lowest set bit → next candidate column
            bit = available & -available
            available ^= bit              # remove it from candidates
            col = bit.bit_length() - 1    # convert bitmask → column index

            placement.append(col)
            dp(
                row + 1,
                cols | bit,
                (left_diag | bit) << 1,    # shift left for next row
                (right_diag | bit) >> 1,   # shift right for next row
                placement,
            )
            placement.pop()

    dp(0, 0, 0, 0, [])
    return solutions


# ---------------------------------------------------------------------------
#  Pretty-print helpers
# ---------------------------------------------------------------------------

def board_string(n: int, placement: List[int]) -> str:
    """Return an ASCII chessboard for a single solution."""
    lines = []
    col_hdr = "    " + "  ".join(str(c) for c in range(n))
    lines.append(col_hdr)
    lines.append("  +" + "---" * n + "+")
    for row, col in enumerate(placement):
        row_str = f"{row} |"
        for c in range(n):
            row_str += " Q " if c == col else " . "
        row_str += "|"
        lines.append(row_str)
    lines.append("  +" + "---" * n + "+")
    return "\n".join(lines)


def print_summary(n: int, solutions: List[List[int]], elapsed: float) -> None:
    """Print solution count, timing, and a few example boards."""
    print(f"\n{'=' * 50}")
    print(f"  N = {n}  |  {len(solutions)} solutions found  |  {elapsed:.4f}s")
    print(f"{'=' * 50}")

    # show up to 3 example solutions
    show = min(3, len(solutions))
    for i in range(show):
        print(f"\n  Solution {i + 1}:")
        print(board_string(n, solutions[i]))

    if len(solutions) > show:
        print(f"\n  ... and {len(solutions) - show} more solutions")


# ---------------------------------------------------------------------------
#  Main – solve for 5×5 → 8×8
# ---------------------------------------------------------------------------

def main() -> None:
    print("N-Queens Solver — Bitmask Dynamic Programming")
    print("=" * 50)

    results: List[Tuple[int, int, float]] = []

    for n in range(5, 9):
        start = time.perf_counter()
        solutions = solve_n_queens(n)
        elapsed = time.perf_counter() - start

        results.append((n, len(solutions), elapsed))
        print_summary(n, solutions, elapsed)

    # final comparison table
    print(f"\n{'=' * 50}")
    print("  Summary")
    print(f"{'=' * 50}")
    print(f"  {'N':>3}  {'Solutions':>10}  {'Time (s)':>10}")
    print(f"  {'---':>3}  {'----------':>10}  {'----------':>10}")
    for n, count, elapsed in results:
        print(f"  {n:>3}  {count:>10}  {elapsed:>10.6f}")
    print()


if __name__ == "__main__":
    main()
