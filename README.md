# Rzl_Platform

Template base para operar con:
- arquitectura por buckets,
- buckets,
- assets,
- orquestacion entre buckets por referencias cruzadas.

## Fuente de maxima jerarquia

Repositorio canonico de referencia para ecosistema AI:
- `https://github.com/Gentleman-Programming/gentle-ai`

Contrato local de aplicacion:
- `platform/gentle_ai/README.md`
- `platform/gentle_ai/manifests/MANIFEST_gentle_ai_template_v0.1.yaml`

## Estructura local inicial

- `platform/` -> herramientas, arquitectura y reportes
- `core/` -> base compartida
- `rzl_database/` -> conocimiento operativo principal
- `rzl_persona/` -> contexto personal
- `rzl_gpt_apps/` -> superficies ChatGPT (Windows/iOS/VSCode)
- `plugins/` -> integraciones
- `rzl_gdrive/` -> payload pesado

Mapa de template:
- `platform/architecture/maps/template_architecture_map.md`
- `platform/architecture/maps/ANALISIS_angels_repo_v0.1.md`
- `platform/architecture/adrs/PROPOSAL_agent_teams_lite_v2_2026-03-24.md`
- `platform/architecture/roadmaps/ROADMAP_route_d_staged_execution_v1.md`

## Uso rapido

1. Ejecutar barrido sobre este repo local:

```powershell
python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/ops/reports/sweeps --tag baseline
```

2. Revisar reportes generados:
- `platform/ops/reports/sweeps/REPORT_bucket_asset_orchestration_*_latest.md`
- `platform/ops/reports/sweeps/SNAPSHOT_bucket_asset_orchestration_*_latest.json`

## Arquitectura operativa v1 (inicio)

- `platform/governance/` -> reglas, manifiestos y contratos
- `platform/ops/` -> runbooks, workbenches y checks
- `rzl_database/systems/_template/` -> template base de sistema
- `rzl_gpt_apps/packs/` -> empaquetado para superficies/agentes
- `plugins/apps/extensions/` -> integraciones por caso de uso

## Bootstrap Gentle AI (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File platform/gentle_ai/runbooks/WINDOWS_bootstrap_gentle_ai.ps1 -Agents "claude-code,vscode-copilot" -DryRun
```

Aplicar real:

```powershell
powershell -ExecutionPolicy Bypass -File platform/gentle_ai/runbooks/WINDOWS_bootstrap_gentle_ai.ps1 -Agents "claude-code,vscode-copilot" -Apply -EnableGga
```

Verificar stack:

```powershell
powershell -ExecutionPolicy Bypass -File platform/gentle_ai/runbooks/WINDOWS_verify_gentle_ai_stack.ps1
```
