# Protocolo de Ingesta de Conocimiento — ALGO I

Como alimentar al agente con libros y material de estudio para que los convierta en movimientos de aprendizaje.

---

## Principio

ALGO I aprende con vos, no por vos. Cuando le das material de un libro, lo convierte en un Movimiento estructurado — con posicion, calculo, implementacion en ambos lenguajes, insight y ejercicio. El material que ingesta queda como Nota de Conocimiento para referencias futuras.

---

## Comando de ingesta

Activas el modo INGESTA con este prefijo:

```
INGESTA: [texto del libro o fragmento de estudio]
```

Ejemplo:

```
INGESTA: 
"En Haskell, una funcion es de orden superior cuando toma otra funcion como 
argumento o devuelve una funcion como resultado. El ejemplo canonico es map, 
que aplica una funcion a cada elemento de una lista..."
```

ALGO I responde con:
1. Conceptos identificados en el fragmento (maximo 3)
2. Ubicacion en el curriculo (Apertura / Medio juego / Final)
3. Movimiento completo del concepto principal
4. Nota de Conocimiento para guardar

---

## Tipos de material que podes ingestar

| Tipo | Como enviarlo | Que hace el agente |
|---|---|---|
| Parrafo de libro | Pegarlo despues de `INGESTA:` | Extrae conceptos, genera movimiento |
| Definicion formal | Pegar definicion + contexto | Traduce a lenguaje comun + codigo |
| Ejemplo de codigo del libro | Pegar el codigo | Explica patron, reformula en ambos lenguajes |
| Ejercicio del libro | Pegar enunciado | Convierte a formato PRACTICA de ALGO I |
| Diagrama descrito en texto | Describir el diagrama | Genera codigo que representa la estructura |

---

## Donde guardar las notas de conocimiento

Cada Nota de Conocimiento que genera ALGO I la guardas en:

```
algo_i/assets/[nombre-del-libro]/[capitulo-o-tema].md
```

Ejemplo:

```
algo_i/assets/lyah/cap06-higher-order-functions.md
algo_i/assets/clrs/cap02-insertion-sort.md
algo_i/assets/fluent-python/cap07-closures.md
```

---

## Como enlazar una sesion con material anterior

Al iniciar una sesion nueva con material ya ingestado, referencia el archivo:

```
ESTUDIO: Quiero continuar desde la Nota de Conocimiento en 
algo_i/assets/lyah/cap06-higher-order-functions.md.
Siguiente concepto a cubrir: foldl vs foldr.
```

---

## Registro de materiales (actualizar aqui)

Cada libro o recurso que ingresas al sistema. Mantener actualizado.

| ID | Libro / Recurso | Lenguaje | Capitulos ingestados | Nota |
|---|---|---|---|---|
| lyah | Learn You a Haskell for Great Good! | Haskell | — | — |
| rwh | Real World Haskell | Haskell | — | — |
| adwh | Algorithm Design with Haskell | Haskell | — | — |
| clrs | Introduction to Algorithms | General | — | — |
| fp | Fluent Python | Python | — | — |
| grokking | Grokking Algorithms | Python | — | — |

---

## Flujo de una sesion con libro

```
1. Abris el libro en el capitulo a estudiar
2. Lees un fragmento (parrafo o seccion corta)
3. Lo pegas en Claude Projects con INGESTA:
4. ALGO I genera el Movimiento
5. Trabajas el ejercicio que genera (PRACTICA:)
6. Guardas la Nota de Conocimiento en algo_i/assets/
7. Actualizas el curriculo en algo_i/docs/curriculum_map.md
8. Pasas al siguiente fragmento o al siguiente capitulo
```

---

## Buenas practicas

- Ingestá fragmentos de tamano moderado — un parrafo o concepto a la vez, no capitulos enteros.
- Si el libro tiene codigo, incluilo en el fragmento — ALGO I lo reformula en ambos lenguajes.
- Si el fragmento toca mas de 3 conceptos, parti la ingesta en dos mensajes separados.
- Guarda las notas inmediatamente despues de generarlas — no las pierdas en el chat.
- Al final de cada sesion, actualiza el `curriculum_map.md` con el movimiento completado.
