---
asset_id: scrapping
asset_type: pack
status: draft
version: v0.1
owner: Rzl_Platform
updated: 2026-03-24
surface: chatgpt_projects
---

# Pack: Scrapping

Pack operativo para levantar el proyecto `scrapping` orientado a prospeccion comercial de bares en CABA desde Google Maps.

## Alcance

- Definir contexto funcional y tecnico del proyecto.
- Usar un system prompt listo para ChatGPT Projects.
- Mantener el codigo modular en `plugins/apps/extensions/scrapping/`.

## Activos del pack

1. `01_intake.md`: brief funcional del proyecto.
2. `02_agent_system_prompt.md`: prompt listo para pegar en ChatGPT Projects.
3. `03_runbook_local.md`: forma de ejecutar el scraper localmente.

## Referencias cruzadas

- Codigo scraper: `plugins/apps/extensions/scrapping/`
- Registro de sistema: `rzl_database/systems/scrapping/01_registry/project_brief.md`

## Estado

Draft. Preparado para iterar selectores, calidad de datos y performance.
