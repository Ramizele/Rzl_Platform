---
asset_id: brainstorm_whatsapp_bot
asset_type: pack
status: draft
version: v0.1
owner: Rzl_Platform
updated: 2026-03-28
surface: chatgpt_projects
---

# Pack: Brainstorm — Bot de WhatsApp con Google Sheets

Pack para diseñar un bot de WhatsApp que envía mensajes usando una hoja de Google Sheets como fuente de destinatarios y datos, de forma 100% gratuita.

## Idea semilla

Bot que lee una Google Sheets → extrae destinatarios y contenido → envía mensajes de WhatsApp automáticamente. Sin costo.

## Cómo usar

**Paso 1 — Leer el brainstorming**
Abrí `01_brainstorm.md`. Contiene el análisis completo de opciones técnicas gratuitas con recomendaciones.

**Paso 2 — Completar el intake**
Abrí `02_intake.md` y respondé las preguntas para definir el alcance exacto de tu caso.

**Paso 3 — Armar el system prompt**
Abrí `03_agent_system_prompt.md`, reemplazá los `[PLACEHOLDERS]` y pegá en un ChatGPT Project dedicado al proyecto.

## Output

Al finalizar los 3 pasos tenés:
- Decisión técnica documentada (qué stack usar y por qué)
- Un agente de ChatGPT especializado en tu bot
- Brief del proyecto listo para arrancar implementación

## Plataforma

- Registry: `rzl_database/systems/whatsapp_bot/`
- Workspace: `projects/whatsapp_bot/`
- Mover a `packs/released/` cuando el bot esté en producción
