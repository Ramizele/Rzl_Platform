# whatsapp_bot

Bot que lee una Google Sheets con destinatarios y envía mensajes de WhatsApp automáticamente, de forma gratuita.

## Estado

`draft`

## Idea central

- **Fuente de datos**: Google Sheets (nombre, teléfono, mensaje, estado de envío)
- **Output**: Mensajes de WhatsApp enviados y sheet actualizada con el resultado
- **Costo**: $0

## Contexto de plataforma

- Registry: `rzl_database/systems/whatsapp_bot/`
- Pack: `rzl_gpt_apps/packs/draft/brainstorm_whatsapp_bot/`

## Stack (por decidir)

Ver análisis completo en `rzl_gpt_apps/packs/draft/brainstorm_whatsapp_bot/01_brainstorm.md`

| Opción | Stack | Cuándo |
|--------|-------|--------|
| Rápido/local | Node.js + whatsapp-web.js + googleapis | Arrancar ya, volumen bajo |
| Robusto/cloud | Python + Evolution API (Railway) + gspread | Producción, cualquier lenguaje |
| Sin código de protocolo | Python + Green API free + gspread | < 100 msg/día, máxima simplicidad |

## Estructura

```
docs/       ← decisiones técnicas, ADRs, contexto del proyecto
src/        ← código fuente del bot
worklog/    ← bitácora de sesiones de desarrollo
assets/     ← credentials.json template, sheet de ejemplo
```
