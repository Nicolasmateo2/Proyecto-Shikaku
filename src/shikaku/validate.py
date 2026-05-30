from __future__ import annotations

from typing import Iterable, Set, Tuple

from .domain import Board, Clue, Cell, Rect


def validate_board_basic(board: Board) -> tuple[bool, str]:
    """Basic board validity checks.

    These are necessary conditions for a valid Shikaku instance.
    """

    if board.n_rows <= 0 or board.n_cols <= 0:
        return False, "Dimensiones inválidas (N y M deben ser > 0)."

    if not board.clues:
        return False, "El tablero no contiene pistas (números)."

    for clue in board.clues:
        if clue.area <= 0:
            return False, f"Pista inválida en ({clue.row},{clue.col}): área <= 0."

    total_area = board.n_rows * board.n_cols
    sum_clues = sum(c.area for c in board.clues)
    if sum_clues != total_area:
        return (
            False,
            f"La suma de las pistas ({sum_clues}) no coincide con el área del tablero ({total_area}).",
        )

    return True, "OK"


def validate_board_or_raise(board: Board) -> None:
    ok, msg = validate_board_basic(board)
    if not ok:
        raise ValueError(msg)


def rect_in_bounds(board: Board, rect: Rect) -> bool:
    return 0 <= rect.r1 <= rect.r2 < board.n_rows and 0 <= rect.c1 <= rect.c2 < board.n_cols


def rect_contains_only_its_clue(board: Board, rect: Rect, clue: Clue) -> bool:
    """True if rect contains clue and no other clues."""
    if not rect.contains(clue.cell):
        return False
    for other in board.clues:
        if other == clue:
            continue
        if rect.contains(other.cell):
            return False
    return True


def rect_area_matches(rect: Rect, area: int) -> bool:
    return rect.area() == area


def rects_overlap(a: Rect, b: Rect) -> bool:
    # Separating axis: if one is completely left/right/up/down of other => no overlap
    if a.r2 < b.r1 or b.r2 < a.r1:
        return False
    if a.c2 < b.c1 or b.c2 < a.c1:
        return False
    return True


def rect_overlaps_any(rect: Rect, placed: Iterable[Rect]) -> bool:
    return any(rects_overlap(rect, r) for r in placed)


def covers_all_cells(board: Board, rects: Iterable[Rect]) -> bool:
    covered: Set[Cell] = set()
    for rect in rects:
        for cell in rect.cells():
            covered.add(cell)
    return len(covered) == board.n_rows * board.n_cols
