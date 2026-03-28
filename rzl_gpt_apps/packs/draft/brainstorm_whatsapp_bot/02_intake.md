# Intake — Bot de WhatsApp con Google Sheets

Respondé las preguntas. Este documento alimenta directamente el system prompt del agente.
Dejá en blanco lo que no sabés — el agente te ayuda a definirlo.

---

## 1. Concepto

**¿Cuál es el propósito de los mensajes?** (campañas, recordatorios, notificaciones, seguimiento, etc.)
>

**¿Los mensajes son personalizados por contacto o es el mismo texto para todos?**
- [ ] Mismo mensaje para todos
- [ ] Personalizado por contacto (nombre, datos específicos, etc.)
- [ ] Combinación

**¿Quién va a operar el bot?** (vos, un equipo, alguien no técnico)
>

**Nombre del proyecto** (snake_case — ej: `whatsapp_notificaciones`, `bot_seguimiento`):
>

---

## 2. Escala y frecuencia

**Cantidad estimada de mensajes por envío:**
- [ ] Pocos (< 50)
- [ ] Medio (50 – 200)
- [ ] Alto (> 200)

**Frecuencia de uso:**
- [ ] Una sola vez (one-shot)
- [ ] Periódico — cada: `[ ] hora` `[ ] día` `[ ] semana` `[ ] mes` `[ ] manual`
- [ ] Reactivo (se activa cuando hay filas nuevas en la sheet)

**¿El envío es urgente / en tiempo real o puede tener demora?**
>

---

## 3. Google Sheets

**¿Ya tenés la sheet creada?**
- [ ] Sí — ¿qué columnas tiene? ___
- [ ] No — voy a crearla

**¿Los números de teléfono ya están en formato internacional?** (ej: 5491112345678)
- [ ] Sí
- [ ] No — están en otro formato: ___
- [ ] Mixto

**¿Querés que el bot actualice la sheet con el estado del envío?** (columna enviado/error)
- [ ] Sí
- [ ] No

---

## 4. Mensajes

**¿Incluyen solo texto o también archivos/imágenes?**
- [ ] Solo texto
- [ ] Texto + imágenes
- [ ] Texto + documentos (PDF, etc.)
- [ ] Combinación

**¿Los mensajes tienen variables dinámicas?** (nombre del destinatario, fechas, montos, etc.)
- [ ] No, texto fijo
- [ ] Sí — ¿cuáles? (ej: `{{nombre}}`, `{{monto}}`)

**¿Tenés un ejemplo del mensaje que querés enviar?**
>

---

## 5. Entorno de ejecución

**¿Dónde querés correr el bot?**
- [ ] Local (mi PC) — el teléfono tiene que estar conectado a WhatsApp Web
- [ ] Servidor en la nube (gratis) — Railway, Render, etc.
- [ ] Sin definir — recomendame

**¿Tenés preferencia de lenguaje?**
- [ ] Python
- [ ] Node.js / JavaScript
- [ ] Sin preferencia — elegí el más adecuado

**¿El número de WhatsApp que vas a usar es personal o dedicado?**
- [ ] Personal (el mío de siempre)
- [ ] Número dedicado para el bot

---

## 6. Restricciones y contexto

**¿Es importante que no haya riesgo de ban de la cuenta?**
- [ ] Sí, es crítico → preferir opciones oficiales (Green API o Meta)
- [ ] Es aceptable el riesgo con uso responsable

**¿Tenés alguna restricción técnica?** (sin instalar Node.js, sin servidor, etc.)
>

**¿Hay algo ya implementado o un intento anterior?**
- [ ] No
- [ ] Sí — ¿qué? ___

**Contexto adicional:**
>
