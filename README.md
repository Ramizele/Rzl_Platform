# Rzl_Platform

Template base para operar con:
- arquitectura por buckets,
- buckets,
- assets,
- orquestacion entre buckets por referencias cruzadas.

## Estructura local inicial

- `platform/` -> herramientas, arquitectura y reportes
- `core/` -> base compartida
- `rzl_database/` -> conocimiento operativo principal
- `rzl_persona/` -> contexto personal
- `rzl_gpt_apps/` -> superficies ChatGPT (Windows/iOS/VSCode)
- `plugins/` -> integraciones
- `rzl_gdrive/` -> payload pesado

Mapa de template:
- `platform/architecture/template_architecture_map.md`

## Uso rapido

1. Ejecutar barrido sobre este repo local:

```powershell
python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/reports/local --tag baseline
```

2. Revisar reportes generados:
- `platform/reports/*/REPORT_bucket_asset_orchestration_*_latest.md`
- `platform/reports/*/SNAPSHOT_bucket_asset_orchestration_*_latest.json`
