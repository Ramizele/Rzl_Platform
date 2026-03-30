# Instrucciones para Claude (VS Code) — whatsapp_bot — Paso 3: verificación y test

Pegá este bloque después de haber aplicado los cambios de sheets.js e index.js.

---

<!-- ============================================================ -->
<!-- PEGAR DESDE AQUÍ                                             -->
<!-- ============================================================ -->

Revisá que el proyecto whatsapp_bot quedó correctamente modificado. No tocar ningún archivo — solo verificar.

## Checklist de verificación

Confirmá que en **sheets.js** existen y están exportadas estas funciones:
- `getModoYEtiqueta()` — lee `mensajes!D2:D3`, devuelve `{ modo, etiqueta }`
- `getMensajes(modo, etiqueta)` — lee tabla desde `mensajes!A5:E`, filtra por modo Y etiqueta
- `getPendientesGest(etiqueta)` — filtra `gest` por etiqueta Y `estado_msj = "pendiente"`
- `getPendientesUniverso(etiqueta)` — filtra `plan_universo` por etiqueta Y `estado_msj = "pendiente"`
- `updateEstadoGest(rowIndex, estado, fechaEnvio)` — escribe en `gest!T:U`
- `updateEstadoUniverso(rowIndex, estado, fechaEnvio)` — escribe en `plan_universo!L:M`
- `writeLog(rows)` — sobreescribe hoja `log`
- `writeLogUniverso(rows)` — sobreescribe hoja `log_universo`

Confirmá que en **index.js**:
- El import de sheets usa las nuevas funciones
- `processRow` recibe `(client, row, etiqueta, modo)` como firma
- `run()` llama `getModoYEtiqueta()` al inicio
- `run()` bifurca entre `getPendientesGest` y `getPendientesUniverso` según modo
- `run()` bifurca entre `writeLog` y `writeLogUniverso` según modo
- El resumen final muestra modo y etiqueta
- Las funciones viejas (`getEtiquetaCampana`, `getClientesByEtiqueta`) no están en uso

Confirmá que **no se tocaron**: `sender.js`, `utils.js`, `package.json`, `.env`, `.gitignore`

## Si todo está bien

Indicá que el proyecto está listo para testear con:

```
node index.js --test
```

Recordar que antes de correr el test hay que tener en la hoja `mensajes`:
- `D2` = `gest` o `universo`
- `D3` = nombre de una etiqueta que exista en la tabla de la fila 5 en adelante
- Al menos una fila en `gest` o `plan_universo` con esa etiqueta y `estado_msj = pendiente`

<!-- ============================================================ -->
<!-- PEGAR HASTA AQUÍ                                             -->
<!-- ============================================================ -->
