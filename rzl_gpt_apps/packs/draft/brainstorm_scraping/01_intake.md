# Intake — Nuevo Proyecto de Scraping

Respondé las preguntas. Este documento alimenta directamente el system prompt del agente.
Dejá en blanco lo que no sabés — el agente te ayuda a definirlo.

---

## 1. Concepto

**¿Qué querés scrapear?** (sitio web, API, servicio — URL o descripción)
>

**¿Por qué? ¿Qué problema resuelve o qué uso le vas a dar a los datos?**
>

**¿Cuál es el output final?** (dataset para análisis, feed en tiempo real, alimentar una app, etc.)
>

**Nombre del proyecto** (snake_case, corto — ej: `precio_dolar`, `inmuebles_ba`, `jobs_feed`):
>

---

## 2. Target / Fuente de datos

**URL(s) objetivo:**
>

**Tipo de fuente:**
- [ ] Sitio web estático (HTML puro)
- [ ] Sitio web con JavaScript / SPA (React, Angular, Vue)
- [ ] API REST con endpoints documentados
- [ ] API no documentada / reverse-engineered
- [ ] Combinación

**¿Requiere login o autenticación?**
- [ ] No
- [ ] Sí — tipo: `[ ] usuario/contraseña` `[ ] API key` `[ ] OAuth` `[ ] otro: ___`

**¿Tiene protecciones anti-scraping conocidas?**
- [ ] No / no sé
- [ ] Cloudflare
- [ ] Rate limiting (errores 429)
- [ ] CAPTCHA
- [ ] Bloqueo por IP
- [ ] Fingerprinting de browser
- [ ] Otro: ___

**¿Tiene paginación o scroll infinito?**
- [ ] No (todo en una página)
- [ ] Paginación con parámetros URL (`?page=2`, `?offset=50`)
- [ ] Scroll infinito / lazy load
- [ ] "Load more" button
- [ ] No sé todavía

---

## 3. Datos a extraer

**Listá todos los campos que querés capturar** (nombre + descripción breve):
- `campo_1`:
- `campo_2`:
- `campo_3`:
- _(agregá los que necesites)_

**¿Necesitás datos anidados o relaciones?** (ej: cada producto tiene múltiples reviews)
>

**¿Hay datos que son difíciles de extraer?** (imágenes, PDFs, datos calculados, etc.)
>

---

## 4. Output y almacenamiento

**Formato de salida:**
- [ ] JSON (archivos)
- [ ] CSV
- [ ] Base de datos — `[ ] PostgreSQL` `[ ] SQLite` `[ ] MongoDB` `[ ] otro: ___`
- [ ] API / webhook (el scraper pushea a un endpoint)
- [ ] No definido todavía

**¿Necesitás deduplicación?** (evitar guardar registros repetidos)
- [ ] No / no sé
- [ ] Sí — campo(s) clave para identificar unicidad: ___

---

## 5. Escala y frecuencia

**Volumen estimado:**
- [ ] Pocos registros (< 1.000)
- [ ] Medio (1.000 – 100.000)
- [ ] Grande (> 100.000)
- [ ] No sé

**Frecuencia de ejecución:**
- [ ] Una sola vez (one-shot)
- [ ] Periódico — cada: `[ ] hora` `[ ] día` `[ ] semana` `[ ] mes`
- [ ] Continuo / near real-time
- [ ] No definido

---

## 6. Stack técnico

**Lenguaje preferido:**
- [ ] Python
- [ ] Node.js / TypeScript
- [ ] Sin preferencia

**Librería/framework preferido:**
- [ ] `requests` + `BeautifulSoup` (simple, estático)
- [ ] `Scrapy` (robusto, escalable)
- [ ] `Playwright` (JavaScript, headless browser)
- [ ] `Puppeteer` (Node.js, headless browser)
- [ ] `Selenium` (legacy, headless browser)
- [ ] Sin preferencia — elegí el más adecuado

**¿Dónde va a correr el scraper?**
- [ ] Local (mi máquina)
- [ ] Cloud — `[ ] AWS` `[ ] GCP` `[ ] Azure` `[ ] Railway` `[ ] otro: ___`
- [ ] VPS / servidor propio
- [ ] Sin definir

---

## 7. Restricciones y contexto

**¿Revisaste robots.txt y Terms of Service del sitio?**
- [ ] Sí, no hay restricciones relevantes
- [ ] Sí, hay restricciones: ___
- [ ] No todavía

**¿Tenés código existente de referencia o un prototipo?**
- [ ] No
- [ ] Sí — dónde / qué hace: ___

**¿Algo no negociable en la implementación?** (performance, anonimato, costo, etc.)
>

**Contexto adicional que el agente debe saber:**
>
