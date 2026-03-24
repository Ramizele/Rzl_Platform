# Template Architecture Map

## Objetivo

Usar una referencia externa solo como fuente de estructura para arrancar la plataforma local con el mismo enfoque:
- buckets claros por dominio,
- inventario de assets por bucket,
- orquestacion entre buckets basada en referencias de rutas.

## Mapeo de referencia a implementacion local

| Referencia AingZ | Implementacion local |
| --- | --- |
| `platform/` | `platform/` |
| `core/` | `core/` |
| `aingz_database/` | `rzl_database/` |
| `aingz_persona/` | `rzl_persona/` |
| `aingz_gpt_apps/` | `rzl_gpt_apps/` |
| `aingz_gdrive/` | `rzl_gdrive/` |
| `plugins/` | `plugins/` |

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
