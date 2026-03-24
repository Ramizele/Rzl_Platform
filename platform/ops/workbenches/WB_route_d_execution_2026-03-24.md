# Workbench - Route D Execution (2026-03-24)

## Goal

Run the staged strategy `A -> B -> C` with validation gates and leave the repository ready for commit/sync.

## Phase tracker

| Phase | Goal | Gate | Status | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Baseline + cleanup in template mode | `G1` | done | sweep report under `platform/reports/local` |
| 2 | Agent Teams Lite governance | `G2` | done | ruleset + team contract + roadmap |
| 3 | Build operational stack | `G3` | done | bootstrap + verification runbooks |
| 4 | Validate stack and architecture checks | `G4` | done | gate validation report |
| 5 | Release readiness | `G5` | done | `REPORT_route_d_gate_status_latest.md` |

## Decisions

1. Keep `gentle-ai` as source of highest hierarchy.
2. Keep repository in template mode only.
3. Validate `gga` through Git Bash on Windows when not present in PowerShell PATH.

## Migration v2 (2026-03-24)

Estructura migrada de v1 a v2 según `platform/architecture/adrs/PROPOSAL_agent_teams_lite_v2_2026-03-24.md`.

| Cambio | Origen | Destino |
| --- | --- | --- |
| Archivos de arquitectura | `platform/architecture/*.md` | `maps/`, `adrs/`, `roadmaps/` |
| Manifest gentle-ai | `platform/gentle_ai/` | `platform/gentle_ai/manifests/` |
| Contrato de agentes | `platform/governance/agents/` | `platform/governance/contracts/` |
| Reportes de barrido | `platform/reports/local/` | `platform/ops/reports/sweeps/` |
| Schema JSON | `platform/config/` | `platform/schemas/` |
| intake_field | `rzl_database/intake_field/` | `rzl_database/intake/` |
| Sys_Template | `rzl_database/systems/Sys_Template/` | `rzl_database/systems/_template/` |
| Subdirs numerados | `02_registry … 09_migration` | `01_registry … 06_migration` |
| MATRIX doc | `rzl_gpt_apps/docs/` | `rzl_gpt_apps/docs/surfaces/` |
| extensiones | `plugins/apps/extensiones/` | `plugins/apps/extensions/` |
| Nuevos directorios vacíos | — | `core/`, `rzl_database/indexes/`, `rzl_persona/profiles/`, `rzl_persona/policies/`, `rzl_gdrive/manifests/`, `rzl_gdrive/payload_index/`, `plugins/connectors/`, `rzl_gpt_apps/packs/draft/released/`, `platform/governance/standards/`, `platform/gentle_ai/presets/`, `platform/ops/reports/audits/`, `platform/schemas/` |

## Risks

1. `gga` may be unavailable in PowerShell PATH while still functional in Git Bash.
2. Drift risk if manifest components and bootstrap runbook diverge again.

## Mitigations

1. Use `WINDOWS_validate_route_d_gates.ps1` before merges.
2. Treat gate report as mandatory release artifact.
