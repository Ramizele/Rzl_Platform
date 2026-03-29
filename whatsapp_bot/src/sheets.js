require('dotenv').config();
const { google } = require('googleapis');
const path = require('path');

const SPREADSHEET_ID = process.env.SPREADSHEET_ID;
const CREDENTIALS_PATH = process.env.GOOGLE_CREDENTIALS_PATH || './credentials.json';

async function getSheets() {
  const auth = new google.auth.GoogleAuth({
    keyFile: path.resolve(CREDENTIALS_PATH),
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  return google.sheets({ version: 'v4', auth });
}

async function getEtiquetaCampana() {
  const sheets = await getSheets();
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'campañas!A2',
  });
  const val = (res.data.values?.[0]?.[0] || '').trim();
  return val || null;
}

async function getClientesByEtiqueta(etiqueta) {
  const sheets = await getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'gest!A:U',
  });

  const rows = response.data.values || [];
  if (rows.length < 2) return [];

  // Fila 0 = header, filas 1+ = datos; rowIndex 1-based (header=1, datos desde 2)
  return rows.slice(1)
    .map((row, i) => ({ row, rowIndex: i + 2 }))
    .filter(({ row }) => {
      const cliente = (row[0] || '').trim();
      const telefono = (row[17] || '').trim();
      const etiq = (row[18] || '').trim();
      return cliente && telefono && etiq === etiqueta;
    })
    .map(({ row, rowIndex }) => ({
      rowIndex,
      cliente: (row[0] || '').trim(),
      telefono: (row[17] || '').trim(),
      nombre_contacto: '',
    }));
}

async function getCliente(nombre) {
  const sheets = await getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'clientes!A:C',
  });

  const rows = response.data.values || [];
  const found = rows.slice(1).find(row => (row[0] || '').trim() === nombre);
  if (!found) return null;

  return {
    cliente: (found[0] || '').trim(),
    telefono: (found[1] || '').trim(),
    nombre_contacto: (found[2] || '').trim(),
  };
}

async function getMensajes(etiqueta) {
  const sheets = await getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'mensajes!A:D',
  });

  const rows = response.data.values || [];
  const found = rows.slice(1).find(row => (row[0] || '').trim() === etiqueta);
  if (!found) return [];

  return [found[1], found[2], found[3]].filter(Boolean).filter(m => m.trim());
}

async function updateEstadoGest(rowIndex, estado, fechaEnvio) {
  const sheets = await getSheets();
  await sheets.spreadsheets.values.update({
    spreadsheetId: SPREADSHEET_ID,
    range: `gest!T${rowIndex}:U${rowIndex}`,
    valueInputOption: 'RAW',
    requestBody: {
      values: [[fechaEnvio, estado]],
    },
  });
}

async function writeLog(rows) {
  const sheets = await getSheets();

  await sheets.spreadsheets.values.clear({
    spreadsheetId: SPREADSHEET_ID,
    range: 'log!A:G',
  });

  const header = ['fecha_envio', 'cliente', 'telefono', 'etiqueta', 'mensaje_enviado', 'estado', 'detalle_error'];
  const data = rows.map(r => [
    r.fecha_envio,
    r.cliente,
    r.telefono,
    r.etiqueta,
    r.mensaje_enviado,
    r.estado,
    r.detalle_error || '',
  ]);

  await sheets.spreadsheets.values.update({
    spreadsheetId: SPREADSHEET_ID,
    range: 'log!A1',
    valueInputOption: 'RAW',
    requestBody: {
      values: [header, ...data],
    },
  });
}

module.exports = { getEtiquetaCampana, getClientesByEtiqueta, getCliente, getMensajes, updateEstadoGest, writeLog };
