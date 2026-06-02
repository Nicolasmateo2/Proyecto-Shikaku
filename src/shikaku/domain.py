from __future__ import annotations

"""Modelos de dominio del proyecto Shikaku.

Este módulo contiene únicamente estructuras de datos simples.
La lógica algorítmica (candidatos/solver/validación) se implementa en otros módulos.

Conceptos clave:
- *Clue* (Pista): celda numerada que indica el área del rectángulo.
- *Rect* (Rectángulo): rectángulo alineado a la grilla que cubre un conjunto de celdas.
- *Board* (Tablero): grilla de números + lista de pistas.
"""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


Cell = Tuple[int, int]  # (fila, columna)


@dataclass(frozen=True, slots=True)
class Clue:
    """Una pista (fila, columna) con un área requerida."""

    row: int
    col: int
    area: int

    @property
    def cell(self) -> Cell:
        return (self.row, self.col)


@dataclass(frozen=True, slots=True)
class Rect:
    """Rectángulo inclusivo definido por (r1,c1) arriba-izquierda y (r2,c2) abajo-derecha.

    Las coordenadas son inclusivas: un rectángulo de 1x1 tiene r1==r2 y c1==c2.
    """

    r1: int
    c1: int
    r2: int
    c2: int

    def height(self) -> int:
        return self.r2 - self.r1 + 1

    def width(self) -> int:
        return self.c2 - self.c1 + 1

    def area(self) -> int:
        return self.height() * self.width()

    def contains(self, cell: Cell) -> bool:
        """Retorna True si la celda (fila,col) está dentro del rectángulo."""

        r, c = cell
        return self.r1 <= r <= self.r2 and self.c1 <= c <= self.c2

    def cells(self) -> Iterable[Cell]:
        """Itera todas las celdas cubiertas por este rectángulo."""

        for r in range(self.r1, self.r2 + 1):
            for c in range(self.c1, self.c2 + 1):
                yield (r, c)


@dataclass(slots=True)
class Board:
    """Tablero del Shikaku.

    - grid: list[list[int]] donde 0 = vacío, >0 = pista (área)
    - clues: lista de pistas extraídas de la grilla

    Nota: mantenemos `grid` y `clues` porque la GUI necesita acceso rápido
    para dibujar los números, mientras el solver trabaja sobre la lista de pistas.
    """

    n_rows: int
    n_cols: int
    grid: List[List[int]]
    clues: List[Clue]

    def in_bounds(self, r: int, c: int) -> bool:
        """True si (r,c) está dentro de los límites del tablero."""

        return 0 <= r < self.n_rows and 0 <= c < self.n_cols

    def clue_at(self, r: int, c: int) -> Optional[Clue]:
        """Retorna la pista en (r,c) si la celda está numerada."""

        v = self.grid[r][c]
        if v <= 0:
            return None
        for clue in self.clues:
            if clue.row == r and clue.col == c:
                return clue
        return None
