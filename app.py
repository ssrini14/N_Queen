"""
N-Queens Solver — Interactive Gradio App
========================================
Visual, step-by-step explorer for the N-Queens problem (5×5 → 8×8)
using the bitmask DP solver.
"""

import time
from typing import List, Optional, Tuple

import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from n_queen_dp import solve_n_queens

matplotlib.use("Agg")

# ── colour palette ──────────────────────────────────────────────────────────
LIGHT_SQ = "#F0D9B5"
DARK_SQ = "#B58863"
QUEEN_COLOR = "#1565C0"
ATTACK_COLOR = "#FFCDD2"
SAFE_COLOR = "#C8E6C9"
BORDER_COLOR = "#5D4037"
STEP_QUEEN_COLOR = "#1565C0"
PLACED_QUEEN_COLOR = "#1565C0"
HEADER_BG = "#3E2723"

# ── global solution cache ───────────────────────────────────────────────────
_cache: dict = {}


def _get_solutions(n: int) -> List[List[int]]:
    if n not in _cache:
        _cache[n] = solve_n_queens(n)
    return _cache[n]


# ── drawing helpers ─────────────────────────────────────────────────────────

def _draw_board(
    n: int,
    placement: Optional[List[int]] = None,
    step: Optional[int] = None,
    show_attacks: bool = False,
    title: str = "",
) -> plt.Figure:
    """
    Render an n×n chessboard with optional queen placement.

    Parameters
    ----------
    n : board size
    placement : full solution (list of col indices per row)
    step : if given, only show queens for rows 0..step (animation mode)
    show_attacks : highlight attacked / safe squares
    title : figure title
    """
    fig, ax = plt.subplots(1, 1, figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_xlim(-0.05, n + 0.05)
    ax.set_ylim(-0.05, n + 0.55)
    ax.set_aspect("equal")
    ax.axis("off")

    # determine which queens are visible
    visible_rows = range(n)
    if placement and step is not None:
        visible_rows = range(min(step + 1, n))

    # build attack map for visible queens
    attacked = set()
    if show_attacks and placement:
        for r in visible_rows:
            c = placement[r]
            for i in range(n):
                attacked.add((r, i))       # row
                attacked.add((i, c))       # column
                if 0 <= r + i < n and 0 <= c + i < n:
                    attacked.add((r + i, c + i))
                if 0 <= r - i < n and 0 <= c - i < n:
                    attacked.add((r - i, c - i))
                if 0 <= r + i < n and 0 <= c - i < n:
                    attacked.add((r + i, c - i))
                if 0 <= r - i < n and 0 <= c + i < n:
                    attacked.add((r - i, c + i))

    # draw squares
    for row in range(n):
        for col in range(n):
            is_light = (row + col) % 2 == 0
            base = LIGHT_SQ if is_light else DARK_SQ

            if show_attacks and placement:
                if (row, col) in attacked:
                    base = ATTACK_COLOR
                elif row not in list(visible_rows):
                    base = SAFE_COLOR

            rect = patches.FancyBboxPatch(
                (col, n - 1 - row),
                1, 1,
                boxstyle="round,pad=0.01",
                facecolor=base,
                edgecolor=BORDER_COLOR,
                linewidth=1.2,
            )
            ax.add_patch(rect)

    # column / row labels
    for i in range(n):
        ax.text(i + 0.5, -0.02, chr(ord("a") + i),
                ha="center", va="top", fontsize=11, fontweight="bold",
                color=BORDER_COLOR)
        ax.text(-0.02, n - 1 - i + 0.5, str(i + 1),
                ha="right", va="center", fontsize=11, fontweight="bold",
                color=BORDER_COLOR)

    # draw queens
    if placement:
        for r in visible_rows:
            c = placement[r]
            is_current_step = (step is not None and r == step)
            color = STEP_QUEEN_COLOR if is_current_step else PLACED_QUEEN_COLOR

            # queen body — circle + crown
            ax.add_patch(plt.Circle(
                (c + 0.5, n - 1 - r + 0.5), 0.32,
                facecolor=color, edgecolor="white", linewidth=2, zorder=5,
            ))
            ax.text(
                c + 0.5, n - 1 - r + 0.5, "♛",
                ha="center", va="center", fontsize=22,
                color="white", fontweight="bold", zorder=6,
            )

            # step number
            if step is not None:
                ax.text(
                    c + 0.85, n - 1 - r + 0.15, str(r + 1),
                    ha="center", va="center", fontsize=8,
                    color=color, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white",
                              ec=color, lw=0.8),
                    zorder=7,
                )

    # title
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", color=HEADER_BG,
                      pad=12)

    fig.tight_layout()
    return fig


# ── Gradio callbacks ────────────────────────────────────────────────────────

def solve_and_show(n: int, show_attacks: bool):
    """Solve for given N, display first solution and stats."""
    start = time.perf_counter()
    solutions = _get_solutions(int(n))
    elapsed = time.perf_counter() - start

    if not solutions:
        fig = _draw_board(int(n), title=f"No solutions for {int(n)}×{int(n)}")
        return fig, "No solutions found.", 1, 1, ""

    placement = solutions[0]
    title = f"{int(n)}-Queens  —  Solution 1 / {len(solutions)}"
    fig = _draw_board(int(n), placement, show_attacks=show_attacks, title=title)

    stats = (
        f"### 📊 Statistics\n"
        f"- **Board size:** {int(n)} × {int(n)}\n"
        f"- **Total solutions:** {len(solutions)}\n"
        f"- **Solve time:** {elapsed * 1000:.2f} ms\n"
        f"- **Algorithm:** Bitmask DP (backtracking with bitmask pruning)\n"
    )

    solution_text = _format_solution(int(n), placement, 1, len(solutions))

    return fig, stats, 1, int(n), solution_text


def navigate(n: int, current_idx: int, direction: str, show_attacks: bool):
    """Move to the previous / next solution."""
    solutions = _get_solutions(int(n))
    if not solutions:
        return _draw_board(int(n)), 1, ""

    idx = int(current_idx)
    if direction == "prev":
        idx = max(1, idx - 1)
    elif direction == "next":
        idx = min(len(solutions), idx + 1)
    elif direction == "first":
        idx = 1
    elif direction == "last":
        idx = len(solutions)

    placement = solutions[idx - 1]
    title = f"{int(n)}-Queens  —  Solution {idx} / {len(solutions)}"
    fig = _draw_board(int(n), placement, show_attacks=show_attacks, title=title)
    solution_text = _format_solution(int(n), placement, idx, len(solutions))
    return fig, idx, solution_text


def step_through(n: int, current_idx: int, step: int, show_attacks: bool):
    """Show queen placement up to the given step (row)."""
    solutions = _get_solutions(int(n))
    if not solutions:
        return _draw_board(int(n)), ""

    idx = max(1, min(int(current_idx), len(solutions)))
    placement = solutions[idx - 1]
    step = int(step)

    if step < 0:
        title = f"{int(n)}-Queens  —  Empty board"
        fig = _draw_board(int(n), show_attacks=False, title=title)
        step_text = "**Step 0:** Empty board — no queens placed yet."
    else:
        row = min(step, int(n) - 1)
        title = f"{int(n)}-Queens  —  Step {row + 1} / {int(n)}"
        fig = _draw_board(int(n), placement, step=row,
                          show_attacks=show_attacks, title=title)
        step_text = _format_step(int(n), placement, row)

    return fig, step_text


def _format_solution(n: int, placement: List[int], idx: int, total: int) -> str:
    lines = [f"### 🏆 Solution {idx} of {total}\n"]
    lines.append("| Row | Column | Square |")
    lines.append("|:---:|:------:|:------:|")
    for r, c in enumerate(placement):
        square = f"{chr(ord('a') + c)}{r + 1}"
        lines.append(f"| {r + 1} | {c + 1} | {square} |")
    return "\n".join(lines)


def _format_step(n: int, placement: List[int], step: int) -> str:
    lines = [f"### 🔍 Step {step + 1} of {n}\n"]
    lines.append(f"Place queen on **row {step + 1}**, "
                 f"**column {placement[step] + 1}** "
                 f"(square {chr(ord('a') + placement[step])}{step + 1})\n")
    if step < n - 1:
        lines.append(f"*{n - step - 1} queens remaining…*")
    else:
        lines.append("✅ **All queens placed — solution complete!**")
    return "\n".join(lines)


# ── Build the Gradio UI ────────────────────────────────────────────────────

DESCRIPTION = """
# ♛ N-Queens Solver

Place **N** queens on an **N×N** chessboard so that no two queens threaten each other.
Uses a **bitmask dynamic programming** approach for fast enumeration of all solutions.

**How to use:**
1. Select a board size (5 – 8)
2. Click **Solve** to find all solutions
3. Navigate between solutions with ◀ / ▶
4. Use the **step slider** to watch queens placed one-by-one
5. Toggle **Show attacks** to see threatened squares
"""

with gr.Blocks(title="N-Queens Solver") as app:

    gr.Markdown(DESCRIPTION)

    with gr.Row():
        # ── left panel: controls ────────────────────────────────────
        with gr.Column(scale=1, min_width=300):
            gr.Markdown("### ⚙️ Controls")

            board_size = gr.Slider(
                minimum=5, maximum=8, step=1, value=8,
                label="Board size (N)",
                info="Choose N for an N×N board",
            )
            show_attacks = gr.Checkbox(
                label="Show attacked squares",
                value=False,
                info="Highlight squares under attack",
            )
            solve_btn = gr.Button("♛  Solve", variant="primary", size="lg")

            stats_md = gr.Markdown("*Click Solve to begin.*")

            gr.Markdown("---")
            gr.Markdown("### 🔄 Navigate Solutions")

            with gr.Row(elem_classes="solution-nav"):
                first_btn = gr.Button("⏮", size="sm", min_width=50)
                prev_btn = gr.Button("◀ Prev", size="sm")
                solution_idx = gr.Number(
                    value=1, label="Solution #", precision=0,
                    minimum=1, interactive=True,
                )
                next_btn = gr.Button("Next ▶", size="sm")
                last_btn = gr.Button("⏭", size="sm", min_width=50)

            gr.Markdown("---")
            gr.Markdown("### 🚶 Step-by-Step", elem_classes="step-section")

            step_slider = gr.Slider(
                minimum=-1, maximum=7, step=1, value=-1,
                label="Placement step",
                info="Slide to watch queens placed row by row (-1 = full solution)",
            )
            step_md = gr.Markdown("")

        # ── right panel: board visualisation ────────────────────────
        with gr.Column(scale=2, min_width=500):
            board_plot = gr.Plot(label="Chessboard")
            solution_md = gr.Markdown("")

    # hidden state for max slider value
    max_n = gr.State(8)

    # ── events ──────────────────────────────────────────────────────

    def _update_step_slider(n):
        return gr.update(maximum=int(n) - 1, value=-1)

    def _on_solve(n, attacks):
        fig, stats, idx, board_n, sol_text = solve_and_show(n, attacks)
        return (
            fig, stats, idx, board_n, sol_text,
            gr.update(maximum=int(n) - 1, value=-1), ""
        )

    solve_btn.click(
        fn=_on_solve,
        inputs=[board_size, show_attacks],
        outputs=[board_plot, stats_md, solution_idx, max_n,
                 solution_md, step_slider, step_md],
    )

    def _nav(n, idx, direction, attacks):
        fig, new_idx, sol_text = navigate(n, idx, direction, attacks)
        return fig, new_idx, sol_text, gr.update(value=-1), ""

    for btn, direction in [
        (prev_btn, "prev"), (next_btn, "next"),
        (first_btn, "first"), (last_btn, "last"),
    ]:
        btn.click(
            fn=_nav,
            inputs=[board_size, solution_idx, gr.State(direction), show_attacks],
            outputs=[board_plot, solution_idx, solution_md, step_slider, step_md],
        )

    def _on_step(n, idx, step, attacks):
        if int(step) < 0:
            # show full solution
            solutions = _get_solutions(int(n))
            if solutions:
                i = max(0, min(int(idx) - 1, len(solutions) - 1))
                placement = solutions[i]
                title = f"{int(n)}-Queens  —  Solution {i + 1} / {len(solutions)}"
                fig = _draw_board(int(n), placement, show_attacks=attacks,
                                  title=title)
                return fig, ""
            return _draw_board(int(n)), ""
        return step_through(n, idx, step, attacks)

    step_slider.change(
        fn=_on_step,
        inputs=[board_size, solution_idx, step_slider, show_attacks],
        outputs=[board_plot, step_md],
    )

    show_attacks.change(
        fn=_on_step,
        inputs=[board_size, solution_idx, step_slider, show_attacks],
        outputs=[board_plot, step_md],
    )

    # ── launch ──────────────────────────────────────────────────────

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="orange",
        ),
        css="""
        .solution-nav { display: flex; gap: 8px; align-items: center; }
        .step-section { border-top: 1px solid #ddd; padding-top: 12px; margin-top: 8px; }
        """,
    )
