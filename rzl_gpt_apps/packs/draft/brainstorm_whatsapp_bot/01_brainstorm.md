# Brainstorm — Bot de WhatsApp con Google Sheets (gratuito)

## Problema a resolver

Enviar mensajes de WhatsApp de forma automatizada a una lista de contactos que vive en Google Sheets, sin pagar por APIs ni servicios de terceros.

---

## Restricciones del ecosistema de WhatsApp

Antes de elegir una solución, hay que entender el contexto:

| Factor | Detalle |
|--------|---------|
| **API oficial (Meta)** | Requiere cuenta Business verificada, número dedicado, aprobación de Meta |
| **Costo oficial** | Gratis hasta 1.000 conversaciones/mes iniciadas por la empresa (desde jun 2025 cambia modelo) |
| **Enfoque no oficial** | Simula WhatsApp Web en el browser — gratis, pero viola ToS de WhatsApp |
| **Riesgo no oficial** | Posible ban de cuenta si se detecta automatización masiva |
| **Escala personal/chica** | Enfoque no oficial funciona bien para uso personal o grupos pequeños |

---

## Opciones técnicas gratuitas

### Opción A — whatsapp-web.js (Node.js) ⭐ Recomendada para empezar

**Qué es:** Librería Node.js que controla WhatsApp Web mediante Puppeteer. Escanear QR con el teléfono y listo.

**Cómo funciona:**
1. El bot abre WhatsApp Web en segundo plano
2. Autenticás con QR una sola vez (la sesión persiste)
3. Lees la Google Sheet → iteras contactos → enviás mensajes

**Stack:**
```
Node.js
└── whatsapp-web.js       ← controla WhatsApp Web
└── googleapis            ← lee Google Sheets
└── node-cron (opcional)  ← ejecución programada
```

**Pros:**
- Más documentada y con más ejemplos disponibles
- Multi-media: texto, imágenes, archivos, botones
- Sesión persistente (no hay que escanear QR cada vez)
- Comunidad activa, muchos ejemplos

**Contras:**
- Requiere Node.js instalado
- Puppeteer pesa ~300MB
- Viola ToS de WhatsApp — riesgo de ban con uso masivo
- El teléfono tiene que estar con batería/internet (igual que WhatsApp Web)

**Costo:** $0

---

### Opción B — Baileys (Node.js)

**Qué es:** Librería Node.js que implementa el protocolo de WhatsApp directamente (sin Puppeteer). Más liviana y potente.

**Pros:**
- Sin Puppeteer — mucho más liviana
- Más estable para producción
- Usada por Evolution API y WPPConnect como base
- Soporta multi-device

**Contras:**
- Más compleja de configurar que whatsapp-web.js
- Menos ejemplos de inicio rápido
- También viola ToS

**Cuándo elegirla:** Si vas a escalar o necesitás correr en un servidor sin browser disponible.

**Costo:** $0

---

### Opción C — Evolution API (self-hosted) ⭐ Recomendada para producción

**Qué es:** Servidor REST open source que expone endpoints HTTP para enviar mensajes de WhatsApp. Corre sobre Baileys.

**Cómo funciona:**
1. Levantás Evolution API en Railway / Render / VPS (hay free tiers)
2. Tu script (Python o cualquier lenguaje) hace requests HTTP al servidor
3. El servidor se encarga de todo el protocolo de WhatsApp

**Stack:**
```
Evolution API (self-hosted, gratis en Railway)
└── Baileys bajo el capó

Tu script (Python o Node)
└── requests / axios       ← llama a Evolution API
└── gspread / googleapis   ← lee Google Sheets
```

**Pros:**
- Interfaz HTTP simple — cualquier lenguaje puede usarla
- Panel de administración web incluido
- Más fácil de mantener a largo plazo
- Railway tiene free tier (suficiente para este caso)

**Contras:**
- Requiere deploy en un servidor (aunque sea gratuito)
- Un poco más de setup inicial

**Costo:** $0 (Evolution API gratis + Railway free tier)

---

### Opción D — Green API (free tier)

**Qué es:** Servicio de API de WhatsApp con un plan gratuito.

**Plan gratuito:** 100 mensajes/día, 1 instancia

**Stack:**
```
Python o cualquier lenguaje
└── requests → Green API (REST)
└── gspread → Google Sheets
```

**Pros:**
- Muy fácil de integrar (REST simple)
- No requiere manejar el protocolo de WhatsApp
- Más seguro que las opciones no oficiales (aunque sigue siendo semi-oficial)

**Contras:**
- Límite de 100 mensajes/día en plan gratuito
- Dependés de un tercero

**Costo:** $0 para hasta 100 mensajes/día

---

### Opción E — Meta WhatsApp Business API (oficial)

**Qué es:** La API oficial de Meta para WhatsApp Business.

**Costo:** Gratis hasta 1.000 conversaciones iniciadas por empresa/mes

**Pros:**
- Oficial — sin riesgo de ban
- Confiable para producción

**Contras:**
- Requiere cuenta Business verificada con Meta
- Número de teléfono dedicado (no tu número personal)
- Templates de mensajes deben ser aprobados por Meta
- Setup complejo (Meta Developer Console, webhook, etc.)
- No sirve para enviar mensajes a cualquier número — el destinatario tiene que haber iniciado conversación o estar en un template aprobado

**Costo:** $0 hasta 1.000 conversaciones/mes (después se cobra por conversación)

---

## Integración con Google Sheets

Independiente del enfoque de WhatsApp, la lectura de la sheet es la misma:

### Python (recomendado para simplicidad)
```python
import gspread
from google.oauth2.service_account import Credentials

# Autenticación con Service Account (gratuito)
creds = Credentials.from_service_account_file('credentials.json', scopes=[...])
client = gspread.authorize(creds)

sheet = client.open("Mi Lista de Contactos").sheet1
rows = sheet.get_all_records()
# rows = [{"nombre": "Juan", "telefono": "5491112345678", "mensaje": "Hola!"}]
```

### Node.js
```js
const { google } = require('googleapis');
const sheets = google.sheets({ version: 'v4', auth });
const res = await sheets.spreadsheets.values.get({ spreadsheetId, range: 'Sheet1' });
```

**Setup Google Sheets API (gratuito):**
1. Google Cloud Console → crear proyecto → activar Sheets API
2. Crear Service Account → descargar `credentials.json`
3. Compartir la sheet con el email del Service Account

---

## Comparativa de opciones

| Opción | Dificultad | Riesgo | Límite mensajes | Lenguaje | Recomendado |
|--------|-----------|--------|-----------------|----------|-------------|
| whatsapp-web.js | Baja | Medio | Sin límite | Node.js | ✅ Para empezar |
| Baileys | Media | Medio | Sin límite | Node.js | Para escalar |
| Evolution API | Media | Medio | Sin límite | Cualquiera | ✅ Para producción |
| Green API | Muy baja | Bajo | 100/día | Cualquiera | Si el volumen es bajo |
| Meta oficial | Alta | Ninguno | 1.000/mes | Cualquiera | Si necesitás garantías |

---

## Recomendación según caso de uso

### Caso: Uso personal / equipo pequeño, < 200 mensajes por vez
→ **whatsapp-web.js + Google Sheets API**
→ Stack: Node.js local, fácil de probar y extender

### Caso: Quiero correr en la nube gratis, cualquier lenguaje
→ **Evolution API en Railway + Python con gspread**
→ Stack más mantenible a largo plazo

### Caso: Volumen muy bajo (< 100/día), sin querer lidiar con protocolo de WhatsApp
→ **Green API free tier + Python**
→ La opción más simple de todas

### Caso: Uso formal/empresarial, mensajes masivos, sin riesgo
→ **Meta WhatsApp Business API**
→ Requiere más setup pero es la única forma oficial

---

## Stack recomendado para este proyecto

Dado que el requisito es **gratuito** y **usar Google Sheets como fuente**:

```
Opción 1 (más simple, arrancar rápido):
  Node.js + whatsapp-web.js + googleapis

Opción 2 (más robusta, fácil de mantener):
  Python + Evolution API (Railway) + gspread
```

---

## Estructura de la Google Sheets sugerida

| columna | tipo | descripción |
|---------|------|-------------|
| `nombre` | texto | Nombre del destinatario |
| `telefono` | texto | Número en formato internacional sin + (ej: `5491112345678`) |
| `mensaje` | texto | Mensaje personalizado (puede tener variables) |
| `estado` | texto | `pendiente` / `enviado` / `error` — el bot actualiza esta columna |
| `fecha_envio` | fecha | Timestamp de cuándo se envió |

El bot marca cada fila como `enviado` después de procesar para no mandar dos veces.

---

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Ban de cuenta (opciones no oficiales) | Usar delays entre mensajes (5-15 seg), no enviar masivo de golpe |
| Cambios en WhatsApp Web rompen la lib | Mantener dependencias actualizadas, usar versiones estables |
| Credenciales Google expuestas | Nunca commitear `credentials.json`, usar `.env` o variables de entorno |
| Mensajes duplicados | Columna `estado` en la sheet actúa como flag |
