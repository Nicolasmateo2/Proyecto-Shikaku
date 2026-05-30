from __future__ import annotations

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
    """Randomly split rect into two rectangles, if possible."""

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
        # cut between rows: choose top height in [1, h-1]
        cut = rng.randint(1, h - 1)
        r_top = Rect(rect.r1, rect.c1, rect.r1 + cut - 1, rect.c2)
        r_bot = Rect(rect.r1 + cut, rect.c1, rect.r2, rect.c2)
        return r_top, r_bot
    else:
        cut = rng.randint(1, w - 1)
        r_left = Rect(rect.r1, rect.c1, rect.r2, rect.c1 + cut - 1)
        r_right = Rect(rect.r1, rect.c1 + cut, rect.r2, rect.c2)
        return r_left, r_right


def generate_tessellation(cfg: GenConfig) -> List[Rect]:
    """Generate a random tessellation of the board as a list of non-overlapping rectangles.

    Algorithm: start with the full board rectangle and repeatedly split random rectangles
    until reaching target_pieces (or no more splits are possible).
    """

    if cfg.n_rows <= 0 or cfg.n_cols <= 0:
        raise ValueError("n_rows and n_cols must be > 0")
    if cfg.target_pieces <= 0:
        raise ValueError("target_pieces must be > 0")

    rng = random.Random(cfg.seed)

    rects: list[Rect] = [Rect(0, 0, cfg.n_rows - 1, cfg.n_cols - 1)]

    # Guard to avoid infinite loops when target_pieces is too large
    max_iters = cfg.target_pieces * 50
    it = 0

    while len(rects) < cfg.target_pieces and it < max_iters:
        it += 1

        # Prefer splitting larger rectangles
        rects_sorted = sorted(rects, key=lambda r: r.area(), reverse=True)
        # Choose among the top few to keep randomness
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
    """Create a Shikaku puzzle (Board) from a tessellation.

    Places exactly one clue (area) in a random cell inside each rectangle.
    """

    rng = random.Random(seed)

    grid: list[list[int]] = [[0 for _ in range(n_cols)] for _ in range(n_rows)]
    clues: list[Clue] = []

    for rect in rects:
        area = rect.area()
        r = rng.randint(rect.r1, rect.r2)
        c = rng.randint(rect.c1, rect.c2)
        grid[r][c] = area
        clues.append(Clue(row=r, col=c, area=area))

    return Board(n_rows=n_rows, n_cols=n_cols, grid=grid, clues=clues)


def generate_puzzle(n_rows: int, n_cols: int, difficulty: str, seed: Optional[int] = None) -> Board:
    """Generate a resolvable Shikaku puzzle.

    difficulty: 'easy' | 'medium' | 'hard'

    Heuristic mapping (can be tuned):
      - easy: many smaller rectangles
      - medium: moderate number
      - hard: fewer larger rectangles
    """

    total = n_rows * n_cols
    diff = difficulty.lower().strip()

    if diff in ("facil", "fácil", "easy"):
        target = max(4, total // 4)  # many pieces
    elif diff in ("medio", "medium"):
        target = max(4, total // 6)
    elif diff in ("dificil", "difícil", "hard"):
        target = max(3, total // 9)  # fewer pieces
    else:
        raise ValueError("difficulty must be: easy|medium|hard (or facil|medio|dificil)")

    # Cap to avoid impossible targets (more rectangles than cells)
    target = min(target, total)

    rects = generate_tessellation(GenConfig(n_rows=n_rows, n_cols=n_cols, target_pieces=target, seed=seed))
    return puzzle_from_tessellation(n_rows, n_cols, rects, seed=seed)
