# Intake - Proyecto Scrapping

## 1. Concepto

- Que queremos scrapear:
  Google Maps (resultados de bares, pubs y cervecerias de CABA).
- Para que:
  Dataset de prospeccion para identificar potenciales canales de venta de cerveza artesanal.
- Output final:
  CSV incremental para analisis comercial.
- Nombre del proyecto:
  `scrapping`

## 2. Target / fuente de datos

- URL objetivo:
  `https://www.google.com/maps/search/`
- Tipo de fuente:
  SPA con JavaScript pesado.
- Requiere login:
  No.
- Anti-scraping observado:
  Fingerprinting de browser, cambios frecuentes de selectores, rate limiting implicito.
- Navegacion:
  Feed con scroll infinito.

## 3. Datos a extraer

Campos base:
- `Nombre`
- `Direccion`
- `Barrio`
- `Telefono`
- `Instagram_o_Web`
- `Estrellas`
- `Comentarios`
- `Estado`
- `Link Maps`
- `Query`

## 4. Output y almacenamiento

- Formato: CSV.
- Dedupe: si, por nombre + direccion normalizados.
- Archivos locales:
  - `output/caba_scrapping.csv`
  - `output/duplicados.csv`

## 5. Escala y frecuencia

- Volumen esperado: medio (miles de lugares).
- Frecuencia: one-shot por barrio, con posibilidad de re-ejecucion.

## 6. Stack tecnico

- Lenguaje: Python.
- Framework scraping: Selenium + ChromeDriver.
- Ejecucion: local en Windows.

## 7. Restricciones

- Mantener maximo 4 workers paralelos para reducir bloqueos.
- Aplicar delays aleatorios y headers realistas.
- No mover el repo fuera de modo template.
