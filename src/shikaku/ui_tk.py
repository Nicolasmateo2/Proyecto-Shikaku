from __future__ import annotations

import colorsys
import tkinter as tk
from tkinter import filedialog, messagebox

from .domain import Rect
from .parser_txt import parse_board_txt
from .solver import solve
from .validate import validate_board_basic


def _pastel_color(i: int, n: int) -> str:
    """Generate a pastel-ish hex color."""
    if n <= 0:
        n = 1
    h = (i % n) / n
    s = 0.35
    v = 0.98
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


class ShikakuApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Shikaku - GUI mínima")

        self.board = None
        self.solution_rects: list[Rect] = []

        self.cell_size = 42
        self.pad = 10

        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(toolbar, text="Cargar TXT", command=self.load_txt)
        btn_load.pack(side=tk.LEFT, padx=6, pady=6)

        self.btn_solve = tk.Button(toolbar, text="Resolver", command=self.solve_and_draw, state=tk.DISABLED)
        self.btn_solve.pack(side=tk.LEFT, padx=6, pady=6)

        self.status = tk.StringVar(value="Carga un tablero TXT")
        lbl = tk.Label(toolbar, textvariable=self.status, anchor="w")
        lbl.pack(side=tk.LEFT, padx=10)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bind("<Configure>", lambda e: self.redraw())

    def load_txt(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecciona un tablero TXT",
            filetypes=[("Text files", "*.txt"), ("All files", "*")],
        )
        if not path:
            return
        try:
            board = parse_board_txt(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el tablero:\n{e}")
            self.board = None
            self.solution_rects = []
            self.btn_solve.config(state=tk.DISABLED)
            self.status.set("Error al cargar")
            return

        ok, msg = validate_board_basic(board)
        if not ok:
            messagebox.showwarning("Tablero inválido", msg)
            self.board = board  # still show it
            self.solution_rects = []
            self.btn_solve.config(state=tk.DISABLED)
            self.status.set("Tablero inválido")
            self.redraw()
            return

        self.board = board
        self.solution_rects = []
        self.btn_solve.config(state=tk.NORMAL)
        self.status.set(f"Tablero cargado: {self.board.n_rows}x{self.board.n_cols} | pistas: {len(self.board.clues)}")
        self.redraw()

    def solve_and_draw(self) -> None:
        if self.board is None:
            return

        self.status.set("Resolviendo...")
        self.update_idletasks()

        res = solve(self.board)
        if not res.success:
            self.solution_rects = []
            self.redraw()
            messagebox.showwarning("Sin solución", res.message or "No se encontró solución.")
            self.status.set("Sin solución")
            return

        self.solution_rects = res.rects
        self.redraw()
        self.status.set("Resuelto")

    def redraw(self) -> None:
        self.canvas.delete("all")
        if self.board is None:
            return

        n, m = self.board.n_rows, self.board.n_cols
        s = self.cell_size
        x0, y0 = self.pad, self.pad

        width = x0 * 2 + m * s
        height = y0 * 2 + n * s
        self.canvas.config(scrollregion=(0, 0, width, height))

        # Draw filled solution rectangles first (so grid lines and numbers are on top)
        for i, rect in enumerate(self.solution_rects):
            fill = _pastel_color(i, max(1, len(self.solution_rects)))
            x1 = x0 + rect.c1 * s
            y1 = y0 + rect.r1 * s
            x2 = x0 + (rect.c2 + 1) * s
            y2 = y0 + (rect.r2 + 1) * s
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#333", width=3, fill=fill)

        # Draw grid cells and clues
        for r in range(n):
            for c in range(m):
                x1 = x0 + c * s
                y1 = y0 + r * s
                x2 = x1 + s
                y2 = y1 + s
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#888")

                v = self.board.grid[r][c]
                if v > 0:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=str(v),
                        fill="#111",
                        font=("TkDefaultFont", 12, "bold"),
                    )


def main() -> None:
    app = ShikakuApp()
    app.minsize(420, 320)
    app.mainloop()


if __name__ == "__main__":
    main()
