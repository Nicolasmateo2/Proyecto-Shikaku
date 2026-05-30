from __future__ import annotations

from pathlib import Path

from src.shikaku.parser_txt import parse_board_txt
from src.shikaku.solver import solve
from src.shikaku.validate import covers_all_cells


def test_solver_facil_solves_and_tessellates() -> None:
    board = parse_board_txt(Path("boards/facil_5x5.txt"))
    res = solve(board)
    assert res.success, res.message
    assert covers_all_cells(board, res.rects)


def test_solver_medio_solves_and_tessellates() -> None:
    board = parse_board_txt(Path("boards/medio_6x6.txt"))
    res = solve(board)
    assert res.success, res.message
    assert covers_all_cells(board, res.rects)
