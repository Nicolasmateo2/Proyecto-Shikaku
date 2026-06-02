from __future__ import annotations

"""Generación de rectángulos candidatos.

Dada una pista con valor A, el rectángulo asignado debe cumplir área == A.
Por eso el solver precomputa todos los rectángulos posibles para cada pista
("candidatos") y luego realiza una búsqueda con backtracking.

Este módulo es clave para el rendimiento:
- Reduce el espacio de búsqueda desde el inicio.
- Codifica la regla del Shikaku: "exactamente 1 pista por rectángulo".
"""

from typing import Dict, Iterable, List, Tuple

from .domain import Board, Clue, Rect


def factor_pairs(area: int) -> Iterable[Tuple[int, int]]:
    """Genera pares (alto, ancho) tales que alto*ancho == area."""

    if area <= 0:
        return
    h = 1
    while h * h <= area:
        if area % h == 0:
            w = area // h
            yield (h, w)
            if w != h:
                yield (w, h)
        h += 1


def generate_candidates_for_clue(board: Board, clue: Clue) -> List[Rect]:
    """Genera todos los rectángulos válidos para una pista.

    Un rectángulo es candidato válido para `clue` si:
    - su área es exactamente `clue.area`
    - está dentro de los límites del tablero
    - contiene la celda de la pista
    - NO contiene ninguna otra pista

    Esta última regla garantiza "exactamente una pista por rectángulo".
    """

    r0, c0 = clue.row, clue.col
    candidates: list[Rect] = []

    for h, w in factor_pairs(clue.area):
        # Colocar un rectángulo de tamaño h x w de forma que (r0,c0) quede dentro.
        # r1 puede variar tal que r1 <= r0 <= r1+h-1 -> r1 en [r0-h+1, r0]
        for r1 in range(r0 - h + 1, r0 + 1):
            r2 = r1 + h - 1
            if r1 < 0 or r2 >= board.n_rows:
                continue
            for c1 in range(c0 - w + 1, c0 + 1):
                c2 = c1 + w - 1
                if c1 < 0 or c2 >= board.n_cols:
                    continue

                rect = Rect(r1=r1, c1=c1, r2=r2, c2=c2)

                # Verificar que no contenga otras pistas
                ok = True
                for other in board.clues:
                    if other == clue:
                        continue
                    if rect.contains(other.cell):
                        ok = False
                        break
                if ok:
                    candidates.append(rect)

    # Deduplicar (por si se generó algún repetido)
    uniq = list(dict.fromkeys(candidates))
    return uniq


def generate_all_candidates(board: Board) -> Dict[Clue, List[Rect]]:
    """Retorna un diccionario: pista -> lista de rectángulos candidatos."""

    mp: dict[Clue, list[Rect]] = {}
    for clue in board.clues:
        mp[clue] = generate_candidates_for_clue(board, clue)
    return mp
