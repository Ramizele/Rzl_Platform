# Curriculum Map — ALGO I

Mapa de temas ordenado por nivel. Cada nivel corresponde a una fase de la partida de ajedrez.

---

## APERTURA — Fundamentos

Conceptos basicos compartidos entre Python y Haskell. Punto de entrada al tablero.

| Movimiento | Concepto | Python | Haskell |
|---|---|---|---|
| 1 | Tipos basicos y variables | `int`, `str`, `bool`, `float` | `Int`, `String`, `Bool`, `Double` |
| 2 | Funciones puras | `def f(x): return x` | `f x = x` |
| 3 | Recursion basica | Factorial, Fibonacci | Factorial, Fibonacci |
| 4 | Listas y operaciones | `list`, `map`, `filter`, `reduce` | `[a]`, `map`, `filter`, `foldl` |
| 5 | Pattern matching | Destructuring, `match`/`case` (3.10+) | `case`, guards, destructuring |
| 6 | Funciones de orden superior | Lambdas, closures, `functools` | Lambdas, currying, `$`, `.` |
| 7 | Tuplas y registros | `tuple`, `namedtuple`, `dataclass` | Tuplas, records, `data` |
| 8 | Tipos opcionales | `None`, `Optional` | `Maybe`, `Just`, `Nothing` |

---

## MEDIO JUEGO — Estructura y logica

Estructuras de datos clasicas y algoritmos fundamentales.

| Movimiento | Concepto | Python | Haskell |
|---|---|---|---|
| 9 | Arboles binarios | Clases, recursion | `data Tree`, recursion |
| 10 | Pilas y colas | `list`, `deque` | Listas con semantica de stack |
| 11 | Diccionarios y mapas | `dict`, `defaultdict` | `Data.Map`, `Data.HashMap` |
| 12 | Conjuntos | `set`, `frozenset` | `Data.Set` |
| 13 | Busqueda en profundidad (DFS) | Recursion + stack | Recursion pura |
| 14 | Busqueda en anchura (BFS) | Cola + visited set | Cola + visited |
| 15 | Ordenamiento: Merge Sort | Divide y conquista | Divide y conquista |
| 16 | Ordenamiento: Quick Sort | Particion | Particion con listas |
| 17 | Programacion dinamica: memoizacion | `@lru_cache`, `functools` | Lazy evaluation + `Map` |
| 18 | Programacion dinamica: tabulacion | Iteracion con tabla | Array con `Data.Array` |
| 19 | Grafos: representacion | Diccionario de adyacencia | `Map` de listas |
| 20 | Grafos: BFS/DFS generalizados | Visited set + cola/stack | Recursion + acumulador |

---

## FINAL — Integracion y profundidad

Conceptos avanzados. Convergencia de algoritmos y programacion funcional pura.

| Movimiento | Concepto | Python | Haskell |
|---|---|---|---|
| 21 | Type classes y protocolos | ABCs, Protocols (`typing`) | `class`, `instance`, derivacion |
| 22 | Functores | `map` generalizado | `Functor`, `fmap` |
| 23 | Monads | Chaining con `>>=` en Python (simulado) | `Monad`, `do` notation, `IO` |
| 24 | Dijkstra (grafos ponderados) | `heapq` + dist | `Data.Map` + priority queue |
| 25 | Floyd-Warshall | Matriz de distancias | Array bidimensional |
| 26 | Arbol de expansion minima | Kruskal, Union-Find | Kruskal con `Data.Set` |
| 27 | Parsing y ASTs | `ast` module, PLY | Parsec, Attoparsec |
| 28 | Complejidad algoritmica | Big-O analisis | Big-O analisis |
| 29 | Lazy evaluation | Generators, `itertools` | Evaluacion perezosa nativa |
| 30 | Concurrencia basica | `asyncio`, `threading` | `async`, STM, `forkIO` |

---

## Libros de referencia

Agregar aqui los libros en uso. Vincular con extractos en `assets/`.

| Libro | Lenguaje | Estado |
|---|---|---|
| _(agregar al iniciar estudio)_ | — | — |

---

## Estado del tablero

Actualizar a medida que se completan movimientos.

- Ultimo movimiento completado: —
- Nivel actual: Apertura
- Siguiente movimiento: 1 — Tipos basicos y variables
