# Instrucciones para Claude (VS Code) — whatsapp_bot — Paso 2: index.js

Pegá este bloque completo como mensaje en Claude dentro de VS Code, después de haber aplicado los cambios de sheets.js.

---

<!-- ============================================================ -->
<!-- PEGAR DESDE AQUÍ                                             -->
<!-- ============================================================ -->

Ahora modificá **index.js** del proyecto whatsapp_bot. El archivo ya existe y funciona — solo aplicar los cambios que se detallan abajo. No tocar `sender.js`, `utils.js`, ni ningún otro archivo.

## Cambios en el import

Reemplazar la línea de require de sheets.js por:

```javascript
const {
  getModoYEtiqueta,
  getMensajes,
  getPendientesGest,
  getPendientesUniverso,
  updateEstadoGest,
  updateEstadoUniverso,
  writeLog,
  writeLogUniverso,
} = require('./sheets');
```

## Cambios en processRow

La firma cambia para recibir `modo` como cuarto parámetro.
Internamente usa `updateEstadoGest` o `updateEstadoUniverso` según el modo.

```javascript
async function processRow(client, row, etiqueta, modo) {
  const { rowIndex, cliente, telefono, nombre_contacto } = row;
  const fecha_envio = formatTimestamp();
  console.log(`\n[fila ${rowIndex}] ${cliente} | ${etiqueta} | modo: ${modo}`);

  const updateEstado = modo === 'universo' ? updateEstadoUniverso : updateEstadoGest;

  const phoneNorm = normalizePhone(telefono);
  if (!isValidPhone(phoneNorm)) {
    const detalle_error = `teléfono inválido: "${telefono}" → "${phoneNorm}"`;
    console.error(`  ERROR: ${detalle_error}`);
    await updateEstado(rowIndex, 'error', fecha_envio);
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: '', estado: 'error', detalle_error };
  }

  const mensajes = await getMensajes(modo, etiqueta);
  if (!mensajes.length) {
    const detalle_error = `sin templates para modo: "${modo}" etiqueta: "${etiqueta}"`;
    console.error(`  ERROR: ${detalle_error}`);
    await updateEstado(rowIndex, 'error', fecha_envio);
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: '', estado: 'error', detalle_error };
  }

  const templateRaw = pickRandom(mensajes);
  const message = replaceName(templateRaw, nombre_contacto);
  const chatId = `${phoneNorm}@c.us`;

  console.log(`  → ${cliente} | ${phoneNorm}`);
  console.log(`  → Msg: ${message.slice(0, 60)}${message.length > 60 ? '...' : ''}`);

  try {
    await sendMessage(client, chatId, message, null);
    await updateEstado(rowIndex, 'enviado', fecha_envio);
    console.log('  ✓ Enviado');
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: message, estado: 'enviado', detalle_error: '' };
  } catch (err) {
    console.error(`  ERROR al enviar: ${err.message}`);
    await updateEstado(rowIndex, 'error', fecha_envio);
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: message, estado: 'error', detalle_error: err.message };
  }
}
```

## Cambios en run()

Reemplazar la función `run` completa por:

```javascript
async function run(client) {
  const { modo, etiqueta } = await getModoYEtiqueta();
  console.log(`\nModo    : ${modo}`);
  console.log(`Etiqueta: ${etiqueta}\n`);

  let rows;
  if (modo === 'universo') {
    rows = await getPendientesUniverso(etiqueta);
  } else {
    rows = await getPendientesGest(etiqueta);
  }

  if (!rows.length) {
    console.log(`No hay filas pendientes para modo "${modo}" con etiqueta "${etiqueta}".`);
    return;
  }

  if (TEST_MODE) {
    if (TEST_ROW) {
      rows = rows.filter(r => r.rowIndex === TEST_ROW);
      if (!rows.length) {
        console.log(`Modo test: fila ${TEST_ROW} no encontrada.`);
        return;
      }
    } else {
      rows = [rows[0]];
    }
    console.log(`*** MODO TEST — procesando ${rows.length} fila(s) ***\n`);
  }

  rows.sort(() => Math.random() - 0.5);
  console.log(`Procesando ${rows.length} fila(s)...`);

  const resultados = [];
  for (let i = 0; i < rows.length; i++) {
    const result = await processRow(client, rows[i], etiqueta, modo);
    resultados.push(result);
    if (i < rows.length - 1) await waitBetweenMessages();
  }

  if (modo === 'universo') {
    await writeLogUniverso(resultados);
  } else {
    await writeLog(resultados);
  }

  const enviados = resultados.filter(r => r.estado === 'enviado').length;
  const errores = resultados.filter(r => r.estado === 'error').length;
  console.log('\n=== Resumen ===');
  console.log(`Modo     : ${modo}`);
  console.log(`Etiqueta : ${etiqueta}`);
  console.log(`Enviados : ${enviados}`);
  console.log(`Errores  : ${errores}`);
}
```

## Reglas

- No tocar nada más del archivo — el resto de index.js (inicialización del cliente, QR, eventos, readline) queda exactamente igual
- El modo test (`--test` y `--row`) sigue funcionando igual que antes
- Código completo y funcional, sin TODOs ni placeholders

<!-- ============================================================ -->
<!-- PEGAR HASTA AQUÍ                                             -->
<!-- ============================================================ -->
