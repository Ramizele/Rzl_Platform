require('dotenv').config();
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const QRCode = require('qrcode');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const { getEtiquetaCampana, getClientesByEtiqueta, getMensajes, updateEstadoGest, writeLog } = require('./sheets');
const { sendMessage, waitBetweenMessages } = require('./sender');
const { normalizePhone, isValidPhone, replaceName, pickRandom, formatTimestamp } = require('./utils');

const TEST_MODE = process.argv.includes('--test');
const rowFlagIndex = process.argv.indexOf('--row');
const TEST_ROW = rowFlagIndex !== -1 ? parseInt(process.argv[rowFlagIndex + 1]) : null;

async function processRow(client, row, etiqueta) {
  const { rowIndex, cliente, telefono, nombre_contacto } = row;
  const fecha_envio = formatTimestamp();
  console.log(`\n[fila ${rowIndex}] ${cliente} | ${etiqueta}`);

  const phoneNorm = normalizePhone(telefono);
  if (!isValidPhone(phoneNorm)) {
    const detalle_error = `teléfono inválido: "${telefono}" → "${phoneNorm}"`;
    console.error(`  ERROR: ${detalle_error}`);
    await updateEstadoGest(rowIndex, 'error', fecha_envio);
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: '', estado: 'error', detalle_error };
  }

  const mensajes = await getMensajes(etiqueta);
  if (!mensajes.length) {
    const detalle_error = `sin templates para etiqueta: "${etiqueta}"`;
    console.error(`  ERROR: ${detalle_error}`);
    await updateEstadoGest(rowIndex, 'error', fecha_envio);
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: '', estado: 'error', detalle_error };
  }

  const templateRaw = pickRandom(mensajes);
  const message = replaceName(templateRaw, nombre_contacto);
  const chatId = `${phoneNorm}@c.us`;

  console.log(`  → ${cliente} | ${phoneNorm}`);
  console.log(`  → Msg: ${message.slice(0, 60)}${message.length > 60 ? '...' : ''}`);

  try {
    await sendMessage(client, chatId, message, null);
    await updateEstadoGest(rowIndex, 'enviado', fecha_envio);
    console.log('  ✓ Enviado');
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: message, estado: 'enviado', detalle_error: '' };
  } catch (err) {
    console.error(`  ERROR al enviar: ${err.message}`);
    await updateEstadoGest(rowIndex, 'error', fecha_envio);
    return { fecha_envio, cliente, telefono: phoneNorm, etiqueta, mensaje_enviado: message, estado: 'error', detalle_error: err.message };
  }
}

async function run(client) {
  const etiqueta = await getEtiquetaCampana();
  if (!etiqueta) {
    console.log('No hay etiqueta definida en campañas.');
    return;
  }

  let rows = await getClientesByEtiqueta(etiqueta);
  if (!rows.length) {
    console.log(`No hay clientes con etiqueta "${etiqueta}".`);
    return;
  }

  if (TEST_MODE) {
    if (TEST_ROW) {
      rows = rows.filter(r => r.rowIndex === TEST_ROW);
      if (!rows.length) {
        console.log(`Modo test: fila ${TEST_ROW} no encontrada para etiqueta "${etiqueta}".`);
        return;
      }
    } else {
      rows = [rows[0]];
    }
    console.log(`\n*** MODO TEST — procesando ${rows.length} fila(s) ***\n`);
  }

  // Aleatorizar orden de envío
  rows.sort(() => Math.random() - 0.5);
  console.log(`Procesando ${rows.length} fila(s) con etiqueta "${etiqueta}"...`);

  const resultados = [];

  for (let i = 0; i < rows.length; i++) {
    const result = await processRow(client, rows[i], etiqueta);
    resultados.push(result);

    if (i < rows.length - 1) {
      await waitBetweenMessages();
    }
  }

  await writeLog(resultados);

  const enviados = resultados.filter(r => r.estado === 'enviado').length;
  const errores = resultados.filter(r => r.estado === 'error').length;
  console.log('\n=== Resumen ===');
  console.log(`Enviados : ${enviados}`);
  console.log(`Errores  : ${errores}`);
}

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
});

client.on('qr', qr => {
  console.log('Escaneá este QR con WhatsApp:\n');
  qrcode.generate(qr, { small: true });
  const qrPath = path.join(__dirname, 'qr.png');
  QRCode.toFile(qrPath, qr, { scale: 8 }, err => {
    if (!err) {
      console.log(`\nQR guardado en: ${qrPath}`);
      exec(`start "" "${qrPath}"`);
    }
  });
});

client.on('authenticated', () => {
  console.log('WhatsApp autenticado.');
});

client.on('auth_failure', msg => {
  console.error('Fallo de autenticación:', msg);
  process.exit(1);
});

client.on('ready', async () => {
  console.log('Cliente WhatsApp listo.\n');
  try {
    await run(client);
  } catch (err) {
    console.error('Error fatal:', err);
  } finally {
    console.log('\nListo. Podés cerrar esta terminal.');
  }
});

client.on('disconnected', reason => {
  console.log('Cliente desconectado:', reason);
  process.exit(0);
});

client.initialize();

const readline = require('readline');
readline.emitKeypressEvents(process.stdin);
if (process.stdin.isTTY) process.stdin.setRawMode(true);
process.stdin.on('keypress', (str, key) => {
  if (str === 'q' || (key.ctrl && key.name === 'c')) {
    console.log('\nSaliendo...');
    client.destroy().finally(() => process.exit(0));
  }
});
console.log('Presioná "q" para salir en cualquier momento.');
