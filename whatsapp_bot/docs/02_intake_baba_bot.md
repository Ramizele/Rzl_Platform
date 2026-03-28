# Intake — baba_bot

---

## 1. Concepto

**¿Cuál es el propósito de los mensajes?**
> Campañas/promociones, recordatorios de pago/cobranzas, notificaciones de pedidos

**¿Los mensajes son personalizados por contacto o es el mismo texto para todos?**
- [x] Personalizado por contacto (nombre, etiqueta, datos del cliente)

**¿Quién va a operar el bot?**
> Solo yo

**Nombre del proyecto:**
> `baba_bot`

---

## 2. Escala y frecuencia

**Cantidad estimada de mensajes por envío:**
- [x] Medio (50 – 200)

**Frecuencia de uso:**
- [x] Manual (cuando el operador lo decide)

**¿El envío es urgente / en tiempo real o puede tener demora?**
> Puede tener demora — no es tiempo real

---

## 3. Google Sheets — Arquitectura de tres hojas

### Hoja 1: `clientes` (maestro)
| columna | detalle |
|---|---|
| `cliente` | Nombre del local / empresa |
| `telefono` | Número en formato mixto — el bot normaliza |
| `nombre_contacto` | Nombre de la persona (puede estar vacío) |

### Hoja 2: `campañas` (donde se arma cada envío)
| columna | detalle |
|---|---|
| `cliente` | Nombre del local — el bot hace el lookup en `clientes` por código |
| `etiqueta` | Define qué pool de mensajes usar (ej: `promo`, `cobranza`, `pedido`) |
| `imagen_url` | Opcional — si tiene valor, se envía imagen + caption |
| `estado` | `pendiente` / `enviado` / `error` — el bot actualiza |
| `fecha_envio` | Timestamp que escribe el bot |

### Hoja 3: `mensajes` (templates por etiqueta)
| columna | detalle |
|---|---|
| `etiqueta` | Debe coincidir con las etiquetas de `campañas` |
| `mensaje_1` | Primera variante |
| `mensaje_2` | Segunda variante |
| `mensaje_3` | Tercera variante (opcional) |

**Lógica del bot:**
1. Lee filas con `estado = pendiente` en `campañas`
2. Busca el `cliente` en `clientes` → obtiene `telefono` y `nombre_contacto`
3. Normaliza el teléfono al formato internacional
4. Busca la `etiqueta` en `mensajes` → elige una variante al azar
5. Si hay `nombre_contacto` → usa `{{nombre}}`; si no → usa variante sin nombre
6. Si hay `imagen_url` → envía imagen + caption; si no → solo texto
7. Actualiza `estado` y `fecha_envio` en `campañas`

**¿Querés que el bot actualice la sheet con el estado del envío?**
- [x] Sí

---

## 4. Mensajes

**¿Incluyen solo texto o también archivos/imágenes?**
- [x] En principio solo texto, con soporte opcional para imagen

**Variables dinámicas:**
- `{{nombre}}` — con fallback si `nombre_contacto` está vacío

**Etiquetas y templates:**
- Definidas por el operador en la hoja `mensajes`
- Múltiples variantes por etiqueta → el bot elige al azar (anti-bot)

---

## 5. Entorno de ejecución

**¿Dónde corre el bot?**
- [x] Local (Windows) — teléfono conectado a WhatsApp Web

**Lenguaje:**
- [x] Node.js — Stack Opción A (whatsapp-web.js + googleapis)

**¿El número de WhatsApp es personal o dedicado?**
- [x] Personal — autenticación por QR

---

## 6. Restricciones y contexto

**¿Riesgo de ban?**
- [x] Aceptable con uso responsable

**Estrategia anti-ban:**
- Delays aleatorios entre mensajes (8–20 segundos)
- Simulación de tipeo humano antes de enviar
- Orden de envío aleatorizado
- Límite de ~50 mensajes por hora
- Variantes de mensajes por etiqueta

**¿Hay algo ya implementado?**
- [x] Sí — intento anterior con comportamiento humano (tipeo simulado, delays random, scrolleo)

**Contexto adicional:**
> Bot para Baba, fábrica de cerveza artesanal (PyME, Buenos Aires).
> Contactos agendados como: nombre = nombre del local, apellido = nombre de la persona.
> El operador define etiquetas y templates en la hoja `mensajes`.
