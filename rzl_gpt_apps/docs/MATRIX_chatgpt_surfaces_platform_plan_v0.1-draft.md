---
asset_id: "matrix_chatgpt_surfaces_platform_plan_rzl"
asset_type: "matrix"
status: "draft"
version: "v0.1-draft"
owner: "Rzl_Platform"
updated: "2026-03-24"
---

# MATRIX - ChatGPT surfaces x platform x use case

## Objetivo

Definir que superficie usar segun plataforma y tipo de trabajo, para mantener coherencia entre:
- ChatGPT app en Windows,
- ChatGPT app en iOS,
- VSCode en Windows,
- Codex + modelos GPT.

## Matriz operativa inicial

| surface_id | Surface | Windows app | iOS app | VSCode (Windows) | Uso recomendado |
| --- | --- | --- | --- | --- | --- |
| `chat_sessions` | Chats normales | yes | yes | indirecto | investigacion y decisiones rapidas |
| `projects` | Projects | verify_in_product | verify_in_product | indirecto | trabajo por sprint con contexto largo |
| `custom_gpt` | Custom GPT | verify_in_product | verify_in_product | indirecto | asistentes especializados por dominio |
| `codex_local` | Codex en repo local | yes | no | yes | cambios de codigo, scripts y validaciones |
| `openai_api` | API OpenAI | yes | yes | yes | automatizaciones y orquestacion programatica |

## Capa de ecosistema (coding agents)

- Fuente de jerarquia maxima: `https://github.com/Gentleman-Programming/gentle-ai`
- Control plane local:
  - `platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml`
  - `platform/gentle_ai/runbooks/WINDOWS_bootstrap_gentle_ai.ps1`

## Regla de sincronizacion

1. Disenar el flujo en `platform/` y documentar dependencias.
2. Ejecutar cambios en repo local con Codex/VSCode.
3. Publicar contexto operativo sintetizado en la superficie ChatGPT correspondiente.
4. Aplicar o actualizar ecosistema de agentes con `gentle-ai` (preset recomendado: `ecosystem-only`).
5. Revalidar relaciones entre buckets con:
   - `python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/reports/local --tag baseline`
