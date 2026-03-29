# Baba Prospector — Especificación Técnica v2
# Documento para Claude en VS Code — "construí esto"

---

## Qué es este proyecto

Bot de Telegram para el equipo de ventas de **Baba Cervecería**.
El vendedor manda audios desde el bar → el bot transcribe → extrae campos estructurados → guarda en Google Sheets.

---

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Bot framework | `python-telegram-bot` v20+ (async) |
| Transcripción de audio | Groq Whisper (`whisper-large-v3`) |
| Extracción de campos | Groq LLM (`llama-3.3-70b-versatile`) |
| Storage | Google Sheets API v4 (`gspread`) |
| Configuración de campos | `config/fields.yaml` (fuente única de verdad) |
| Variables de entorno | `python-dotenv` |

---

## Principio de diseño central

**`config/fields.yaml` es la única fuente de verdad.**

Todos los campos, segmentos, estados y comportamiento del bot están definidos ahí.
El código nunca tiene campos hardcodeados — siempre los lee del YAML.
Para cambiar el cuestionario, solo se edita el YAML. El resto se adapta solo.

---

## Estructura de carpetas

```
baba_prospector/
├── main.py
├── config.py                        # Carga .env y fields.yaml
├── config/
│   └── fields.yaml                  # ← fuente única de verdad de campos
├── handlers/
│   ├── audio_handler.py
│   ├── text_handler.py
│   └── session.py
├── services/
│   ├── transcriber.py               # Groq Whisper → texto
│   ├── extractor.py                 # Groq LLM → JSON de campos
│   └── sheets.py                    # Guardar en Google Sheets
├── prompts/
│   └── extraction_prompt.py        # Genera el prompt dinámicamente desde fields.yaml
├── utils/
│   └── formatter.py                # Genera el mensaje de respuesta al vendedor
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## Variables de entorno (.env)

```env
TELEGRAM_BOT_TOKEN=
GROQ_API_KEY=
GOOGLE_SHEETS_ID=
GOOGLE_CREDENTIALS_JSON=./credentials.json
```

---

## config.py — carga del YAML

`config.py` debe:
1. Cargar las variables de entorno desde `.env`
2. Parsear `config/fields.yaml` con PyYAML
3. Exponer un objeto `Config` con:
   - `fields`: lista de campos del YAML
   - `segments`: dict de segmentos y sus marcas
   - `bar_states`: lista de estados posibles
   - `bot`: configuración del bot (comandos de cierre, behavior, etc.)
4. Exponer helpers:
   - `get_fields_by_priority(priority)` → lista de campos con esa prioridad
   - `get_fields_ordered_by_ask_priority()` → campos con ask_priority, ordenados
   - `get_segment_for_brand(brand_name)` → segmento inferido para una marca
   - `get_all_brand_aliases()` → dict plano {marca_lower: segmento} para lookup rápido

---

## session.py — estado por usuario

```python
# Estructura de sesión activa
sessions = {
    telegram_user_id: {
        "bar": {},          # dict con keys = field.key del YAML, values = lo capturado
        "audio_count": 0
    }
}
```

- El dict `bar` se inicializa con todas las keys del YAML en `null`
- Al llegar info nueva, se mergea: un campo ya capturado no se pisa salvo que el nuevo valor sea más completo
- Al cerrar el bar ("siguiente"/"listo"), se limpia la sesión

---

## prompts/extraction_prompt.py — prompt dinámico

Este módulo genera el prompt de extracción **dinámicamente** leyendo `fields.yaml`.

La función `build_extraction_prompt(transcription: str) -> str` debe:

1. Leer todos los campos del YAML y armar el schema JSON para el prompt
2. Incluir los aliases de cada campo como ejemplos de extracción
3. Incluir la tabla de segmentos con sus marcas
4. Devolver el prompt completo listo para enviar a Groq

**Estructura del prompt generado**:

```
Sos un asistente de campo para Baba Cervecería, una cervecería artesanal argentina.
Extraé la información del siguiente texto sobre un bar visitado.
Devolvé SOLO un JSON válido con la estructura exacta de abajo.
Usá null para campos no mencionados. No agregues texto fuera del JSON.

El texto puede estar en español rioplatense.
Aliases y expresiones a reconocer:
[generado dinámicamente desde aliases del YAML]

Segmentos de birra (inferir según marcas mencionadas):
[generado dinámicamente desde segments del YAML]
Si hay marcas de más de un segmento → "mixto"
Si no se mencionan marcas → null

JSON a completar:
[generado dinámicamente desde fields del YAML — solo keys y tipos, sin metadata]

Texto transcripto:
"{{TRANSCRIPCION}}"
```

---

## services/transcriber.py

1. Recibe path de archivo de audio (`.ogg`)
2. Convierte a `.mp3` con pydub
3. Envía a Groq Whisper con `language="es"` y `model="whisper-large-v3"`
4. Devuelve string con la transcripción
5. Elimina archivos temporales

```python
# Dependencia del sistema: ffmpeg
# pip: pydub, groq
```

---

## services/extractor.py

1. Recibe transcripción (string)
2. Llama a `build_extraction_prompt(transcription)`
3. Envía a Groq LLM con `model="llama-3.3-70b-versatile"`, `temperature=0`
4. Parsea la respuesta como JSON
5. Si el parse falla → reintenta una vez con mensaje de error explícito
6. Devuelve dict con los campos extraídos

---

## services/sheets.py

### Columnas

Las columnas de la hoja se generan **dinámicamente** desde `fields.yaml`.
El orden es: primero los campos en el orden del YAML, luego los metadata (id, fecha_visita, estado).

Al inicializar, `sheets.py` debe:
1. Verificar que la hoja `bares_prospectos` existe
2. Verificar que los headers de la fila 1 coinciden con los campos del YAML
3. Si la hoja está vacía, escribir los headers automáticamente

### Operaciones

- `append_bar(bar_data: dict) -> int`: agrega fila, devuelve número de fila
- `update_bar(row: int, bar_data: dict)`: pisa una fila existente
- `find_bar_by_name(name: str) -> int | None`: busca por nombre (case-insensitive), devuelve fila o None
- `get_last_n_bars(n: int) -> list[dict]`: devuelve las últimas n filas como lista de dicts

---

## handlers/audio_handler.py

Flujo por cada audio recibido:

1. Descargar audio a `/tmp/audio_{user_id}_{timestamp}.ogg`
2. Transcribir con `transcriber.transcribe(path)`
3. Extraer campos con `extractor.extract(transcription)`
4. Mergear con sesión activa: `session.merge(user_id, extracted_fields)`
5. Generar respuesta con `formatter.build_summary(session.get(user_id))`
6. Enviar respuesta al usuario
7. Limpiar archivos temporales

---

## handlers/text_handler.py

| Input | Acción |
|---|---|
| `"siguiente"` / `"listo"` (desde `bot.close_commands` del YAML) | Cerrar bar → guardar en Sheets → limpiar sesión |
| `/estado` | Mostrar campos capturados del bar activo |
| `/cancelar` | Descartar bar activo sin guardar |
| `/lista` | Últimos 5 bares guardados (`sheets.get_last_n_bars(5)`) |
| `/start` / `/help` | Bienvenida con instrucciones |
| Texto libre | Pasarlo por el extractor igual que un audio |

Para la confirmación de segmento: si el bot preguntó "¿Es correcto el segmento X?" y el usuario responde "sí" / "no" / una marca → manejar esa respuesta antes de pasarla al extractor.

---

## utils/formatter.py — respuesta al vendedor

`build_summary(bar: dict, config: Config) -> str` genera el mensaje de respuesta.

Lógica:
1. Leer campos con prioridad `clave` y `recomendado` del YAML en orden de `ask_priority`
2. Separar en capturados (valor != null) y faltantes (valor == null)
3. Armar el mensaje con el formato:

```
📍 [nombre]
📌 [direccion] — [barrio]

✅ Capturado:
  • [label del campo]: [valor]
  ...

⚠️ Falta información CLAVE/RECOMENDADA:
  • [label del campo faltante]
  ...

💬 Notas extra:
  "[comentarios]"

¿[pregunta sobre el campo faltante de mayor ask_priority]?
```

4. Si `segmento_inferido` está capturado pero `segmento_confirmado` es null → agregar línea de confirmación: `"Inferí segmento **[label]** ([marcas mencionadas]). ¿Es correcto?"`
5. Una sola pregunta al final, siempre la de mayor `ask_priority` que falte

---

## Detección de duplicados

Al recibir "siguiente"/"listo":
1. Buscar en Sheets con `sheets.find_bar_by_name(nombre)`
2. Si existe → preguntar: `"⚠️ Ya tengo un registro de [NOMBRE]. ¿Actualizar ese registro o crear uno nuevo?"`
3. Guardar la respuesta en sesión y actuar en el próximo mensaje

---

## requirements.txt

```
python-telegram-bot==20.7
groq==0.9.0
gspread==6.1.2
google-auth==2.29.0
pydub==0.25.1
python-dotenv==1.0.1
PyYAML==6.0.1
```

> `ffmpeg` debe estar instalado en el sistema (no es pip).
> Ubuntu/Debian: `sudo apt install ffmpeg`
> Mac: `brew install ffmpeg`

---

## Orden de construcción recomendado

1. `config/fields.yaml` — ya existe, no tocar
2. `config.py` — carga el YAML y expone helpers
3. `handlers/session.py` — estado en memoria
4. `services/transcriber.py` — Groq Whisper
5. `prompts/extraction_prompt.py` — prompt dinámico
6. `services/extractor.py` — Groq LLM → JSON
7. `services/sheets.py` — Google Sheets
8. `utils/formatter.py` — arma el mensaje de respuesta
9. `handlers/audio_handler.py` — orquesta el flujo de audio
10. `handlers/text_handler.py` — maneja texto y comandos
11. `main.py` — inicializa y arranca el bot

---

## Lo que Claude en VS Code debe construir

- Crear toda la estructura de carpetas y archivos
- Implementar cada módulo según esta spec
- **Nunca hardcodear campos** — siempre leerlos de `config/fields.yaml` via `config.py`
- El bot debe correr con `python main.py` sin errores
- Manejar errores: audio inentendible, JSON malformado, fallo de Sheets, fallo de Groq
