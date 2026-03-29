---
project: baba_prospector
status: draft
version: v0.1
stack: Python 3.11 / python-telegram-bot / Groq / Google Sheets
updated: 2026-03-29
---

# Baba Prospector Bot

Bot de Telegram para el equipo de ventas de Baba Cervecería.
Manda un audio desde el bar → el bot transcribe, extrae los campos del prospecto y confirma qué falta.

## Flujo

```
audio (OGG)
  → Groq Whisper → texto
  → Groq LLM (Llama 3.3) → JSON de campos
  → Validación de checklist
  → Respuesta al vendedor: ✅ capturado / ⚠️ faltante / 💬 notas
  → "siguiente" / "listo" → guarda en Google Sheets
```

## Setup

### 1. Requisitos del sistema

- Python 3.11+
- `ffmpeg` instalado y en PATH

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Mac
brew install ffmpeg

# Windows — descargar desde https://ffmpeg.org/download.html y agregar al PATH
```

### 2. Dependencias Python

```bash
cd baba_prospector
pip install -r requirements.txt
```

### 3. Variables de entorno

```bash
cp .env.example .env
# Editar .env con los valores reales
```

Necesitás:
- `TELEGRAM_BOT_TOKEN` — crear el bot con @BotFather
- `GROQ_API_KEY` — cuenta gratuita en console.groq.com
- `GOOGLE_SHEETS_ID` — ID del spreadsheet
- `GOOGLE_CREDENTIALS_JSON` — path al JSON del Service Account

### 4. Google Sheets — Service Account

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto → habilitar **Google Sheets API** y **Google Drive API**
3. Crear Service Account → descargar JSON de credenciales
4. Guardar como `credentials.json` en la raíz del proyecto
5. Compartir el spreadsheet con el email del Service Account (como editor)

### 5. Correr el bot

```bash
python main.py
```

## Estructura

```
baba_prospector/
├── main.py                      # Entry point
├── config.py                    # Carga .env + fields.yaml, helpers
├── config/
│   └── fields.yaml              # ← fuente única de verdad de campos
├── handlers/
│   ├── audio_handler.py         # Flujo de mensajes de voz
│   ├── text_handler.py          # Comandos y texto libre
│   └── session.py               # Estado en memoria por usuario
├── services/
│   ├── transcriber.py           # Groq Whisper
│   ├── extractor.py             # Groq LLM → JSON
│   └── sheets.py                # Google Sheets
├── prompts/
│   └── extraction_prompt.py     # Prompt dinámico desde YAML
├── utils/
│   └── formatter.py             # Mensajes de respuesta
├── docs/
├── worklog/
├── assets/
├── .env.example
└── requirements.txt
```

## Comandos del bot

| Comando | Acción |
|---------|--------|
| `/start` / `/help` | Bienvenida e instrucciones |
| `/estado` | Ver info capturada del bar activo |
| `/cancelar` | Descartar el bar sin guardar |
| `/lista` | Últimos 5 bares guardados |
| `siguiente` / `listo` | Cerrar y guardar el bar activo |

## Configurar campos

Todo el comportamiento del bot está en `config/fields.yaml`:

- Agregar un campo → nuevo ítem en `fields:`
- Cambiar prioridad → modificar `priority:` (clave / recomendado / util / opcional)
- Cambiar comportamiento → `bot.behavior:` (activo / pasivo / hibrido)
- Agregar una marca de cerveza → agregar en `segments:`

No hace falta tocar el código Python para estos cambios.

## Contexto de negocio

Este bot es upstream del workflow de Baba:

```
Baba Prospector (este bot) → Google Sheets → baba_bot (WhatsApp sender)
```

Los bares prospectos se guardan en la hoja `bares_prospectos`.
Cuando un bar confirma interés, se pasa manualmente a la hoja `clientes` de baba_bot para las campañas de WhatsApp.
