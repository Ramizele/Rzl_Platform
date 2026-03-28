# Template Architecture Map

## Objetivo

Usar `gentle-ai` como fuente de maxima jerarquia del ecosistema de agentes y mantener esta arquitectura local por buckets:
- buckets claros por dominio,
- inventario de assets por bucket,
- orquestacion entre buckets basada en referencias de rutas.

## Fuente jerarquica

- Upstream: `https://github.com/Gentleman-Programming/gentle-ai`
- Capa local: `platform/gentle_ai/`

## Buckets locales canonicos

- `platform/`
- `core/`
- `rzl_database/`
- `rzl_persona/`
- `rzl_gpt_apps/`
- `plugins/`
- `rzl_gdrive/`
- `{nombre_proyecto}/` — cada proyecto vive como bucket raíz (ej: `whatsapp_bot/`)

## Regla de orquestacion local

1. `platform/` define reglas, templates, runbooks y scripts.
2. `rzl_database/` concentra conocimiento operativo y assets de sistemas.
3. `rzl_gpt_apps/` traduce el trabajo a superficies ChatGPT (Windows/iOS/Web/Projects/GPTs).
4. `plugins/` integra automatizaciones externas.
5. `core/` mantiene componentes base compartidos.
6. Cada proyecto vive como carpeta raíz junto a los buckets de plataforma (ej: `whatsapp_bot/`). Contiene el trabajo propio del proyecto (código, docs, worklog, assets) separado de la infraestructura.

## Modelo de dos capas por proyecto

Cada proyecto tiene presencia en dos capas:

| Capa | Bucket | Contenido |
|------|--------|-----------|
| Plataforma | `rzl_database/systems/{name}/` | Registry, metadata, knowledge base |
| Plataforma | `rzl_gpt_apps/packs/draft/{name}/` | Packs y superficies ChatGPT |
| Proyecto | `{name}/` (raíz del repo) | Código, docs, worklog, assets del proyecto |

Ver convención completa: `platform/governance/standards/CONVENTION_project_workspace_v1.md`

## Ciclo operativo minimo

1. Cargar/actualizar assets en `rzl_database/`.
2. Generar contexto operativo y packs en `rzl_gpt_apps/`.
3. Ejecutar barrido de coherencia:
   - `python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/reports/local --tag baseline`
4. Revisar edges de orquestacion para detectar rutas rotas o dependencias no deseadas.
