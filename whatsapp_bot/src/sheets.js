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

async function getModoYEtiqueta() {
  const sheets = await getSheets();
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'mensajes!D2:D3',
  });
  const values = res.data.values || [];
  const modo = (values[0]?.[0] || '').trim();
  const etiqueta = (values[1]?.[0] || '').trim();
  if (!modo) throw new Error('La celda mensajes!D2 (MODO) está vacía.');
  if (!etiqueta) throw new Error('La celda mensajes!D3 (ETIQUETA) está vacía.');
  return { modo, etiqueta };
}

async function getMensajes(modo, etiqueta) {
  const sheets = await getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'mensajes!A5:E',
  });

  const rows = response.data.values || [];
  const found = rows.find(row =>
    (row[0] || '').trim() === modo && (row[1] || '').trim() === etiqueta
  );
  if (!found) return [];

  return [found[2], found[3], found[4]].filter(v => v && v.trim());
}

async function getPendientesGest(etiqueta) {
  const sheets = await getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'gest!A:U',
  });

  const rows = response.data.values || [];
  if (rows.length < 2) return [];

  // Fila 0 = header, datos desde fila 2 (rowIndex 1-based)
  return rows.slice(1)
    .map((row, i) => ({ row, rowIndex: i + 2 }))
    .filter(({ row }) => {
      const etiq = (row[18] || '').trim();
      const estado = (row[20] || '').trim().toLowerCase();
      return etiq === etiqueta && estado === 'pendiente';
    })
    .map(({ row, rowIndex }) => ({
      rowIndex,
      cliente: (row[0] || '').trim(),
      telefono: (row[17] || '').trim(),
      nombre_contacto: (row[2] || '').trim(),
    }));
}

async function getPendientesUniverso(etiqueta) {
  const sheets = await getSheets();
  const response = await sheets.spreadsheets.values.get({
    spreadsheetId: SPREADSHEET_ID,
    range: 'plan_universo!A:N',
  });

  const rows = response.data.values || [];
  if (rows.length < 2) return [];

  // Fila 0 = header, datos desde fila 2 (rowIndex 1-based)
  return rows.slice(1)
    .map((row, i) => ({ row, rowIndex: i + 2 }))
    .filter(({ row }) => {
      const etiq = (row[10] || '').trim();
      const estado = (row[11] || '').trim().toLowerCase();
      return etiq === etiqueta && estado === 'pendiente';
    })
    .map(({ row, rowIndex }) => ({
      rowIndex,
      cliente: (row[0] || '').trim(),
      telefono: (row[3] || '').trim(),
      nombre_contacto: '',
    }));
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

async function updateEstadoUniverso(rowIndex, estado, fechaEnvio) {
  const sheets = await getSheets();
  await sheets.spreadsheets.values.update({
    spreadsheetId: SPREADSHEET_ID,
    range: `plan_universo!L${rowIndex}:M${rowIndex}`,
    valueInputOption: 'RAW',
    requestBody: {
      values: [[estado, fechaEnvio]],
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

async function writeLogUniverso(rows) {
  const sheets = await getSheets();

  await sheets.spreadsheets.values.clear({
    spreadsheetId: SPREADSHEET_ID,
    range: 'log_universo!A:G',
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
    range: 'log_universo!A1',
    valueInputOption: 'RAW',
    requestBody: {
      values: [header, ...data],
    },
  });
}

module.exports = {
  getModoYEtiqueta,
  getMensajes,
  getPendientesGest,
  getPendientesUniverso,
  updateEstadoGest,
  updateEstadoUniverso,
  writeLog,
  writeLogUniverso,
};
