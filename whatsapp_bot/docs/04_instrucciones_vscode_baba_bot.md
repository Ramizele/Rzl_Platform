# Instrucciones para Claude (VS Code) — baba_bot

Pegá este bloque completo como primer mensaje en Claude dentro de VS Code.

---

<!-- ============================================================ -->
<!-- PEGAR DESDE AQUÍ                                             -->
<!-- ============================================================ -->

Vamos a construir **baba_bot** desde cero. Es un bot de WhatsApp en Node.js que lee desde Google Sheets y envía mensajes automatizados.

## Stack

- Node.js
- `whatsapp-web.js` — controla WhatsApp Web via Puppeteer
- `googleapis` — lee y escribe en Google Sheets
- `dotenv` — manejo de credenciales

## Arquitectura de Google Sheets

El proyecto usa 3 hojas dentro de un mismo Google Spreadsheet:

**Hoja `clientes`** — maestro de contactos
```
| cliente      | telefono      | nombre_contacto |
|--------------|---------------|-----------------|
| La Birra Bar | 5491112345678 | Juan            |
| El Bodegón   | 1187654321    |                 |
```

**Hoja `campañas`** — filas a enviar en cada ejecución
```
| cliente      | etiqueta | imagen_url | estado    | fecha_envio |
|--------------|----------|------------|-----------|-------------|
| La Birra Bar | cobranza |            | pendiente |             |
| El Bodegón   | promo    | https://…  | pendiente |             |
```

**Hoja `mensajes`** — templates por etiqueta
```
| etiqueta | mensaje_1                       | mensaje_2                  | mensaje_3 |
|----------|---------------------------------|----------------------------|-----------|
| cobranza | Hola {{nombre}}, te escribimos… | {{nombre}}, recordatorio…  |           |
| promo    | Hola {{nombre}}! Esta semana…   | Buenas {{nombre}}, tenemos |           |
```

## Lógica de ejecución

1. Leer todas las filas con `estado = pendiente` de la hoja `campañas`
2. Aleatorizar el orden de envío
3. Para cada fila:
   - Buscar `cliente` en la hoja `clientes` → obtener `telefono` y `nombre_contacto`
   - Si el cliente no existe → marcar `error` en `campañas`, loggear, continuar
   - Normalizar `telefono` al formato internacional (`5491112345678`)
   - Si el número es inválido → marcar `error`, loggear, continuar
   - Buscar `etiqueta` en la hoja `mensajes` → obtener todas las variantes no vacías
   - Si la etiqueta no existe o no tiene mensajes → marcar `error`, loggear, continuar
   - Elegir una variante al azar
   - Si hay `nombre_contacto` → reemplazar `{{nombre}}`; si no → usar la variante tal cual (los templates sin `{{nombre}}` son el fallback)
   - Si hay `imagen_url` → enviar imagen con el mensaje como caption; si no → enviar solo texto
   - Antes de enviar: simular tipeo humano con `sendPresenceUpdate('composing')`
   - Enviar el mensaje
   - Actualizar `estado` → `enviado` y escribir `fecha_envio` con timestamp
   - Esperar delay aleatorio entre 8 y 20 segundos antes del siguiente envío
4. Al finalizar: loggear resumen (enviados, errores, omitidos)

## Estructura de archivos del proyecto

```
baba_bot/
├── index.js              ← entry point, inicializa WhatsApp y dispara el envío
├── sheets.js             ← toda la lógica de Google Sheets (leer, buscar, actualizar)
├── sender.js             ← lógica de envío, delays, tipeo simulado
├── utils.js              ← normalización de teléfonos, reemplazo de variables, helpers
├── .env                  ← credenciales (nunca commitear)
├── .env.example          ← template de variables de entorno
├── .gitignore            ← excluir .env y credentials.json
└── package.json
```

## Variables de entorno (.env)

```
GOOGLE_CREDENTIALS_PATH=./credentials.json
SPREADSHEET_ID=tu_spreadsheet_id_aqui
```

## Reglas de implementación

- `credentials.json` nunca va hardcodeado — siempre desde `.env`
- Todos los teléfonos se normalizan antes de enviar — nunca asumir formato correcto
- Delay mínimo entre mensajes: 8 segundos. Máximo: 20 segundos. Siempre aleatorio, nunca fijo
- Máximo ~50 mensajes por hora — agregar control de rate si el volumen supera eso
- Si cualquier paso del lookup o envío falla → marcar `error` en la sheet, loggear con detalle, continuar con la siguiente fila (no cortar la ejecución)
- Antes de un envío masivo debe existir un modo test: procesar solo 1 fila específica
- El código debe ser completo y funcional — sin TODOs ni placeholders

## Primer paso

Creá la estructura de archivos del proyecto e implementá primero `sheets.js` completo con:
- Autenticación via Service Account
- `getPendingRows()` — lee campañas con estado pendiente
- `getCliente(nombre)` — lookup en hoja clientes
- `getMensajes(etiqueta)` — devuelve array de variantes no vacías para esa etiqueta
- `updateEstado(rowIndex, estado, fechaEnvio)` — actualiza estado y timestamp en campañas

<!-- ============================================================ -->
<!-- PEGAR HASTA AQUÍ                                             -->
<!-- ============================================================ -->

---

## Cómo usar

1. Abrí VS Code con la carpeta del proyecto (o una carpeta vacía)
2. Abrí Claude en VS Code (panel lateral o chat)
3. Pegá el bloque completo como primer mensaje
4. Claude va a generar `sheets.js` primero — revisalo y confirmá antes de seguir
5. En el siguiente mensaje pedile: `"Ahora implementá sender.js y utils.js"`
6. Finalmente: `"Ahora implementá index.js con el flujo completo"`
