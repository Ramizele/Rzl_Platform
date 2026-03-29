# 01 — Brainstorm Técnico: Bar Prospector Bot

> Análisis de opciones para construir un bot que recibe audios desde el campo,
> transcribe la info de bares visitados, valida completitud y guarda los datos.

---

## Problema central

Tenés dos subproblemas independientes que se encadenan:

```
AUDIO  →  [Dimensión 1: Transcripción]  →  TEXTO
TEXTO  →  [Dimensión 2: Análisis]       →  DATOS ESTRUCTURADOS + VALIDACIÓN
```

Más una decisión de infraestructura:

```
[Dimensión 3: Canal]  →  Por dónde mandan los audios
[Dimensión 4: Storage]  →  Dónde queda guardado todo
```

---

## Dimensión 1 — Transcripción de audio a texto

### Contexto técnico
- **Formato de entrada**: WhatsApp y Telegram envían audios en OGG/OPUS. Todos los servicios de transcripción modernos lo soportan.
- **Idioma**: Español rioplatense con vocabulario de hostelería (capacidad, canilla, chopera, growler, etc.)
- **Duración esperada**: 15–90 segundos por audio. Algunos bares pueden generar 2–3 audios.
- **Latencia esperada**: El usuario está en el bar y espera respuesta. Ideal < 5 segundos.

---

### Opción A — OpenAI Whisper API
| | |
|---|---|
| **Costo** | ~$0.006 / minuto (muy barato para uso esporádico) |
| **Velocidad** | 2–5 segundos para audios cortos |
| **Español** | Excelente. Es el mejor modelo en español |
| **Setup** | Mínimo: 3 líneas de código, API key de OpenAI |
| **Formato** | Soporta OGG, MP3, M4A, WAV, WEBM |

**Pros**: Confiable, excelente precisión en español argentino, sin mantenimiento, API simple.
**Contras**: Pago por uso (aunque el costo es mínimo), dependencia de OpenAI.
**Ideal para**: MVP rápido, cuando ya tenés cuenta OpenAI.

---

### Opción B — Groq Whisper (Whisper Large v3 en Groq)
| | |
|---|---|
| **Costo** | **Gratis** en el tier actual (con límites de uso generosos) |
| **Velocidad** | < 1 segundo. Es el más rápido disponible |
| **Español** | Igual que OpenAI Whisper (mismo modelo base) |
| **Setup** | API key de Groq (gratis), API compatible con OpenAI |
| **Formato** | Soporta los mismos formatos que OpenAI Whisper |

**Pros**: Velocidad extrema, gratis, API casi idéntica a OpenAI (minimal code change).
**Contras**: Servicio más nuevo, menos garantías de uptime que OpenAI. Los límites gratuitos pueden cambiar.
**Ideal para**: MVP sin costo, si ya usás Groq para el LLM.

> **Recomendación para MVP**: Groq Whisper. Gratis, rápido, misma API que OpenAI — si luego querés migrar son 2 líneas de código.

---

### Opción C — Deepgram
| | |
|---|---|
| **Costo** | Tier gratuito con $200 de crédito al registrarse |
| **Velocidad** | ~1 segundo (muy rápido) |
| **Español** | Bueno, modelos específicos para español |
| **Setup** | API key, SDK propio |

**Pros**: Muy rápido, crédito inicial generoso, buena documentación.
**Contras**: SDK diferente, otro proveedor a manejar.
**Ideal para**: Si querés explorar fuera del ecosistema OpenAI.

---

### Opción D — AssemblyAI
| | |
|---|---|
| **Costo** | Tier gratuito + pay-per-use |
| **Velocidad** | 2–4 segundos |
| **Español** | Bueno |
| **Setup** | API key, SDK propio |
| **Extra** | Tiene análisis de sentimiento, diarización de hablantes, entity detection |

**Pros**: Features extras (podrías detectar automáticamente nombres de personas, lugares).
**Contras**: Costo más elevado que Whisper para uso sostenido.
**Ideal para**: Si querés features avanzadas en la transcripción misma.

---

### Opción E — Whisper local (open source)
| | |
|---|---|
| **Costo** | Gratis (computación propia) |
| **Velocidad** | Lento sin GPU (30–120 seg para un audio de 1 min en CPU) |
| **Español** | Excelente (mismo modelo) |
| **Setup** | Python, ffmpeg, 1–5 GB de descarga del modelo |

**Pros**: Privacidad total, sin costo, sin dependencia externa.
**Contras**: Lento en CPU, requiere mantener un servidor propio, complejo de deployar.
**Ideal para**: Si tenés GPU o si la privacidad es crítica. No recomendado para MVP.

---

### Tabla comparativa — Transcripción

| Opción | Costo | Velocidad | Precisión ESP | Setup | Recomendado |
|--------|-------|-----------|---------------|-------|-------------|
| Groq Whisper | Gratis | ⚡ < 1s | ★★★★★ | Mínimo | ✅ MVP |
| OpenAI Whisper API | ~$0.006/min | ★★★★ 2-5s | ★★★★★ | Mínimo | ✅ Fallback |
| Deepgram | Gratis (crédito) | ⚡ ~1s | ★★★★ | SDK propio | Alternativa |
| AssemblyAI | Gratis (tier) | ★★★ 2-4s | ★★★★ | SDK propio | Si necesitás extras |
| Whisper local | Gratis | ★ lento | ★★★★★ | Complejo | ❌ No para MVP |

---

## Dimensión 2 — Análisis e inteligencia del contenido

### Qué necesitamos hacer con el texto transcripto

Una vez que tenemos el texto, el bot debe:
1. **Extraer** los campos del bar de forma estructurada
2. **Validar** cuáles campos se llenaron y cuáles faltan
3. **Responder** con un resumen claro al usuario
4. **Acumular** si llegan múltiples audios del mismo bar

---

### Opción A — LLM con JSON Schema (recomendada)

**Flujo**:
```
Transcripción (texto)
  → Prompt: "Extraé los siguientes campos de este texto: [lista de campos] → JSON"
  → GPT-4o mini / Claude Haiku / Llama 3 (Groq)
  → JSON estructurado con campos completados y nulos
  → Código valida cuáles campos están vacíos
  → Respuesta al usuario
```

**Por qué funciona bien para este caso**:
- El usuario habla de forma natural ("está por San Telmo, en la calle Chile al 400, se llama La Cervecería del Sur")
- El LLM entiende el contexto y mapea sin necesidad de frases exactas
- Maneja perfectamente el español rioplatense y los modismos del sector
- Puede inferir el tipo de local del contexto ("es un bolichito de barrio" → tipo: bar/pub)
- Los campos faltantes simplemente quedan como `null` en el JSON

**Costo**: GPT-4o mini es muy barato (~$0.15/1M tokens input). Para textos de 300-500 palabras, estamos hablando de fracciones de centavo por bar.

**Ejemplo de prompt de extracción**:
```
Sos un asistente de campo para una cervecería artesanal.
Extraé la información del siguiente texto sobre un bar visitado.
Devolvé SOLO un JSON con esta estructura, usando null para campos no mencionados:

{
  "nombre": string | null,
  "direccion": string | null,
  "barrio": string | null,
  "tipo_local": "bar" | "restaurant" | "pub" | "boliche" | "cervecería" | "otro" | null,
  "contacto_nombre": string | null,
  "contacto_telefono": string | null,
  "contacto_instagram": string | null,
  "encargado_compras": string | null,
  "cervezas_actuales": string | null,
  "tiene_chopera": boolean | null,
  "tiene_heladera_propia": boolean | null,
  "volumen_estimado_litros_semana": number | null,
  "precio_pinta": number | null,
  "capacidad": number | null,
  "horarios": string | null,
  "estilo_local": string | null,
  "comentarios": string | null
}

Texto del campo: "{transcripcion}"
```

**Pros**: Robusto ante lenguaje informal, preciso, fácil de mantener, muy barato.
**Contras**: Requiere cuenta de LLM, latencia de 1-3 segundos adicionales.

---

### Opción B — Regex / NLP clásico

Patrones para detectar:
- Teléfonos: `\+?[0-9]{8,15}`
- Emails: patrón estándar
- Direcciones: relativamente difícil de capturar con regex

**Pros**: Sin costo de LLM, determinístico.
**Contras**: Frágil ante lenguaje natural, requiere hablar de forma muy estructurada, alto mantenimiento.
**Veredicto**: No recomendado. El LLM es superior en costo/beneficio.

---

### Opción C — Bot conversacional con memoria de sesión

**Flujo**:
```
Usuario: [audio con info parcial]
Bot: "Captaste nombre y dirección. Falta contacto, ¿tenés el nombre de alguien?"
Usuario: [audio con más info]
Bot: "Perfecto. Ahora solo falta el volumen estimado..."
...
Bot: "✅ Bar completo. Resumen: [muestra todo]"
```

**Pros**: Muy amigable, el bot guía activamente la carga.
**Contras**: Requiere mantener estado de sesión (qué bar está activo, qué campos faltan).
**Cuándo tiene sentido**: Como segunda iteración, después del MVP básico.

---

### Opción D — Híbrido (recomendado a mediano plazo)

Combina A + C:
- **Extracción automática** (Opción A) con cada audio
- **Notificación proactiva** de qué falta (no bloqueante)
- **Sesión abierta** para el bar actual (el usuario puede mandar más audios)
- **Confirmación final** cuando el usuario dice "listo", "siguiente bar", o similar

---

### Comportamiento de validación y checklist

**Niveles de importancia de los campos**:

```
🔴 CLAVE — Siempre queremos tenerlos (sin esto, el bar no sirve)
   • Nombre del bar
   • Dirección / Barrio

🟡 RECOMENDADO — Muy útil para el seguimiento comercial
   • Contacto (nombre)
   • Contacto (teléfono o Instagram)
   • Tipo de local
   • Cervezas que venden actualmente

🟢 ÚTIL — Enriquece el perfil comercial
   • Encargado de compras
   • ¿Tiene chopera?
   • ¿Tiene heladera propia?
   • Volumen estimado (litros/semana)
   • Precio al público (pinta)

⚪ OPCIONAL — Contexto adicional
   • Horarios de atención
   • Capacidad (personas)
   • Estilo / Público objetivo
   • Comentarios libres
```

**Formato de respuesta del bot**:
```
📍 Bar: La Cervecería del Sur
📌 Dirección: Chile 420, San Telmo

✅ Capturado:
  • Nombre
  • Dirección y barrio
  • Tipo: bar/cervecería
  • Contacto: Juan (11-5555-0000)
  • Tienen Antares y Patagonia actualmente

⚠️ Faltaría tener:
  • ¿Tienen chopera?
  • Volumen estimado

💬 Notas extra:
  "Buena onda el encargado, dijo que están evaluando sumar artesanales"

¿Mandás más info o pasamos al siguiente bar?
```

---

## Dimensión 3 — Canal de mensajería

### Opción A — Telegram (recomendado para MVP)

**¿Por qué Telegram?**
- API oficial, documentada, estable
- Soporte nativo para mensajes de voz (OGG/OPUS, sin conversión)
- Webhooks o long polling, ambos simples
- Gratis, sin riesgo de ban
- Excelente ecosistema de librerías: `python-telegram-bot`, `grammy` (Node.js), `telegraf` (Node.js)
- Los bots de Telegram no necesitan aprobación de ningún tipo

**Stack Node.js** (compatible con baba_bot):
```javascript
// Con Grammy (moderno, TypeScript-friendly)
import { Bot } from "grammy";
const bot = new Bot(process.env.TELEGRAM_TOKEN);

bot.on("message:voice", async (ctx) => {
  const file = await ctx.getFile();
  // file.file_path → URL de descarga del audio OGG
  // → transcribir → analizar → responder
});
```

**Stack Python**:
```python
# Con python-telegram-bot
from telegram.ext import Application, MessageHandler, filters

async def handle_voice(update, context):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    # → transcribir → analizar → responder
```

---

### Opción B — WhatsApp (whatsapp-web.js)

**Ventaja clave**: Mismo stack que baba_bot (Node.js + whatsapp-web.js), mismo canal que el equipo ya usa.

**Problemas**:
- whatsapp-web.js no es API oficial → riesgo de ban de cuenta
- Para recibir audios (no solo enviarlos), la integración es más compleja
- Requiere sesión activa (el celular conectado)
- Audio en WhatsApp: PTT (push-to-talk) en formato OGG/OPUS — técnicamente manejable

**Cuándo tiene sentido**: Si el equipo ya vive en WhatsApp y no quiere abrir otra app.

---

### Opción C — WhatsApp Business API (Meta)

- API oficial, robusta, sin riesgo de ban
- Recepción de mensajes de audio con webhook
- **Contras**: Proceso de aprobación de Meta, costo por conversación (~$0.02-0.05/conv), número de teléfono dedicado

**Cuándo tiene sentido**: Escala mayor, uso comercial formal, múltiples usuarios del equipo.

---

### Tabla comparativa — Canal

| Canal | Costo | Setup | Riesgo | Multi-usuario | Recomendado |
|-------|-------|-------|--------|---------------|-------------|
| Telegram | Gratis | ⚡ Simple | Sin riesgo | Nativo | ✅ MVP |
| WhatsApp (web.js) | Gratis | Medio | Riesgo ban | Complicado | ⚠️ Si ya usás |
| WhatsApp Business API | Pago | Complejo | Sin riesgo | Nativo | 🔮 A futuro |

---

## Dimensión 4 — Almacenamiento

### Opción A — Google Sheets (recomendado)

**Por qué**: baba_bot ya usa Google Sheets con service account. Podría ser la misma planilla o una conectada.

**Estructura sugerida**:
```
Hoja: bares_prospectos
  Columnas: id | nombre | barrio | dirección | tipo_local | contacto_nombre |
            contacto_tel | contacto_ig | encargado_compras | cervezas_actuales |
            tiene_chopera | tiene_heladera | volumen_lt_semana | precio_pinta |
            capacidad | horarios | estilo | notas | estado | fecha_visita | visitado_por
```

**Estados del bar**:
- `prospecto` — visitado, info cargada
- `contactado` → pasó a campaña de baba_bot
- `cliente` — confirmado como cliente
- `no_interesado` — descartado
- `revisar` — falta info o tiene dudas

**Integración con baba_bot**: Cuando un bar pasa a `contactado`, se copia automáticamente a la hoja `clientes` de baba_bot.

---

### Opción B — Notion Database

**Pros**: Vista de cards por estado (Kanban de prospección), filtros, fácil para el equipo.
**Contras**: API tiene rate limits, más complejo de implementar vs Sheets.
**Cuándo tiene sentido**: Si el equipo ya vive en Notion.

---

### Opción C — Airtable

Similar a Notion pero con mejor API. Tier gratuito generoso.

---

## Arquitectura completa del MVP

```
┌─────────────────────────────────────────────────────────────┐
│                    BAR PROSPECTOR BOT                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Usuario en el bar]                                        │
│       │ manda audio (OGG/OPUS)                              │
│       ↓                                                     │
│  ┌──────────┐    ┌───────────────────┐                     │
│  │ Telegram │    │  Groq Whisper API │                     │
│  │  Bot     │───>│  (transcripción)  │                     │
│  └──────────┘    └─────────┬─────────┘                     │
│                            │ texto                          │
│                            ↓                               │
│                  ┌───────────────────┐                     │
│                  │   GPT-4o mini /   │                     │
│                  │   Groq Llama      │                     │
│                  │  (extracción JSON)│                     │
│                  └─────────┬─────────┘                     │
│                            │ JSON estructurado              │
│                            ↓                               │
│                  ┌───────────────────┐                     │
│                  │  Checklist        │                     │
│                  │  Validator        │                     │
│                  │  (campos OK/falta)│                     │
│                  └─────┬──────┬──────┘                     │
│                        │      │                            │
│              respuesta │      │ guardar                    │
│                        ↓      ↓                            │
│              [Usuario] │  ┌──────────────┐                 │
│                        │  │ Google Sheets│                 │
│                        │  │  (storage)   │                 │
│                        │  └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

**Stack recomendado para MVP**:
- **Runtime**: Node.js (consistente con baba_bot)
- **Bot framework**: Grammy (Telegram)
- **Transcripción**: Groq Whisper API
- **LLM extractor**: GPT-4o mini o Groq Llama 3.1 (gratis)
- **Storage**: Google Sheets (reutilizar infra de baba_bot)
- **Deploy**: Local en tu máquina (igual que baba_bot en fase inicial)

**Costo mensual estimado** (30 bares/semana, 2 audios/bar):
- Groq Whisper: **$0** (tier gratuito)
- GPT-4o mini extracción: **~$0.50/mes**
- Telegram bot: **$0**
- Google Sheets: **$0**
- **Total: ~$0.50/mes**

---

## Decisiones pendientes

1. ¿Canal: Telegram o WhatsApp? → responder en `02_intake.md`
2. ¿Campos clave para Baba específicamente? → responder en `02_intake.md`
3. ¿El bot pregunta activamente o solo notifica lo que falta? → responder en `02_intake.md`
4. ¿Integración directa con baba_bot? → responder en `02_intake.md`
5. ¿Node.js o Python? → responder en `02_intake.md`
