# Proyecto Shikaku

Proyecto de **Análisis de Algoritmos** sobre el juego tradicional **Shikaku**.

## Resumen
Shikaku es un puzzle lógico donde se debe dividir una grilla en rectángulos. Cada rectángulo:
- contiene **exactamente una pista** (número)
- tiene **área igual** al valor de esa pista

Este proyecto incluye:
- GUI mínima en **Tkinter** para cargar/generar tableros, jugar y ver soluciones.
- Solucionador automático (**backtracking** con **poda** y heurística **MRV**).
- Generador de tableros **resolubles por construcción**.
- Validación explícita de soluciones (`check_solution`).
- Métricas del solver (tiempo, nodos explorados, podas por solape).
- Pruebas automáticas con **pytest**.

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

## Ver solución / resolver definitivo
- **Ver solución**: muestra la solución como **contornos azules** (overlay). Puedes seguir jugando.
- **Resolver definitivo**: pinta la solución completa y **bloquea el juego** en ese tablero.
  - Para volver a jugar, presiona **Limpiar jugada**.

> Nota: al calcular la solución, la barra de estado muestra métricas como: `ms | nodos | podas(solape)`.

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

## Estructura (módulos principales)
- `src/shikaku/domain.py`: modelos (Board, Clue, Rect)
- `src/shikaku/parser_txt.py`: lectura de tableros TXT
- `src/shikaku/io_txt.py`: guardado de tableros en `boards/`
- `src/shikaku/candidates.py`: generación de rectángulos candidatos
- `src/shikaku/solver.py`: solucionador (backtracking + poda + MRV)
- `src/shikaku/validate.py`: validación de tablero y de soluciones
- `src/shikaku/generator.py`: generador de tableros resolubles
- `src/shikaku/game.py`: estado/reglas para jugar interactivo
- `src/shikaku/ui_tk.py`: interfaz Tkinter (cargar, generar, jugar, resolver)
