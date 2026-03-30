# Instrucciones para Claude (VS Code) — whatsapp_bot v2

Pegá este bloque completo como primer mensaje en Claude dentro de VS Code.

---

<!-- ============================================================ -->
<!-- PEGAR DESDE AQUÍ                                             -->
<!-- ============================================================ -->

Vamos a modificar **whatsapp_bot**. No es un proyecto desde cero — el código ya existe y funciona. Solo modificamos `sheets.js` e `index.js`. No tocar `sender.js`, `utils.js`, `package.json` ni ningún otro archivo.

## Contexto del proyecto

Bot de WhatsApp en Node.js que lee desde Google Sheets y envía mensajes automatizados.
Stack: `whatsapp-web.js` + `googleapis` + `dotenv`

## Cambio central

Eliminamos la dependencia de la hoja `campañas` para el control de ejecución.
El control pasa a vivir en la hoja `mensajes`, en un tablero de dos celdas:

```
C2 = "MODO"      D2 = gest      ← modo activo ("gest" o "universo")
C3 = "ETIQUETA"  D3 = nuevo     ← etiqueta activa
```

Los templates siguen en la misma hoja `mensajes`, a partir de la fila 5:

```
| modo     | etiqueta      | mensaje_1            | mensaje_2              | mensaje_3 |
|----------|---------------|----------------------|------------------------|-----------|
| gest     | nuevo         | Holita {{nombre}}... | Hola {{nombre}}...     |           |
| gest     | viejo         | Hola {{nombre}}...   |                        |           |
| universo | int           | Hola tengo birra...  | Hola vendés cerveza... |           |
| universo | ya_contactado | Hola tanto tiempo... |                        |           |
```

## Arquitectura de hojas

### Hoja `gest` (modo gest)
| Columna | Índice | Campo | Quién escribe |
|---------|--------|-------|---------------|
| R | 17 | telefono | operador |
| S | 18 | etiqueta | operador |
| T | 19 | fecha_envio | **bot** |
| U | 20 | estado_msj | **bot** |

El bot solo procesa filas donde `estado_msj = "pendiente"`.

### Hoja `plan_universo` (modo universo)
| Columna | Índice | Campo | Quién escribe |
|---------|--------|-------|---------------|
| A | 0 | Nombre | operador |
| B | 1 | Direccion | operador |
| C | 2 | Barrio | operador |
| D | 3 | Telefono | operador |
| E | 4 | Instagram_o_Web | operador |
| F | 5 | Estrellas | operador |
| G | 6 | Comentarios | operador |
| H | 7 | Estado | operador |
| I | 8 | Link Maps | operador |
| J | 9 | Query | operador |
| K | 10 | etiqueta | operador |
| L | 11 | estado_msj | **bot** |
| M | 12 | fecha_envio | **bot** |
| N | 13 | intencionalidad | operador (el bot nunca toca esta columna) |

El bot solo procesa filas donde `estado_msj = "pendiente"`.

### Hoja `log` (modo gest)
Se sobreescribe en cada ejecución.
Columnas: `fecha_envio`, `cliente`, `telefono`, `etiqueta`, `mensaje_enviado`, `estado`, `detalle_error`

### Hoja `log_universo` (modo universo)
Se sobreescribe en cada ejecución. Mismas columnas que `log`.

## Flujo de ejecución

1. Leer `D2` de `mensajes` → modo activo (`"gest"` o `"universo"`)
2. Leer `D3` de `mensajes` → etiqueta activa
3. Según modo, leer de `gest` o `plan_universo`:
   - Traer filas donde `etiqueta` coincide **Y** `estado_msj = "pendiente"`
4. Si no hay filas pendientes → loggear mensaje y salir
5. Aleatorizar orden de envío
6. Por cada fila:
   - Normalizar teléfono → si inválido: marcar `error`, loggear, continuar
   - Buscar etiqueta en `mensajes` (tabla desde fila 5, filtrar por `modo` Y `etiqueta`) → array de variantes no vacías
   - Si no hay templates: marcar `error`, loggear, continuar
   - Elegir variante al azar
   - Reemplazar `{{nombre}}` si hay `nombre_contacto` — en modo `universo` siempre vacío
   - Simular tipeo humano → enviar mensaje
   - Actualizar `estado_msj` + `fecha_envio` en la hoja correspondiente
   - Esperar delay aleatorio entre 8 y 20 segundos
7. Escribir log en `log` o `log_universo` según modo
8. Mostrar resumen en consola (modo activo, enviados, errores)

## sheets.js — reescribir completo

Mantener la autenticación existente con `GoogleAuth` + `keyFile` desde `.env`.

Funciones requeridas:

**`getModoYEtiqueta()`**
- Lee `mensajes!D2` y `mensajes!D3`
- Devuelve `{ modo, etiqueta }` donde `modo` es `"gest"` o `"universo"`
- Si alguna celda está vacía, lanzar error descriptivo

**`getMensajes(modo, etiqueta)`**
- Lee la tabla de `mensajes` desde fila 5 en adelante (rango `mensajes!A5:E`)
- Filtra por columna A = `modo` Y columna B = `etiqueta`
- Devuelve array de variantes no vacías (columnas C, D, E)

**`getPendientesGest(etiqueta)`**
- Lee `gest!A:U`
- Filtra filas donde columna S (índice 18) = `etiqueta` Y columna U (índice 20) = `"pendiente"` (case-insensitive)
- Devuelve array de `{ rowIndex, cliente, telefono, nombre_contacto }`
- `rowIndex` es 1-based (header en fila 1, datos desde fila 2)

**`getPendientesUniverso(etiqueta)`**
- Lee `plan_universo!A:N`
- Filtra filas donde columna K (índice 10) = `etiqueta` Y columna L (índice 11) = `"pendiente"` (case-insensitive)
- Devuelve array de `{ rowIndex, cliente, telefono, nombre_contacto: '' }`
- `cliente` viene de columna A (Nombre), `telefono` de columna D

**`updateEstadoGest(rowIndex, estado, fechaEnvio)`**
- Actualiza `gest!T{rowIndex}:U{rowIndex}` con `[fechaEnvio, estado]`

**`updateEstadoUniverso(rowIndex, estado, fechaEnvio)`**
- Actualiza `plan_universo!L{rowIndex}:M{rowIndex}` con `[estado, fechaEnvio]`

**`writeLog(rows)`**
- Limpia y sobreescribe hoja `log`
- Header + datos

**`writeLogUniverso(rows)`**
- Limpia y sobreescribe hoja `log_universo`
- Misma estructura que `writeLog`

## index.js — modificar función run() y processRow()

**`processRow(client, row, etiqueta, modo)`**
- Firma cambia: recibe `modo` como cuarto parámetro
- Usa `updateEstadoGest` si `modo === "gest"`, `updateEstadoUniverso` si `modo === "universo"`
- Todo lo demás igual al código actual

**`run(client)`**
- Reemplazar llamada a `getEtiquetaCampana()` + `getClientesByEtiqueta()` por `getModoYEtiqueta()` + `getPendientesGest()` o `getPendientesUniverso()` según modo
- Al final llamar `writeLog` o `writeLogUniverso` según modo
- En el resumen de consola mostrar el modo activo

El modo test (`--test` y `--row`) debe seguir funcionando exactamente igual.

## Reglas de implementación

- Código completo y funcional — sin TODOs ni placeholders
- `credentials.json` nunca hardcodeado — siempre desde `.env`
- Delay mínimo 8s, máximo 20s, siempre aleatorio (ya implementado en `sender.js`, no tocar)
- Rate limit de 50 mensajes/hora (ya implementado en `sender.js`, no tocar)
- Si cualquier paso falla → marcar `error` en la hoja correspondiente, loggear con detalle, continuar con la siguiente fila
- No tocar `sender.js`, `utils.js`, `package.json`, `.env`, `.gitignore`

## Primer paso

Reescribí `sheets.js` completo con todas las funciones listadas arriba. Cuando lo confirme, pasamos a los cambios en `index.js`.

<!-- ============================================================ -->
<!-- PEGAR HASTA AQUÍ                                             -->
<!-- ============================================================ -->
