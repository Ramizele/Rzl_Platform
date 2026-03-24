# Report - Route D Gate Status

- generated_at: `2026-03-24 15:05:38`
- repo_root: `E:\GITHUB\Plataforma\Rzl_Platform`

## Gate summary
| Gate | Status | Checks |
| --- | --- | ---: |
| G1 | PASS | 8 |
| G2 | PASS | 4 |
| G3 | PASS | 3 |
| G4 | PASS | 6 |
| G5 | PASS | 1 |

## Detailed checks
| Gate | Check | Status | Evidence |
| --- | --- | --- | --- |
| G1 | bucket 'platform' exists | PASS | ok |
| G1 | bucket 'core' exists | PASS | ok |
| G1 | bucket 'rzl_database' exists | PASS | ok |
| G1 | bucket 'rzl_persona' exists | PASS | ok |
| G1 | bucket 'rzl_gpt_apps' exists | PASS | ok |
| G1 | bucket 'plugins' exists | PASS | ok |
| G1 | bucket 'rzl_gdrive' exists | PASS | ok |
| G1 | manifest present | PASS | platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml |
| G2 | artifact 'platform/architecture/ROADMAP_route_d_staged_execution_v1.md' present | PASS | ok |
| G2 | artifact 'platform/governance/rules/RULESET_route_d_phase_gates_v1.md' present | PASS | ok |
| G2 | artifact 'platform/governance/agents/CONTRACT_agent_teams_lite_v1.md' present | PASS | ok |
| G2 | artifact 'platform/ops/checks/CHECKLIST_route_d_gate_validation_v1.md' present | PASS | ok |
| G3 | artifact 'platform/gentle_ai/runbooks/WINDOWS_bootstrap_gentle_ai.ps1' present | PASS | ok |
| G3 | artifact 'platform/gentle_ai/runbooks/WINDOWS_verify_gentle_ai_stack.ps1' present | PASS | ok |
| G3 | artifact '.gga' present | PASS | ok |
| G4 | gentle-ai command available | PASS | C:\Users\rami\AppData\Local\gentle-ai\bin\gentle-ai.exe |
| G4 | engram command available | PASS | C:\Users\rami\go\bin\engram.exe |
| G4 | engram stats command | PASS | Engram Memory Stats |
| G4 | gga via Git Bash | PASS | gga v2.8.0  |
| G4 | gga config on repo | PASS | ok |
| G4 | bucket sweep command | PASS | Sweep complete: files=61 buckets=8 edges=15 report=E:/GITHUB/Plataforma/Rzl_Platform/platform/reports/local/REPORT_bucket_asset_orchestration_route_d_g4_latest.md |
| G5 | artifact 'platform/ops/workbenches/WB_route_d_execution_2026-03-24.md' present | PASS | ok |


