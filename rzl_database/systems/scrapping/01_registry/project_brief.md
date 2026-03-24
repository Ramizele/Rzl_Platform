---
system_id: scrapping
status: draft
owner: Rzl_Platform
updated: 2026-03-24
---

# Project Brief - Scrapping

## Objetivo

Construir un scraper modular para Google Maps que extraiga leads de bares/pubs/cervecerias de CABA y genere un CSV util para prospeccion comercial.

## Entradas

- Archivo de queries por barrio: `plugins/apps/extensions/scrapping/queries/cervecerias_por_localidad.txt`

## Salidas

- Dataset principal: `plugins/apps/extensions/scrapping/output/caba_scrapping.csv`
- Registro de dedupe: `plugins/apps/extensions/scrapping/output/duplicados.csv`

## Restricciones operativas

- Selenium + ChromeDriver.
- Maximo 4 workers concurrentes.
- Delays aleatorios para reducir riesgo de bloqueo.
- Arquitectura modular y mantenible.
