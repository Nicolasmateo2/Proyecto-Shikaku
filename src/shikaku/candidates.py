from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from .domain import Board, Clue, Rect


def factor_pairs(area: int) -> Iterable[Tuple[int, int]]:
    """Yield (h, w) pairs such that h*w == area."""
    if area <= 0:
        return
    h = 1
    while h * h <= area:
        if area % h == 0:
            w = area // h
            yield (h, w)
            if w != h:
                yield (w, h)
        h += 1


def generate_candidates_for_clue(board: Board, clue: Clue) -> List[Rect]:
    """Generate all valid rectangles for a clue that:

    - have exactly clue.area
    - are within bounds
    - contain the clue cell
    - contain no other clue cells
    """

    r0, c0 = clue.row, clue.col
    candidates: list[Rect] = []

    for h, w in factor_pairs(clue.area):
        # Place rectangle of size h x w such that (r0,c0) lies inside.
        # r1 can range so that r1 <= r0 <= r1+h-1 -> r1 in [r0-h+1, r0]
        for r1 in range(r0 - h + 1, r0 + 1):
            r2 = r1 + h - 1
            if r1 < 0 or r2 >= board.n_rows:
                continue
            for c1 in range(c0 - w + 1, c0 + 1):
                c2 = c1 + w - 1
                if c1 < 0 or c2 >= board.n_cols:
                    continue

                rect = Rect(r1=r1, c1=c1, r2=r2, c2=c2)

                # Check it contains no other clues
                ok = True
                for other in board.clues:
                    if other == clue:
                        continue
                    if rect.contains(other.cell):
                        ok = False
                        break
                if ok:
                    candidates.append(rect)

    # Deduplicate (in case of any repeats)
    uniq = list(dict.fromkeys(candidates))
    return uniq


def generate_all_candidates(board: Board) -> Dict[Clue, List[Rect]]:
    """Return mapping from clue to list of candidate rectangles."""

    mp: dict[Clue, list[Rect]] = {}
    for clue in board.clues:
        mp[clue] = generate_candidates_for_clue(board, clue)
    return mp
