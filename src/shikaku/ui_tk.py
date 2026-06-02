from __future__ import annotations

"""Interfaz gráfica (Tkinter).

La GUI provee el mínimo requerido por el proyecto:
- Cargar un tablero desde TXT
- Generar un tablero aleatorio (N x M + dificultad)
- Permitir jugar dibujando rectángulos (arrastrar y soltar)
- Ejecutar el solver y mostrar la solución
- Exportar tableros a ./boards para pruebas reproducibles

Notas de diseño:
- "Ver solución" dibuja sólo el contorno para que el usuario pueda seguir jugando.
- "Resolver definitivo" pinta la solución y bloquea el modo juego.
- Antes de mostrar, se valida la salida del solver con check_solution().
"""

import colorsys
import datetime as _dt
import tkinter as tk
from tkinter import filedialog, messagebox

from .domain import Rect
from .game import GameState
from .generator import generate_puzzle
from .io_txt import save_board_to_boards
from .parser_txt import parse_board_txt
from .solver import solve
from .validate import check_solution, validate_board_basic


def _pastel_color(i: int, n: int) -> str:
    """Genera un color pastel (hex) para rellenar rectángulos."""

    if n <= 0:
        n = 1
    h = (i % n) / n
    s = 0.35
    v = 0.98
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _cell_from_xy(x: int, y: int, pad: int, cell_size: int) -> tuple[int, int] | None:
    """Convierte coordenadas del mouse a una celda (fila,col)."""

    x -= pad
    y -= pad
    if x < 0 or y < 0:
        return None
    c = x // cell_size
    r = y // cell_size
    return int(r), int(c)


def _rect_from_cells(a: tuple[int, int], b: tuple[int, int]) -> Rect:
    """Construye un rectángulo a partir de dos celdas (inicio y fin del arrastre)."""

    r1 = min(a[0], b[0])
    c1 = min(a[1], b[1])
    r2 = max(a[0], b[0])
    c2 = max(a[1], b[1])
    return Rect(r1=r1, c1=c1, r2=r2, c2=c2)


class ShikakuApp(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Shikaku - GUI mínima")

        self.board = None
        self.solution_rects: list[Rect] = []
        self.solution_mode: str = "none"  # 'none' | 'overlay' | 'final'
        self.game: GameState | None = None

        # Estado para arrastrar y dibujar rectángulos
        self.drag_start: tuple[int, int] | None = None
        self.drag_end: tuple[int, int] | None = None

        self.cell_size = 42
        self.pad = 10

        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(toolbar, text="Cargar TXT", command=self.load_txt)
        btn_load.pack(side=tk.LEFT, padx=6, pady=6)

        # Controles del generador
        gen_frame = tk.Frame(toolbar)
        gen_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(gen_frame, text="N:").pack(side=tk.LEFT)
        self.var_n = tk.StringVar(value="6")
        tk.Entry(gen_frame, textvariable=self.var_n, width=3).pack(side=tk.LEFT, padx=(2, 8))

        tk.Label(gen_frame, text="M:").pack(side=tk.LEFT)
        self.var_m = tk.StringVar(value="6")
        tk.Entry(gen_frame, textvariable=self.var_m, width=3).pack(side=tk.LEFT, padx=(2, 8))

        tk.Label(gen_frame, text="Dificultad:").pack(side=tk.LEFT)
        self.var_diff = tk.StringVar(value="Fácil")
        tk.OptionMenu(gen_frame, self.var_diff, "Fácil", "Medio", "Difícil").pack(side=tk.LEFT, padx=(2, 8))

        btn_gen = tk.Button(gen_frame, text="Generar", command=self.generate)
        btn_gen.pack(side=tk.LEFT)

        btn_save = tk.Button(toolbar, text="Guardar tablero", command=self.save_board, state=tk.DISABLED)
        btn_save.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_save = btn_save

        # Botones de solución
        self.btn_show_solution = tk.Button(
            toolbar, text="Ver solución", command=self.show_solution_overlay, state=tk.DISABLED
        )
        self.btn_show_solution.pack(side=tk.LEFT, padx=6, pady=6)

        self.btn_final_solution = tk.Button(
            toolbar, text="Resolver definitivo", command=self.show_solution_final, state=tk.DISABLED
        )
        self.btn_final_solution.pack(side=tk.LEFT, padx=6, pady=6)

        btn_clear = tk.Button(toolbar, text="Limpiar jugada", command=self.clear_play, state=tk.DISABLED)
        btn_clear.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_clear = btn_clear

        self.status = tk.StringVar(value="Carga o genera un tablero")
        lbl = tk.Label(toolbar, textvariable=self.status, anchor="w")
        lbl.pack(side=tk.LEFT, padx=10)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bindings del modo juego
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.bind("<Configure>", lambda e: self.redraw())

    def _set_board(self, board) -> None:
        """Carga un tablero en la GUI y reinicia estados internos."""

        ok, msg = validate_board_basic(board)
        if not ok:
            messagebox.showwarning("Tablero inválido", msg)
            self.board = board
            self.solution_rects = []
            self.solution_mode = "none"
            self.game = None
            self.btn_show_solution.config(state=tk.DISABLED)
            self.btn_final_solution.config(state=tk.DISABLED)
            self.btn_clear.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.NORMAL)  # permitir guardar aunque sea inválido
            self.status.set("Tablero inválido")
            self.redraw()
            return

        self.board = board
        self.solution_rects = []
        self.solution_mode = "none"
        self.game = GameState(board)

        self.btn_show_solution.config(state=tk.NORMAL)
        self.btn_final_solution.config(state=tk.NORMAL)
        self.btn_clear.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.NORMAL)

        self.status.set(
            "Modo juego: arrastra con clic izquierdo para dibujar rectángulos. "
            "Clic derecho para borrar uno."
        )
        self.redraw()

    def load_txt(self) -> None:
        """Carga un tablero desde un TXT."""

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
            self.solution_mode = "none"
            self.game = None
            self.btn_show_solution.config(state=tk.DISABLED)
            self.btn_final_solution.config(state=tk.DISABLED)
            self.btn_clear.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.DISABLED)
            self.status.set("Error al cargar")
            return

        self._set_board(board)

    def generate(self) -> None:
        """Genera un puzzle aleatorio y lo carga."""

        try:
            n = int(self.var_n.get())
            m = int(self.var_m.get())
        except ValueError:
            messagebox.showerror("Error", "N y M deben ser enteros.")
            return

        if n <= 0 or m <= 0:
            messagebox.showerror("Error", "N y M deben ser > 0")
            return

        diff_map = {"Fácil": "easy", "Medio": "medium", "Difícil": "hard"}
        diff = diff_map.get(self.var_diff.get(), "easy")

        board = generate_puzzle(n, m, diff, seed=None)
        self._set_board(board)

    def save_board(self) -> None:
        """Guarda el tablero actual dentro de ./boards."""

        if self.board is None:
            return
        ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{self.board.n_rows}x{self.board.n_cols}_{ts}.txt"
        try:
            path = save_board_to_boards(self.board, filename)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el tablero:\n{e}")
            return
        self.status.set(f"Tablero guardado en {path.as_posix()}")

    def clear_play(self) -> None:
        """Limpia la jugada del usuario y oculta cualquier solución mostrada."""

        if self.game is None:
            return
        self.game.clear()
        self.solution_rects = []
        self.solution_mode = "none"
        self.status.set("Jugada limpiada")
        self.redraw()

    def _compute_solution(self) -> tuple[bool, str]:
        """Ejecuta el solver, valida su salida y guarda la lista de rectángulos."""

        if self.board is None:
            return False, "No hay tablero"

        res = solve(self.board)
        if not res.success:
            self.solution_rects = []
            self.solution_mode = "none"
            self.redraw()
            messagebox.showwarning("Sin solución", res.message or "No se encontró solución.")
            self.status.set("Sin solución")
            return False, res.message

        self.solution_rects = res.rects

        # Verificar correctitud explícitamente antes de mostrar.
        chk = check_solution(self.board, self.solution_rects)
        if not chk.ok:
            messagebox.showerror("Error", f"El solver devolvió una solución inválida: {chk.message}")
            self.solution_rects = []
            self.solution_mode = "none"
            self.redraw()
            return False, chk.message

        # Mostrar métricas para el informe/demo.
        nodes = res.stats.nodes if res.stats else 0
        pruned = res.stats.pruned_overlap if res.stats else 0
        elapsed = res.elapsed_ms if res.elapsed_ms is not None else 0.0
        self.status.set(f"Solución calculada: {elapsed:.1f} ms | nodos: {nodes} | podas(solape): {pruned}")
        return True, "OK"

    def show_solution_overlay(self) -> None:
        """Muestra la solución como contornos (overlay) para que el usuario pueda seguir jugando."""

        if self.board is None:
            return
        self.status.set("Calculando solución...")
        self.update_idletasks()

        ok, _ = self._compute_solution()
        if not ok:
            return

        self.solution_mode = "overlay"
        self.redraw()

    def show_solution_final(self) -> None:
        """Muestra la solución final y bloquea el modo juego."""

        if self.board is None:
            return
        self.status.set("Calculando solución...")
        self.update_idletasks()

        ok, _ = self._compute_solution()
        if not ok:
            return

        self.solution_mode = "final"
        self.status.set(self.status.get() + " | Juego bloqueado (Limpiar jugada para jugar)")
        self.redraw()

    def _cell_from_event(self, event) -> tuple[int, int] | None:
        """Convierte un evento de mouse a una celda válida (fila,col) o None."""

        if self.board is None:
            return None
        cell = _cell_from_xy(event.x, event.y, self.pad, self.cell_size)
        if cell is None:
            return None
        r, c = cell
        if not (0 <= r < self.board.n_rows and 0 <= c < self.board.n_cols):
            return None
        return r, c

    def on_mouse_down(self, event) -> None:
        """Inicia el arrastre para dibujar un rectángulo."""

        if self.game is None or self.solution_mode == "final":
            return
        cell = self._cell_from_event(event)
        if cell is None:
            return
        self.drag_start = cell
        self.drag_end = cell
        self.redraw()

    def on_mouse_move(self, event) -> None:
        """Actualiza la previsualización del rectángulo."""

        if self.game is None or self.solution_mode == "final" or self.drag_start is None:
            return
        cell = self._cell_from_event(event)
        if cell is None:
            return
        self.drag_end = cell
        self.redraw()

    def on_mouse_up(self, event) -> None:
        """Finaliza el arrastre e intenta colocar el rectángulo."""

        if self.game is None or self.solution_mode == "final" or self.drag_start is None or self.drag_end is None:
            return

        rect = _rect_from_cells(self.drag_start, self.drag_end)
        res = self.game.try_add_rect(rect)
        if not res.ok:
            self.status.set(res.message)
        else:
            self.status.set("Rectángulo agregado")
            if self.game.is_win():
                messagebox.showinfo("¡Ganaste!", "La grilla quedó completamente pavimentada.")

        self.drag_start = None
        self.drag_end = None
        self.redraw()

    def on_right_click(self, event) -> None:
        """Elimina el rectángulo más reciente bajo el mouse."""

        if self.game is None or self.solution_mode == "final":
            return
        cell = self._cell_from_event(event)
        if cell is None:
            return
        r, c = cell
        if self.game.try_remove_rect_at(r, c):
            self.status.set("Rectángulo eliminado")
            self.redraw()

    def redraw(self) -> None:
        """Redibuja el canvas completo (grilla + pistas + rectángulos + preview)."""

        self.canvas.delete("all")
        if self.board is None:
            return

        n, m = self.board.n_rows, self.board.n_cols
        s = self.cell_size
        x0, y0 = self.pad, self.pad

        width = x0 * 2 + m * s
        height = y0 * 2 + n * s
        self.canvas.config(scrollregion=(0, 0, width, height))

        # Capa de solución (depende del modo)
        if self.solution_mode == "overlay":
            for rect in self.solution_rects:
                x1 = x0 + rect.c1 * s
                y1 = y0 + rect.r1 * s
                x2 = x0 + (rect.c2 + 1) * s
                y2 = y0 + (rect.r2 + 1) * s
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#1f5eff", width=4)

        elif self.solution_mode == "final":
            for i, rect in enumerate(self.solution_rects):
                fill = _pastel_color(i, max(1, len(self.solution_rects)))
                x1 = x0 + rect.c1 * s
                y1 = y0 + rect.r1 * s
                x2 = x0 + (rect.c2 + 1) * s
                y2 = y0 + (rect.r2 + 1) * s
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#222", width=3, fill=fill)

        # Rectángulos del jugador (cuando no está bloqueado)
        if self.game is not None and self.solution_mode != "final":
            for i, rect in enumerate(self.game.player_rects):
                fill = _pastel_color(i, max(1, len(self.game.player_rects)))
                x1 = x0 + rect.c1 * s
                y1 = y0 + rect.r1 * s
                x2 = x0 + (rect.c2 + 1) * s
                y2 = y0 + (rect.r2 + 1) * s
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#222", width=3, fill=fill)

        # Rectángulo de previsualización (arrastrando)
        if self.solution_mode != "final" and self.drag_start is not None and self.drag_end is not None:
            pr = _rect_from_cells(self.drag_start, self.drag_end)
            x1 = x0 + pr.c1 * s
            y1 = y0 + pr.r1 * s
            x2 = x0 + (pr.c2 + 1) * s
            y2 = y0 + (pr.r2 + 1) * s
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#000", width=2, dash=(4, 3))

        # Grilla y números de pistas
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
    """Punto de entrada para: python -m src.shikaku.ui_tk"""

    app = ShikakuApp()
    app.minsize(980, 360)
    app.mainloop()


if __name__ == "__main__":
    main()
