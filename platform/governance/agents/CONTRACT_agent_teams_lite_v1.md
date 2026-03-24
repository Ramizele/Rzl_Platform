# Contract - Agent Teams Lite v1

## Objective

Define a minimal agent operating model for execution and validation of Route D.

## Team structure

1. `team_control_plane`
- Scope: `platform/gentle_ai/*`, `.gga`, control-plane runbooks.
- Responsibility: keep manifest, runbooks, and execution policy aligned.

2. `team_architecture_ops`
- Scope: `platform/architecture/*`, `platform/ops/*`, `platform/governance/*`.
- Responsibility: maintain roadmap, gates, checklists, and evidence reports.

3. `team_surface_integration`
- Scope: `rzl_gpt_apps/*`, `plugins/*`, references to Windows/iOS/VSCode workflows.
- Responsibility: keep surface matrix and packs aligned with template orchestration.

## Working agreement

1. No team imports external operational datasets into this repository.
2. Any local adaptation must reference:
- `platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml`
- `platform/architecture/template_architecture_map.md`
- `AGENTS.md`
3. Each phase closure must produce one auditable artifact in `platform/ops/checks/`.

## Cadence

1. Daily 15-minute gate sync.
2. Weekly architecture and control-plane alignment review.
3. Gate owner rotates by phase but remains explicit in the workbench.
