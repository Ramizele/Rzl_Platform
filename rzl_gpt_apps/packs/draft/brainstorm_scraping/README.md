---
asset_id: brainstorm_scraping
asset_type: pack
status: draft
version: v0.1
owner: Rzl_Platform
updated: 2026-03-24
surface: chatgpt_projects
---

# Pack: Brainstorm — Nuevo Proyecto de Scraping

Pack para diseñar un nuevo proyecto de scraping desde una idea semilla y generar las instrucciones listas para pegar en un ChatGPT Project dedicado.

## Cómo usar

**Paso 1 — Completar el intake**
Abrí `01_intake.md` y respondé todas las preguntas. Cuanto más completo, mejor el prompt generado.

**Paso 2 — Armar el system prompt**
Abrí `02_agent_system_prompt.md`, reemplazá cada `[PLACEHOLDER]` con la info del intake.

**Paso 3 — Pegar en ChatGPT Projects**
Copiá el bloque marcado en `02_agent_system_prompt.md` y pegalo como instrucciones del nuevo proyecto en la app de ChatGPT (Windows o iOS).

## Output

Al finalizar los 3 pasos tenés:
- Un agente dedicado a tu proyecto de scraping, con contexto completo
- Un brief técnico del proyecto registrado localmente

## Plataforma (próximos pasos opcionales)

- Instanciar `rzl_database/systems/<project_id>/01_registry/` desde `_template` para registrar el sistema
- Mover a `packs/released/` cuando el proyecto esté activo
- Ejecutar sweep de coherencia: `python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/ops/reports/sweeps --tag scraping`
