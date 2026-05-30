from __future__ import annotations

from pathlib import Path

from src.shikaku.parser_txt import parse_board_txt
from src.shikaku.validate import validate_board_basic


def test_validate_board_basic_ok() -> None:
    board = parse_board_txt(Path("boards/facil_5x5.txt"))
    ok, msg = validate_board_basic(board)
    assert ok, msg


def test_validate_board_basic_detects_bad_sum() -> None:
    board = parse_board_txt(Path("boards/sample_01.txt"))
    ok, msg = validate_board_basic(board)
    assert not ok
    assert "suma" in msg.lower() or "área" in msg.lower()
