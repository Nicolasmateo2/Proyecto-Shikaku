from __future__ import annotations

"""Generación de tableros.

El generador crea tableros *resolubles* por construcción:
1) Genera una teselación aleatoria del tablero en rectángulos.
2) Coloca exactamente una pista en cada rectángulo con valor = área del rectángulo.

Esto garantiza al menos una solución (la teselación original), aunque puede no
ser única.

La dificultad es una heurística: controla cuántas piezas (rectángulos) se usan,
lo que influye en el número típico de candidatos del solver.
"""

import random
from dataclasses import dataclass
from typing import List, Optional

from .domain import Board, Clue, Rect


@dataclass(frozen=True, slots=True)
class GenConfig:
    n_rows: int
    n_cols: int
    target_pieces: int
    seed: Optional[int] = None


def _split_rect(rect: Rect, rng: random.Random) -> Optional[tuple[Rect, Rect]]:
    """Divide un rectángulo en dos (si es posible), eligiendo un corte aleatorio."""

    h = rect.height()
    w = rect.width()

    possible: list[str] = []
    if h >= 2:
        possible.append("H")
    if w >= 2:
        possible.append("V")
    if not possible:
        return None

    axis = rng.choice(possible)
    if axis == "H":
        # Corte horizontal: elegir altura superior en [1, h-1]
        cut = rng.randint(1, h - 1)
        r_top = Rect(rect.r1, rect.c1, rect.r1 + cut - 1, rect.c2)
        r_bot = Rect(rect.r1 + cut, rect.c1, rect.r2, rect.c2)
        return r_top, r_bot
    else:
        # Corte vertical
        cut = rng.randint(1, w - 1)
        r_left = Rect(rect.r1, rect.c1, rect.r2, rect.c1 + cut - 1)
        r_right = Rect(rect.r1, rect.c1 + cut, rect.r2, rect.c2)
        return r_left, r_right


def generate_tessellation(cfg: GenConfig) -> List[Rect]:
    """Genera una teselación aleatoria como lista de rectángulos sin solapamiento.

    Algoritmo: iniciar con el rectángulo de todo el tablero y partir rectángulos
    aleatoriamente hasta llegar a target_pieces (o hasta que no se pueda partir más).

    Se usa para construir un puzzle resoluble.
    """

    if cfg.n_rows <= 0 or cfg.n_cols <= 0:
        raise ValueError("n_rows and n_cols must be > 0")
    if cfg.target_pieces <= 0:
        raise ValueError("target_pieces must be > 0")

    rng = random.Random(cfg.seed)

    rects: list[Rect] = [Rect(0, 0, cfg.n_rows - 1, cfg.n_cols - 1)]

    # Guardia para evitar bucles infinitos si target_pieces es demasiado grande
    max_iters = cfg.target_pieces * 50
    it = 0

    while len(rects) < cfg.target_pieces and it < max_iters:
        it += 1

        # Preferir partir rectángulos grandes
        rects_sorted = sorted(rects, key=lambda r: r.area(), reverse=True)
        # Elegir entre los primeros para mantener aleatoriedad
        top_k = min(5, len(rects_sorted))
        victim = rng.choice(rects_sorted[:top_k])

        split = _split_rect(victim, rng)
        if split is None:
            continue

        a, b = split
        rects.remove(victim)
        rects.extend([a, b])

    return rects


def puzzle_from_tessellation(n_rows: int, n_cols: int, rects: List[Rect], seed: Optional[int] = None) -> Board:
    """Crea un puzzle (Board) a partir de una teselación.

    Coloca exactamente una pista (área) en una celda aleatoria dentro de cada rectángulo.
    """

    rng = random.Random(seed)

    grid = [[0 for _ in range(n_cols)] for _ in range(n_rows)]
    clues: list[Clue] = []

    for rect in rects:
        # Elegir una celda aleatoria dentro del rectángulo para ubicar la pista.
        rr = rng.randint(rect.r1, rect.r2)
        cc = rng.randint(rect.c1, rect.c2)
        area = rect.area()
        grid[rr][cc] = area
        clues.append(Clue(row=rr, col=cc, area=area))

    return Board(n_rows=n_rows, n_cols=n_cols, grid=grid, clues=clues)


def generate_puzzle(n_rows: int, n_cols: int, difficulty: str, seed: Optional[int] = None) -> Board:
    """Genera un puzzle aleatorio resoluble.

    `difficulty` controla (heurísticamente) la cantidad objetivo de rectángulos:
    - easy   -> menos rectángulos (más grandes)
    - medium -> más rectángulos
    - hard   -> aún más rectángulos (típicamente más restringido)

    Nota: NO se garantiza unicidad de la solución.
    """

    # Mapeo heurístico dificultad -> número de piezas.
    total = n_rows * n_cols
    if difficulty == "easy":
        target = max(2, total // 6)
    elif difficulty == "medium":
        target = max(3, total // 5)
    else:  # "hard"
        target = max(4, total // 4)

    cfg = GenConfig(n_rows=n_rows, n_cols=n_cols, target_pieces=target, seed=seed)
    rects = generate_tessellation(cfg)
    return puzzle_from_tessellation(n_rows, n_cols, rects, seed=seed)
