from __future__ import annotations

"""Solucionador automático de Shikaku.

Este módulo implementa la técnica principal del proyecto:
- Generar candidatos por pista (ver candidates.py)
- Búsqueda con backtracking para escoger 1 rectángulo por pista
- Poda temprana cuando los rectángulos se solapan
- Heurística simple (MRV): resolver primero las pistas con menos candidatos

También retorna estadísticas para el informe/demo:
- nodos explorados
- podas por solape
- tiempo de ejecución
"""

from dataclasses import dataclass
from typing import Dict, List

from .candidates import generate_all_candidates
from .domain import Board, Clue, Rect
from .validate import covers_all_cells, rect_overlaps_any, validate_board_basic


@dataclass(slots=True)
class SolveStats:
    """Estadísticas de ejecución de la búsqueda."""

    nodes: int = 0
    pruned_overlap: int = 0


@dataclass(slots=True)
class SolveResult:
    """Resultado del intento de resolver un tablero."""

    success: bool
    rects_by_clue: Dict[Clue, Rect]
    message: str = ""
    stats: SolveStats | None = None
    elapsed_ms: float | None = None

    @property
    def rects(self) -> List[Rect]:
        """Atajo: lista de rectángulos de la solución."""

        return list(self.rects_by_clue.values())


def solve(board: Board) -> SolveResult:
    """Resuelve Shikaku con backtracking + poda.

    Estrategia (alto nivel):
    1) Validar tablero (condición necesaria): suma(pistas) == N*M
    2) Precomputar candidatos por pista
    3) Ordenar pistas por número de candidatos (heurística MRV)
    4) Backtracking colocando rectángulos sin solapamiento
    5) Aceptar sólo soluciones que cubran todas las celdas
    """

    import time

    t0 = time.perf_counter()
    stats = SolveStats()

    ok, msg = validate_board_basic(board)
    if not ok:
        return SolveResult(success=False, rects_by_clue={}, message=msg, stats=stats, elapsed_ms=0.0)

    cand = generate_all_candidates(board)

    # Si alguna pista no tiene candidatos, el tablero es irresoluble.
    for clue, rects in cand.items():
        if not rects:
            elapsed = (time.perf_counter() - t0) * 1000
            return SolveResult(
                success=False,
                rects_by_clue={},
                message="Hay una pista sin rectángulos candidatos.",
                stats=stats,
                elapsed_ms=elapsed,
            )

    # Heurística MRV: resolver primero las pistas más restringidas.
    clues = sorted(board.clues, key=lambda c: len(cand[c]))

    placed: list[Rect] = []
    rects_by_clue: dict[Clue, Rect] = {}

    def bt(i: int) -> bool:
        """Recursión de backtracking.

        i es el índice dentro de la lista de pistas ordenada.
        """

        stats.nodes += 1

        # Caso base: ya se asignó un rectángulo a cada pista.
        if i == len(clues):
            # Debe cubrir toda la grilla (sin huecos)
            return covers_all_cells(board, placed)

        clue = clues[i]

        # Probar cada rectángulo candidato para esta pista.
        for rect in cand[clue]:
            # Poda: descartar de inmediato si se solapa con lo ya colocado.
            if rect_overlaps_any(rect, placed):
                stats.pruned_overlap += 1
                continue

            placed.append(rect)
            rects_by_clue[clue] = rect

            if bt(i + 1):
                return True

            # Deshacer y probar siguiente candidato.
            placed.pop()
            rects_by_clue.pop(clue, None)

        return False

    ok2 = bt(0)
    elapsed = (time.perf_counter() - t0) * 1000

    if not ok2:
        return SolveResult(
            success=False,
            rects_by_clue={},
            message="No se encontró solución que pavimente toda la grilla.",
            stats=stats,
            elapsed_ms=elapsed,
        )

    return SolveResult(success=True, rects_by_clue=dict(rects_by_clue), message="OK", stats=stats, elapsed_ms=elapsed)
