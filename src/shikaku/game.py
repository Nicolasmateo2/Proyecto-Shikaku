from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .domain import Board, Clue, Rect
from .validate import covers_all_cells, rect_overlaps_any, rects_overlap


@dataclass(slots=True)
class TryAddResult:
    ok: bool
    message: str = ""


@dataclass(slots=True)
class GameState:
    board: Board
    player_rects: List[Rect] = field(default_factory=list)

    def clear(self) -> None:
        self.player_rects.clear()

    def _clues_inside(self, rect: Rect) -> List[Clue]:
        return [cl for cl in self.board.clues if rect.contains(cl.cell)]

    def try_add_rect(self, rect: Rect) -> TryAddResult:
        # Basic sanity
        if rect.r1 > rect.r2 or rect.c1 > rect.c2:
            return TryAddResult(False, "Rectángulo inválido")

        # Overlap
        if rect_overlaps_any(rect, self.player_rects):
            return TryAddResult(False, "El rectángulo se solapa con otro")

        clues = self._clues_inside(rect)
        if len(clues) == 0:
            return TryAddResult(False, "El rectángulo no contiene ninguna pista")
        if len(clues) > 1:
            return TryAddResult(False, "El rectángulo contiene más de una pista")

        clue = clues[0]
        if rect.area() != clue.area:
            return TryAddResult(False, f"Área incorrecta: debe ser {clue.area}")

        self.player_rects.append(rect)
        return TryAddResult(True, "OK")

    def try_remove_rect_at(self, row: int, col: int) -> bool:
        """Remove the top-most rectangle containing (row,col)."""
        for i in range(len(self.player_rects) - 1, -1, -1):
            if self.player_rects[i].contains((row, col)):
                self.player_rects.pop(i)
                return True
        return False

    def is_win(self) -> bool:
        # Quick check: no overlaps (should be guaranteed) and full coverage
        return covers_all_cells(self.board, self.player_rects)
