from __future__ import annotations

from pathlib import Path

from src.shikaku.game import GameState
from src.shikaku.parser_txt import parse_board_txt
from src.shikaku.domain import Rect


def test_game_rejects_rect_without_clue() -> None:
    board = parse_board_txt(Path("boards/facil_5x5.txt"))
    game = GameState(board)

    # pick a 1x1 rect somewhere that is likely not a clue cell
    rect = Rect(1, 1, 1, 1)
    res = game.try_add_rect(rect)
    assert not res.ok


def test_game_accepts_valid_rect_from_solution() -> None:
    board = parse_board_txt(Path("boards/facil_5x5.txt"))
    game = GameState(board)

    # Use the clue '1' at (2,1) in the provided easy board; its only valid rect is 1x1
    rect = Rect(2, 1, 2, 1)
    res = game.try_add_rect(rect)
    assert res.ok
