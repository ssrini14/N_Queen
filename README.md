# ♛ N-Queens Solver

An interactive, visual explorer for the classic **N-Queens problem** — place _N_ queens on an _N×N_ chessboard so that no two queens threaten each other. Powered by a **bitmask dynamic-programming** solver and a **Gradio** web UI with step-by-step animation.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)
![Algorithm](https://img.shields.io/badge/Algorithm-Bitmask%20DP-green)

---

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Algorithm Details](#algorithm-details)
- [Color Legend](#color-legend)
- [Configuration](#configuration)
- [License](#license)

---

## Features

- **Board sizes 5×5 through 8×8** — solve and visualize all valid queen placements
- **Interactive Gradio web UI** — no frontend code needed; runs in any browser
- **Solution navigation** — browse through every solution with ◀ ▶ ⏮ ⏭ controls
- **Step-by-step animation** — slide through queen placements row by row
- **Attack visualization** — toggle highlighting of attacked (light red) and safe (light green) squares
- **Performance stats** — see solve time, total solution count, and placement details
- **Solution caching** — solutions are computed once and reused across interactions
- **ASCII board output** — run the solver standalone for terminal-based exploration

---

## Demo

| Full Solution | Attack Visualization | Step-by-Step |
|:---:|:---:|:---:|
| 8 queens placed | Attacked squares in red, safe in green | Incremental placement |

---

## How It Works

1. **Select a board size** (5–8) and click **Solve**
2. The bitmask DP solver enumerates all valid placements
3. The first solution is rendered on an interactive chessboard
4. Navigate between solutions or step through placements one row at a time
5. Toggle **Show attacked squares** to see which squares are under threat

---

## Project Structure

```
n_queen/
├── app.py              # Gradio web application — UI, drawing, callbacks
├── n_queen_dp.py       # Core solver — bitmask DP backtracking algorithm
├── requirements.txt    # Python dependencies
├── uv.toml             # uv package manager configuration
└── README.md           # This file
```

### `n_queen_dp.py`

Contains the core solver and CLI helpers:

| Function | Description |
|---|---|
| `solve_n_queens(n)` | Returns all solutions as lists of column indices per row |
| `board_string(n, placement)` | Renders an ASCII chessboard for a single solution |
| `print_summary(n, solutions, elapsed)` | Prints solution count, timing, and example boards |
| `main()` | Solves for N = 5 through 8 and prints a summary table |

### `app.py`

Contains the Gradio-based interactive UI:

| Function | Description |
|---|---|
| `_draw_board(...)` | Renders the chessboard using Matplotlib with queens, attacks, and labels |
| `solve_and_show(n, show_attacks)` | Solves and displays the first solution with statistics |
| `navigate(n, idx, direction, ...)` | Moves to the previous/next/first/last solution |
| `step_through(n, idx, step, ...)` | Shows incremental queen placement up to a given row |

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

```bash
# Clone the repository
git clone https://github.com/ssrini14/ssrini14.github.io.git
cd n_queen

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

**Or with uv:**

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

---

## Usage

### Interactive Web UI (Gradio)

```bash
python app.py
```

Opens a local web server at **http://localhost:7861**. Use the controls to:

- Adjust board size (5–8) with the slider
- Click **♛ Solve** to compute all solutions
- Navigate between solutions with ◀ ▶ ⏮ ⏭
- Drag the **Step slider** to animate placement row by row
- Toggle **Show attacked squares** for attack/safe visualization

### Command-Line Solver

```bash
python n_queen_dp.py
```

Solves for board sizes 5 through 8 and prints ASCII boards + a summary table:

```
==================================================
  N = 8  |  92 solutions found  |  0.0012s
==================================================

  Solution 1:
      0  1  2  3  4  5  6  7
  +------------------------+
  0 | Q  .  .  .  .  .  .  . |
  1 | .  .  .  .  Q  .  .  . |
  ...
```

---

## Algorithm Details

The solver uses **backtracking with bitmask pruning**, processing one row at a time.

### State Representation

Three bitmasks track attacked positions, where each bit corresponds to a column:

| Bitmask | Tracks |
|---|---|
| `cols` | Columns already occupied by a queen |
| `left_diag` | Left-going diagonals (↙) under attack |
| `right_diag` | Right-going diagonals (↘) under attack |

### Core Logic

```
available = ALL_COLUMNS & ~(cols | left_diag | right_diag)
```

This single bitwise operation computes every safe column for the current row in **O(1)**.

For each safe column:
1. Isolate the lowest set bit: `bit = available & -available`
2. Place the queen and recurse to the next row with updated masks:
   - `cols | bit` — mark column occupied
   - `(left_diag | bit) << 1` — shift left diagonal attack one column left
   - `(right_diag | bit) >> 1` — shift right diagonal attack one column right
3. Backtrack by popping the placement

### Complexity

| Metric | Value |
|---|---|
| **Time** | O(N!) worst case — quickly pruned in practice |
| **Space** | O(N) recursion depth; state is just 3 integers |

### Known Solution Counts

| N | Solutions |
|:-:|:-:|
| 5 | 10 |
| 6 | 4 |
| 7 | 40 |
| 8 | 92 |

---

## Color Legend

When **Show attacked squares** is enabled:

| Color | Hex | Meaning |
|---|---|---|
| 🟫 Light tan | `#F0D9B5` | Light square (normal) |
| 🟫 Dark brown | `#B58863` | Dark square (normal) |
| 🔴 Light red | `#FFCDD2` | Square under attack by a queen |
| 🟢 Light green | `#C8E6C9` | Safe square (not attacked) |
| 🔵 Blue circle | `#1565C0` | Queen |

---

## Configuration

### Changing Board Size Range

Edit the slider in [app.py](app.py) (line ~274):

```python
board_size = gr.Slider(minimum=5, maximum=8, step=1, value=8, ...)
```

### Changing Colors

Edit the colour palette at the top of [app.py](app.py):

```python
LIGHT_SQ = "#F0D9B5"
DARK_SQ  = "#B58863"
ATTACK_COLOR = "#FFCDD2"
SAFE_COLOR   = "#C8E6C9"
```

### Server Settings

The app launches on `0.0.0.0:7861` by default. Modify at the bottom of [app.py](app.py):

```python
app.launch(server_name="0.0.0.0", server_port=7861, share=False)
```

Set `share=True` to create a public Gradio link.

---

## License

This project is open source. Feel free to use, modify, and distribute.
