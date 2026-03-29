# 02 — Intake: Bar Prospector Bot

> Completá este cuestionario para definir tu proyecto.
> Las respuestas de este intake son los valores que van a reemplazar los placeholders
> en `03_agent_system_prompt.md`.

---

## Sección 1 — Concepto y alcance

**1.1 ¿Cuál es el nombre del proyecto / bot?**
```
Respuesta:
```

**1.2 ¿Quién lo va a usar?**
*(Solo vos, vos + otro vendedor, todo el equipo — cuántas personas)*
```
Respuesta:
```

**1.3 ¿Cuántos bares por semana estimás visitar?**
*(Contexto para dimensionar el tier gratuito de las APIs)*
```
Respuesta:
```

**1.4 ¿Los audios van a ser en español rioplatense?**
*(Groq/Whisper tienen excelente soporte, pero ayuda saberlo para el prompt de extracción)*
```
Respuesta:
```

---

## Sección 2 — Canal de mensajería

**2.1 ¿Preferís Telegram o WhatsApp?**
*(Ver análisis en `01_brainstorm.md` → Dimensión 3)*

- [ ] Telegram — recomendado para MVP (API oficial, gratis, sin riesgo de ban)
- [ ] WhatsApp (whatsapp-web.js) — mismo stack que baba_bot, pero riesgo de ban
- [ ] Explorar WhatsApp Business API — más formal, pago
- [ ] No lo sé aún

```
Decisión y razonamiento:
```

**2.2 ¿Querés que sea el mismo bot que baba_bot o uno separado?**

- [ ] Separado — más limpio, cada bot tiene su responsabilidad
- [ ] Parte de baba_bot — menos apps, pero mezcla responsabilidades
- [ ] Mismo número/cuenta de WhatsApp, comandos distintos

```
Decisión:
```

---

## Sección 3 — Campos del bar

### 3.1 De los campos base del brainstorm, ¿cuáles son tus CLAVE?

*(Los clave generan advertencia especial si están vacíos. El bot siempre los prioriza.)*

Campos base sugeridos:

| Campo | Nivel por defecto | ¿Lo cambiás? |
|-------|-------------------|--------------|
| Nombre del bar | 🔴 Clave | |
| Dirección / Barrio | 🔴 Clave | |
| Contacto (nombre) | 🟡 Recomendado | |
| Contacto (teléfono o IG) | 🟡 Recomendado | |
| Tipo de local | 🟡 Recomendado | |
| Cervezas actuales | 🟡 Recomendado | |
| Encargado de compras | 🟢 Útil | |
| ¿Tiene chopera? | 🟢 Útil | |
| ¿Tiene heladera propia? | 🟢 Útil | |
| Volumen estimado (lt/sem) | 🟢 Útil | |
| Precio pinta (al público) | 🟢 Útil | |
| Horarios de atención | ⚪ Opcional | |
| Capacidad (personas) | ⚪ Opcional | |
| Estilo / Público objetivo | ⚪ Opcional | |
| Notas / Comentarios libres | Siempre habilitado | — |

```
Cambios a los niveles:
```

### 3.2 ¿Agregás algún campo específico de Baba?

*(Ejemplo: "¿Tienen cava para vinos?", "¿Venden tirada por litro?", "¿Tienen delivery propio?")*

```
Campos adicionales:
```

### 3.3 ¿Cómo querés clasificar el estado de cada bar?

Estados sugeridos: `prospecto` → `contactado` → `cliente` / `no_interesado` / `revisar`

```
Estados que querés usar y su significado:
```

### 3.4 ¿Querés registrar quién visitó cada bar?

*(Útil si hay más de un vendedor en el equipo)*

- [ ] Sí, campo `visitado_por`
- [ ] No es necesario (uso individual)

---

## Sección 4 — Comportamiento del bot

**4.1 ¿Querés que el bot pregunte activamente los campos faltantes?**

- [ ] **Activo**: "Captaste nombre y dirección. ¿Tenés el contacto del encargado?"
- [ ] **Pasivo**: Solo avisa qué falta, sin preguntar — el usuario decide qué completar
- [ ] **Híbrido**: Avisa siempre, pregunta solo por los campos CLAVE

```
Decisión:
```

**4.2 ¿Podés mandar múltiples audios para el mismo bar?**

*(El bot acumula la info de todos los audios hasta que confirmás que terminaste con ese bar)*

- [ ] Sí, quiero poder mandar varios audios del mismo bar
- [ ] No, cada audio = un bar completo

```
Decisión:
```
¿Cómo le decís al bot que terminaste con un bar y querés pasar al siguiente?
*(Ej: "siguiente", "listo", "próximo bar", /nuevo)*
```
Comando de "bar completo":
```

**4.3 ¿Querés poder editar o corregir info ya cargada?**

- [ ] Sí — comando `/editar [campo] [valor]` o conversación
- [ ] No en la primera versión

```
Decisión:
```

**4.4 ¿Necesitás un modo "test" para probar sin guardar datos reales?**

- [ ] Sí — útil en desarrollo
- [ ] No necesario

---

## Sección 5 — Almacenamiento y output

**5.1 ¿Dónde querés que quede la información de los bares?**

- [ ] **Google Sheets** — misma infra que baba_bot, visual, compartible *(recomendado)*
- [ ] **Notion database** — más visual, Kanban por estado
- [ ] **Airtable** — similar a Notion, buena API gratuita
- [ ] **JSON local** — simple, sin dependencias cloud
- [ ] **Otro**: ___

```
Decisión:
```

**5.2 ¿En qué spreadsheet / base de datos?**
*(Si es Sheets: ¿la misma que baba_bot o una nueva?)*

```
Respuesta:
```

**5.3 ¿Necesitás exportar a algún formato?**

- [ ] CSV para análisis en Excel/Sheets
- [ ] PDF de ficha por bar
- [ ] No por ahora

**5.4 ¿Querés integración con baba_bot?**

*(Cuando un bar prospecto confirma interés, pasarlo automáticamente a la hoja `clientes` de baba_bot)*

- [ ] Sí — integración directa
- [ ] No, los mantengo separados
- [ ] Más adelante

```
Decisión:
```

---

## Sección 6 — Stack y restricciones

**6.1 ¿Preferís Node.js o Python?**

- [ ] **Node.js** — consistente con baba_bot (whatsapp-web.js, googleapis)
- [ ] **Python** — más natural para IA/ML, ecosystem de bots también excelente
- [ ] No tengo preferencia

```
Decisión:
```

**6.2 ¿Tenés cuenta y API key de alguno de estos servicios?**

- [ ] OpenAI (para Whisper + GPT-4o mini)
- [ ] Groq (para Whisper + Llama — gratis)
- [ ] Deepgram
- [ ] Ninguno aún

```
Servicios disponibles:
```

**6.3 ¿Tenés restricción de costo mensual?**

*(El MVP estimado es ~$0.50/mes con Groq gratis + GPT-4o mini. ¿Hay límite?)*

```
Restricción de costo:
```

**6.4 ¿Dónde va a correr el bot?**

- [ ] Local (mi máquina) — igual que baba_bot en fase inicial
- [ ] Railway / Render / VPS — siempre encendido
- [ ] No lo sé aún

```
Decisión:
```

---

## Resumen de decisiones

Una vez que completaste el cuestionario, resumí las decisiones clave acá:

```markdown
- Nombre del bot:
- Canal:
- Stack:
- Transcripción (API):
- LLM extractor:
- Storage:
- Campos clave: nombre, dirección, +
- Comportamiento bot: activo / pasivo / híbrido
- Integración baba_bot: sí / no / luego
- Deploy:
```

→ Con este resumen, pasá a `03_agent_system_prompt.md` y completá los placeholders.
