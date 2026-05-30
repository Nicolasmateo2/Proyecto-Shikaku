# Proyecto Shikaku

Proyecto de **Análisis de Algoritmos** sobre el juego tradicional **Shikaku**.

## Requisitos
- Python **3.11+**

## Ejecución (GUI mínima)
Desde la raíz del repositorio:

```bash
python -m src.shikaku.ui_tk
```

## Jugar (modo interactivo)
- **Clic izquierdo + arrastrar**: dibuja un rectángulo.
- Al soltar, el rectángulo se agrega solo si:
  - no se solapa con otro,
  - contiene **exactamente una pista**,
  - y su **área coincide** con el número de esa pista.
- **Clic derecho** sobre un rectángulo: lo elimina.
- Botón **Limpiar jugada**: borra todos los rectángulos del jugador.

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

## Generar tableros
En la GUI puedes ingresar **N**, **M**, seleccionar **dificultad** y hacer clic en **Generar**.

> Nota: el generador garantiza que el tablero sea **resoluble**, no necesariamente de solución única.

## Pruebas
Ejecutar:

```bash
python -m pytest
```

## Estructura
- `src/shikaku/domain.py`: modelos (Board, Clue, Rect)
- `src/shikaku/parser_txt.py`: lectura de tableros TXT
- `src/shikaku/candidates.py`: generación de rectángulos candidatos
- `src/shikaku/solver.py`: solucionador (backtracking)
- `src/shikaku/generator.py`: generador de tableros resolubles
- `src/shikaku/game.py`: estado/reglas para jugar interactivo
- `src/shikaku/ui_tk.py`: interfaz Tkinter (cargar, generar, jugar, resolver)
