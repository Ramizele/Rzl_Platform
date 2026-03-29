---
asset_id: brainstorm_bar_prospector
asset_type: pack
status: draft
version: v0.1
owner: Rzl_Platform
updated: 2026-03-29
surface: chatgpt_projects
tags: [baba, prospecting, audio, transcription, bars]
---

# Brainstorm Pack — Bar Prospector Bot

## Problema que resuelve

Cuando el equipo de Baba sale a visitar bares para prospectar clientes, la información se recolecta de forma informal: notas en el celu, mensajes sueltos, fotos, etc. Al final del día, falta info, se duplican bares, y no hay registro estructurado para darle seguimiento.

**Bar Prospector Bot** resuelve esto: mandás audios desde el bar, el bot transcribe, extrae la información relevante, te avisa qué datos capturó y qué falta, y guarda todo en un lugar centralizado.

## Contexto de negocio

Este proyecto forma parte del workflow comercial de **Baba Cervecería**:

```
Prospección de bares → Registro en Bar Prospector → Campañas con baba_bot
```

- `baba_bot` (ya existente) → envía mensajes de WhatsApp a clientes desde Google Sheets
- `bar_prospector` (este proyecto) → alimenta esa base de clientes desde el campo

## Flujo del bot

```
[Usuario en el bar]
  ↓ manda audio por Telegram / WhatsApp
  ↓ Bot transcribe audio → texto
  ↓ LLM extrae campos estructurados del bar
  ↓ Bot valida checklist de información
  ↓ Respuesta: ✅ qué captó | ⚠️ qué falta | 💬 comentarios extra
  ↓ Info guardada en Google Sheets / Notion / etc.
```

## Estructura del pack

Este pack está organizado en 3 pasos progresivos:

### Paso 1 — Leer el brainstorm técnico
→ [`01_brainstorm.md`](01_brainstorm.md)

Explora las opciones técnicas para las dos dimensiones del problema:
- **Dimensión 1**: ¿Cómo transcribir el audio a texto? (Whisper, Groq, Deepgram, etc.)
- **Dimensión 2**: ¿Cómo analizar y validar la información del bar? (LLM extractor, checklist, conversación)
- **Dimensión 3**: ¿Por qué canal? (Telegram vs WhatsApp)
- Propuesta de campos base para prospectar bares
- Arquitectura sugerida para el MVP

### Paso 2 — Completar el intake
→ [`02_intake.md`](02_intake.md)

Cuestionario para definir el proyecto según tus necesidades:
- Qué campos del bar querés capturar (base + personalizados)
- Canal de mensajería
- Comportamiento del bot
- Almacenamiento y output
- Stack técnico preferido

### Paso 3 — Generar el prompt del agente
→ [`03_agent_system_prompt.md`](03_agent_system_prompt.md)

Prompt listo para pegar en **ChatGPT Projects**. Completás los placeholders con las respuestas del intake y tenés un agente especializado funcionando inmediatamente.

---

> **Próximo paso después del brainstorming**: Si avanzás a implementación, crear `rzl_database/systems/bar_prospector/` y el workspace `bar_prospector/` en la raíz del repo, siguiendo `CONVENTION_project_workspace_v1.md`.
