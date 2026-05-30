from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .candidates import generate_all_candidates
from .domain import Board, Clue, Rect
from .validate import covers_all_cells, rect_overlaps_any, validate_board_basic


@dataclass(slots=True)
class SolveResult:
    success: bool
    rects_by_clue: Dict[Clue, Rect]
    message: str = ""

    @property
    def rects(self) -> List[Rect]:
        return list(self.rects_by_clue.values())


def solve(board: Board) -> SolveResult:
    """Solve Shikaku via backtracking with pruning.

    Strategy:
    - Basic board validation (necessary condition): sum(clues) == N*M
    - Precompute candidates per clue
    - Sort clues by number of candidates ascending (MRV heuristic)
    - Backtrack placing non-overlapping rectangles
    - Accept only solutions that tessellate the entire board
    """

    ok, msg = validate_board_basic(board)
    if not ok:
        return SolveResult(success=False, rects_by_clue={}, message=msg)

    cand = generate_all_candidates(board)

    # If any clue has no candidates -> unsolvable
    for clue, rects in cand.items():
        if not rects:
            return SolveResult(success=False, rects_by_clue={}, message="Hay una pista sin rectángulos candidatos.")

    clues = sorted(board.clues, key=lambda c: len(cand[c]))

    placed: list[Rect] = []
    rects_by_clue: dict[Clue, Rect] = {}

    def bt(i: int) -> bool:
        if i == len(clues):
            # Require full tessellation
            return covers_all_cells(board, placed)

        clue = clues[i]
        for rect in cand[clue]:
            if rect_overlaps_any(rect, placed):
                continue
            placed.append(rect)
            rects_by_clue[clue] = rect
            if bt(i + 1):
                return True
            placed.pop()
            rects_by_clue.pop(clue, None)

        return False

    ok2 = bt(0)
    if not ok2:
        return SolveResult(success=False, rects_by_clue={}, message="No se encontró solución que pavimente toda la grilla.")

    return SolveResult(success=True, rects_by_clue=dict(rects_by_clue), message="OK")
