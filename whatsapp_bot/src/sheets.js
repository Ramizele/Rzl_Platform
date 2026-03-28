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

async function getPendingRows() {
  const sheets = await getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'campañas!A:E',
  });

  const rows = response.data.values || [];
  if (rows.length < 2) return [];

  // Fila 0 = header, filas 1+ = datos; rowIndex es 1-based en Sheets (header=1)
  return rows.slice(1).map((row, i) => ({
    rowIndex: i + 2,
    cliente: (row[0] || '').trim(),
    etiqueta: (row[1] || '').trim(),
    imagen_url: (row[2] || '').trim(),
    estado: (row[3] || '').trim(),
    fecha_envio: (row[4] || '').trim(),
  })).filter(row => row.estado === 'pendiente' && row.cliente);
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

async function updateEstado(rowIndex, estado, fechaEnvio) {
  const sheets = await getSheets();
  await sheets.spreadsheets.values.update({
    spreadsheetId: SPREADSHEET_ID,
    range: `campañas!D${rowIndex}:E${rowIndex}`,
    valueInputOption: 'RAW',
    requestBody: {
      values: [[estado, fechaEnvio]],
    },
  });
}

module.exports = { getPendingRows, getCliente, getMensajes, updateEstado };
