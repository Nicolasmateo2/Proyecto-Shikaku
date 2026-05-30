# Proyecto Shikaku

Proyecto de **Análisis de Algoritmos** sobre el juego tradicional **Shikaku**.

## Requisitos
- Python **3.11+**

## Ejecución (GUI mínima)
Desde la raíz del repositorio:

```bash
python -m src.shikaku.ui_tk
```

## Formato del tablero (TXT)
- Primera línea: `N M`
- Luego `N` líneas con `M` enteros separados por espacios
- `0` = celda vacía, `>0` = pista (área)

Ejemplo:

```text
5 5
0 2 0 0 0
0 0 0 4 0
0 0 0 0 0
0 0 6 0 0
0 0 0 0 0
```

## Estructura
- `src/shikaku/domain.py`: modelos (Board, Clue, Rect)
- `src/shikaku/parser_txt.py`: lectura de tableros TXT
- `src/shikaku/ui_tk.py`: interfaz Tkinter mínima (cargar y dibujar tablero)

> Nota: el solucionador (backtracking) se agregará en archivos `candidates.py`, `solver.py`, `validate.py` y pruebas en `tests/`.
