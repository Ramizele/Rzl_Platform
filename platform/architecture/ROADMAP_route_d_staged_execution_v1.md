# Roadmap Route D - Staged Execution v1

## Scope

Execute the staged path `A -> B -> C` in template mode, with validation gates between phases.

- Phase 1: Template Baseline and Cleanup
- Phase 2: Agent Teams Lite Operating Model
- Phase 3: Multi-Client Integration (Windows ChatGPT, iOS ChatGPT, VSCode)
- Phase 4: Technical Validation
- Phase 5: Release Readiness

## Gate Model

| Gate | Exit condition |
| --- | --- |
| `G1` | Baseline template is clean, aligned with `gentle-ai`, and sweep evidence exists |
| `G2` | Team contracts and governance rules for agent operations are approved |
| `G3` | Runbooks and operating artifacts are implemented and executable |
| `G4` | Validation checks pass (`gentle-ai`, `engram`, `gga`, architecture sweep) |
| `G5` | Release package is ready for commit/sync |

## Deliverables by phase

1. Phase 1
- Local architecture map aligned to canonical buckets.
- Cleanup policy enforced (template-only mode).
- Baseline sweep generated from `platform/tools/bucket_asset_orchestration_sweep.py`.

2. Phase 2
- Agent team contracts documented.
- Gate criteria codified in governance rules.
- Workbench with responsibilities and cadence.

3. Phase 3
- Bootstrap and verification runbooks aligned with manifest components.
- Cross-surface operating matrix linked to orchestration model.
- Local checks/runbooks for daily operation.

4. Phase 4
- Automated gate validation report generated.
- Any gate failure translated into explicit remediation tasks.

5. Phase 5
- Final gate report attached.
- Repo ready for commit and sync.

## Execution command

```powershell
powershell -ExecutionPolicy Bypass -File platform/ops/checks/WINDOWS_validate_route_d_gates.ps1
```
