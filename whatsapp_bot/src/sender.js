const { randomDelay, sleep } = require('./utils');

const MAX_PER_HOUR = 50;
let sentThisHour = 0;
let hourStart = Date.now();

function resetHourIfNeeded() {
  if (Date.now() - hourStart >= 3_600_000) {
    sentThisHour = 0;
    hourStart = Date.now();
  }
}

async function checkRateLimit() {
  resetHourIfNeeded();
  if (sentThisHour >= MAX_PER_HOUR) {
    const waitMs = 3_600_000 - (Date.now() - hourStart);
    console.log(`  [rate-limit] ${MAX_PER_HOUR}/hora alcanzado. Esperando ${Math.ceil(waitMs / 60000)} min...`);
    await sleep(waitMs);
    sentThisHour = 0;
    hourStart = Date.now();
  }
}

async function sendText(client, chatId, message) {
  await client.sendPresenceUpdate('composing', chatId);
  // Delay proporcional al largo del mensaje (mín 1s, máx 4s)
  const typingMs = Math.min(message.length * 35 + Math.random() * 800, 4000);
  await sleep(typingMs);
  await client.sendMessage(chatId, message);
  await client.sendPresenceUpdate('paused', chatId);
}

async function sendImage(client, chatId, imageUrl, caption) {
  const { MessageMedia } = require('whatsapp-web.js');
  const media = await MessageMedia.fromUrl(imageUrl, { unsafeMime: true });
  await client.sendPresenceUpdate('composing', chatId);
  await sleep(1500);
  await client.sendMessage(chatId, media, { caption });
  await client.sendPresenceUpdate('paused', chatId);
}

async function sendMessage(client, chatId, message, imageUrl = null) {
  await checkRateLimit();

  if (imageUrl) {
    await sendImage(client, chatId, imageUrl, message);
  } else {
    await sendText(client, chatId, message);
  }

  sentThisHour++;
}

async function waitBetweenMessages() {
  const delay = randomDelay();
  console.log(`  Esperando ${(delay / 1000).toFixed(1)}s antes del próximo envío...`);
  await sleep(delay);
}

module.exports = { sendMessage, waitBetweenMessages };
