from __future__ import annotations

from pathlib import Path

from src.shikaku.parser_txt import parse_board_txt


def test_parse_board_txt_facil() -> None:
    board = parse_board_txt(Path("boards/facil_5x5.txt"))
    assert board.n_rows == 5
    assert board.n_cols == 5
    assert len(board.clues) == 6
