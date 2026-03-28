function normalizePhone(telefono) {
  let cleaned = String(telefono).replace(/\D/g, '');

  // Ya está en formato internacional correcto (549XXXXXXXXXX)
  if (cleaned.startsWith('549') && cleaned.length === 13) return cleaned;

  // 54 + 10 dígitos sin el 9 → insertar 9
  if (cleaned.startsWith('54') && cleaned.length === 12) {
    return '549' + cleaned.slice(2);
  }

  // Comienza con 0 (formato local argentino: 011..., 0221..., etc.)
  if (cleaned.startsWith('0') && cleaned.length === 11) {
    return '549' + cleaned.slice(1);
  }

  // 10 dígitos sueltos (area + número, sin prefijo)
  if (cleaned.length === 10) {
    return '549' + cleaned;
  }

  // 11 dígitos empezando con 9 (9 + area + número)
  if (cleaned.startsWith('9') && cleaned.length === 11) {
    return '54' + cleaned;
  }

  return cleaned;
}

function isValidPhone(telefono) {
  return /^549\d{10}$/.test(telefono);
}

function replaceName(message, nombre) {
  if (!nombre || !nombre.trim()) return message;
  return message.replace(/\{\{nombre\}\}/g, nombre.trim());
}

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomDelay(min = 8000, max = 20000) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function formatTimestamp() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

module.exports = {
  normalizePhone,
  isValidPhone,
  replaceName,
  pickRandom,
  randomDelay,
  sleep,
  formatTimestamp,
};
