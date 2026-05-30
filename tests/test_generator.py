from __future__ import annotations

from src.shikaku.generator import generate_puzzle
from src.shikaku.solver import solve
from src.shikaku.validate import covers_all_cells, validate_board_basic


def test_generate_puzzle_is_valid_and_solvable() -> None:
    board = generate_puzzle(6, 6, "easy", seed=123)
    ok, msg = validate_board_basic(board)
    assert ok, msg

    res = solve(board)
    assert res.success, res.message
    assert covers_all_cells(board, res.rects)
