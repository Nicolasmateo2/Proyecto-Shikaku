from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from .parser_txt import parse_board_txt


class ShikakuApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Shikaku - GUI mínima")

        self.board = None
        self.cell_size = 42
        self.pad = 10

        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(toolbar, text="Cargar TXT", command=self.load_txt)
        btn_load.pack(side=tk.LEFT, padx=6, pady=6)

        self.btn_solve = tk.Button(toolbar, text="Resolver", command=self.solve, state=tk.DISABLED)
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
            self.board = parse_board_txt(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el tablero:\n{e}")
            self.board = None
            self.btn_solve.config(state=tk.DISABLED)
            self.status.set("Error al cargar")
            return

        self.btn_solve.config(state=tk.NORMAL)
        self.status.set(
            f"Tablero cargado: {self.board.n_rows}x{self.board.n_cols} | pistas: {len(self.board.clues)}"
        )
        self.redraw()

    def solve(self) -> None:
        messagebox.showinfo("Resolver", "Solver aún no implementado. (Siguiente paso: backtracking)")

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
