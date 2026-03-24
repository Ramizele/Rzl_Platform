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

## Regla de orquestacion local

1. `platform/` define reglas, templates, runbooks y scripts.
2. `rzl_database/` concentra conocimiento operativo y assets de sistemas.
3. `rzl_gpt_apps/` traduce el trabajo a superficies ChatGPT (Windows/iOS/Web/Projects/GPTs).
4. `plugins/` integra automatizaciones externas.
5. `core/` mantiene componentes base compartidos.

## Ciclo operativo minimo

1. Cargar/actualizar assets en `rzl_database/`.
2. Generar contexto operativo y packs en `rzl_gpt_apps/`.
3. Ejecutar barrido de coherencia:
   - `python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/reports/local --tag baseline`
4. Revisar edges de orquestacion para detectar rutas rotas o dependencias no deseadas.
