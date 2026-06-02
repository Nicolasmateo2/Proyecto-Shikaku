from __future__ import annotations

"""Exportación de tableros a TXT.

Este módulo lo usa la GUI para guardar tableros en la carpeta `boards/`.
Guardar tableros facilita:
- incluir instancias de prueba en el informe
- repetir una demo de manera determinista en la sustentación
"""

from pathlib import Path

from .domain import Board


def board_to_txt(board: Board) -> str:
    """Serializa un Board al formato TXT del proyecto."""

    lines: list[str] = [f"{board.n_rows} {board.n_cols}"]
    for r in range(board.n_rows):
        lines.append(" ".join(str(board.grid[r][c]) for c in range(board.n_cols)))
    lines.append("")
    return "\n".join(lines)


def save_board_to_boards(board: Board, filename: str) -> Path:
    """Guarda un tablero como TXT dentro de ./boards.

    filename debe terminar en .txt
    """

    if not filename.endswith(".txt"):
        raise ValueError("filename must end with .txt")

    boards_dir = Path("boards")
    boards_dir.mkdir(parents=True, exist_ok=True)
    path = boards_dir / filename
    path.write_text(board_to_txt(board), encoding="utf-8")
    return path
