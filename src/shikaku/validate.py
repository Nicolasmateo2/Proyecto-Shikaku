from __future__ import annotations

"""Funciones de validación.

Este módulo centraliza chequeos de reglas para:
- validar un tablero de entrada (condiciones necesarias)
- validar solapamientos entre rectángulos
- validar una solución completa (usado por tests y por la GUI)

Tener estas reglas en un solo lugar mejora la correctitud y facilita explicar
la solución en el informe.
"""

from dataclasses import dataclass
from typing import Iterable, Set

from .domain import Board, Cell, Rect


def validate_board_basic(board: Board) -> tuple[bool, str]:
    """Validación básica del tablero (condiciones necesarias).

    Útil para fallar temprano y no ejecutar el solver sobre entradas imposibles:
    - N y M positivos
    - al menos una pista
    - pistas con área positiva
    - suma de pistas == N*M

    Nota: esto NO garantiza que exista solución, sólo que el tablero es consistente.
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


def rects_overlap(a: Rect, b: Rect) -> bool:
    """True si dos rectángulos comparten al menos una celda."""

    # Eje separador: si uno está totalmente arriba/abajo/izq/der del otro, no se solapan
    if a.r2 < b.r1 or b.r2 < a.r1:
        return False
    if a.c2 < b.c1 or b.c2 < a.c1:
        return False
    return True


def rect_overlaps_any(rect: Rect, placed: Iterable[Rect]) -> bool:
    """True si rect se solapa con algún rectángulo ya colocado."""

    return any(rects_overlap(rect, r) for r in placed)


def covers_all_cells(board: Board, rects: Iterable[Rect]) -> bool:
    """True si la unión de rectángulos cubre todas las celdas del tablero."""

    covered: Set[Cell] = set()
    for rect in rects:
        for cell in rect.cells():
            covered.add(cell)
    return len(covered) == board.n_rows * board.n_cols


@dataclass(frozen=True, slots=True)
class CheckResult:
    ok: bool
    message: str


def check_solution(board: Board, rects: Iterable[Rect]) -> CheckResult:
    """Valida una solución completa contra las reglas del Shikaku.

    Condiciones:
    - no solapamiento
    - cada rectángulo contiene exactamente 1 pista
    - área del rectángulo coincide con el número de la pista
    - los rectángulos cubren todo el tablero

    Se usa en:
    - pruebas automáticas
    - GUI, para confirmar que la salida del solver es correcta antes de mostrarla
    """

    rect_list = list(rects)

    # 1) Sin solapamientos
    for i in range(len(rect_list)):
        for j in range(i + 1, len(rect_list)):
            if rects_overlap(rect_list[i], rect_list[j]):
                return CheckResult(False, "La solución tiene rectángulos solapados")

    # 2) Exactamente una pista por rectángulo + área correcta
    for rect in rect_list:
        clues_inside = [cl for cl in board.clues if rect.contains(cl.cell)]
        if len(clues_inside) != 1:
            return CheckResult(False, "Un rectángulo no contiene exactamente una pista")
        clue = clues_inside[0]
        if rect.area() != clue.area:
            return CheckResult(False, "El área de un rectángulo no coincide con su pista")

    # 3) Cobertura total
    if not covers_all_cells(board, rect_list):
        return CheckResult(False, "La solución no pavimenta toda la grilla")

    return CheckResult(True, "OK")
