from __future__ import annotations

from pathlib import Path

from src.shikaku.parser_txt import parse_board_txt
from src.shikaku.solver import solve
from src.shikaku.validate import check_solution


def test_check_solution_accepts_solver_output() -> None:
    board = parse_board_txt(Path("boards/facil_5x5.txt"))
    res = solve(board)
    assert res.success
    chk = check_solution(board, res.rects)
    assert chk.ok, chk.message
