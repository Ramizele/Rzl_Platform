require('dotenv').config();
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const { getPendingRows, getCliente, getMensajes, updateEstado } = require('./sheets');
const { sendMessage, waitBetweenMessages } = require('./sender');
const { normalizePhone, isValidPhone, replaceName, pickRandom, formatTimestamp } = require('./utils');

const TEST_MODE = process.argv.includes('--test');
const rowFlagIndex = process.argv.indexOf('--row');
const TEST_ROW = rowFlagIndex !== -1 ? parseInt(process.argv[rowFlagIndex + 1]) : null;

async function processRow(client, row) {
  const { rowIndex, cliente, etiqueta, imagen_url } = row;
  console.log(`\n[fila ${rowIndex}] ${cliente} | ${etiqueta}`);

  const clienteData = await getCliente(cliente);
  if (!clienteData) {
    console.error(`  ERROR: cliente no encontrado en maestro: "${cliente}"`);
    await updateEstado(rowIndex, 'error', formatTimestamp());
    return 'error';
  }

  const phoneNorm = normalizePhone(clienteData.telefono);
  if (!isValidPhone(phoneNorm)) {
    console.error(`  ERROR: teléfono inválido: "${clienteData.telefono}" → "${phoneNorm}"`);
    await updateEstado(rowIndex, 'error', formatTimestamp());
    return 'error';
  }

  const mensajes = await getMensajes(etiqueta);
  if (!mensajes.length) {
    console.error(`  ERROR: sin templates para etiqueta: "${etiqueta}"`);
    await updateEstado(rowIndex, 'error', formatTimestamp());
    return 'error';
  }

  const templateRaw = pickRandom(mensajes);
  const message = replaceName(templateRaw, clienteData.nombre_contacto);
  const chatId = `${phoneNorm}@c.us`;

  const nombreDisplay = clienteData.nombre_contacto || '(sin nombre)';
  console.log(`  → ${clienteData.cliente} / ${nombreDisplay} | ${phoneNorm}`);
  console.log(`  → Msg: ${message.slice(0, 60)}${message.length > 60 ? '...' : ''}`);

  try {
    await sendMessage(client, chatId, message, imagen_url || null);
    await updateEstado(rowIndex, 'enviado', formatTimestamp());
    console.log('  ✓ Enviado');
    return 'enviado';
  } catch (err) {
    console.error(`  ERROR al enviar: ${err.message}`);
    await updateEstado(rowIndex, 'error', formatTimestamp());
    return 'error';
  }
}

async function run(client) {
  let rows = await getPendingRows();

  if (!rows.length) {
    console.log('No hay filas pendientes en campañas.');
    return;
  }

  if (TEST_MODE) {
    if (TEST_ROW) {
      rows = rows.filter(r => r.rowIndex === TEST_ROW);
      if (!rows.length) {
        console.log(`Modo test: fila ${TEST_ROW} no encontrada o no está pendiente.`);
        return;
      }
    } else {
      rows = [rows[0]];
    }
    console.log(`\n*** MODO TEST — procesando ${rows.length} fila(s) ***\n`);
  }

  // Aleatorizar orden de envío
  rows.sort(() => Math.random() - 0.5);
  console.log(`Procesando ${rows.length} fila(s) pendiente(s)...`);

  const counts = { enviado: 0, error: 0 };

  for (let i = 0; i < rows.length; i++) {
    const result = await processRow(client, rows[i]);
    counts[result] = (counts[result] || 0) + 1;

    if (i < rows.length - 1) {
      await waitBetweenMessages();
    }
  }

  console.log('\n=== Resumen ===');
  console.log(`Enviados : ${counts.enviado || 0}`);
  console.log(`Errores  : ${counts.error || 0}`);
}

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
});

client.on('qr', qr => {
  console.log('Escaneá este QR con WhatsApp:\n');
  qrcode.generate(qr, { small: true });
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
