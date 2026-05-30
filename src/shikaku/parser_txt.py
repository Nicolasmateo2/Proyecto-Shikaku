from __future__ import annotations

from pathlib import Path

from .domain import Board, Clue


def parse_board_txt(path: str | Path) -> Board:
    """Parse a Shikaku board from a TXT file.

    Format:
      First line: N M
      Next N lines: M integers separated by spaces
      0 = empty, >0 = clue area
    """

    p = Path(path)
    raw_lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not raw_lines:
        raise ValueError("Empty board file")

    header = raw_lines[0].split()
    if len(header) != 2:
        raise ValueError("First line must be: N M")

    n_rows, n_cols = map(int, header)
    if n_rows <= 0 or n_cols <= 0:
        raise ValueError("N and M must be positive")

    if len(raw_lines) - 1 != n_rows:
        raise ValueError(f"Expected {n_rows} row lines, got {len(raw_lines) - 1}")

    grid: list[list[int]] = []
    clues: list[Clue] = []

    for r in range(n_rows):
        parts = raw_lines[1 + r].split()
        if len(parts) != n_cols:
            raise ValueError(f"Row {r} expected {n_cols} columns, got {len(parts)}")
        row_vals = list(map(int, parts))
        grid.append(row_vals)
        for c, v in enumerate(row_vals):
            if v > 0:
                clues.append(Clue(row=r, col=c, area=v))

    return Board(n_rows=n_rows, n_cols=n_cols, grid=grid, clues=clues)
