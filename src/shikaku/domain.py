from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


Cell = Tuple[int, int]  # (row, col)


@dataclass(frozen=True, slots=True)
class Clue:
    """A numbered cell (row, col) with a required area."""

    row: int
    col: int
    area: int

    @property
    def cell(self) -> Cell:
        return (self.row, self.col)


@dataclass(frozen=True, slots=True)
class Rect:
    """Inclusive rectangle defined by (r1,c1) top-left and (r2,c2) bottom-right."""

    r1: int
    c1: int
    r2: int
    c2: int

    def height(self) -> int:
        return self.r2 - self.r1 + 1

    def width(self) -> int:
        return self.c2 - self.c1 + 1

    def area(self) -> int:
        return self.height() * self.width()

    def contains(self, cell: Cell) -> bool:
        r, c = cell
        return self.r1 <= r <= self.r2 and self.c1 <= c <= self.c2

    def cells(self) -> Iterable[Cell]:
        for r in range(self.r1, self.r2 + 1):
            for c in range(self.c1, self.c2 + 1):
                yield (r, c)


@dataclass(slots=True)
class Board:
    """Board holds grid and clues.

    grid: list[list[int]] where 0 = empty, >0 = clue area.
    """

    n_rows: int
    n_cols: int
    grid: List[List[int]]
    clues: List[Clue]

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.n_rows and 0 <= c < self.n_cols

    def clue_at(self, r: int, c: int) -> Optional[Clue]:
        v = self.grid[r][c]
        if v <= 0:
            return None
        for clue in self.clues:
            if clue.row == r and clue.col == c:
                return clue
        return None
