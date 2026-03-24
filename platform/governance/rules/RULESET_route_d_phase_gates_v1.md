# Ruleset - Route D Phase Gates v1

## Purpose

Standardize the staged execution of the platform in template mode, with explicit pass/fail gates.

## Policy

1. `gentle-ai` remains the highest hierarchy source for ecosystem contracts.
2. This repository must stay in `template_only` mode (no imported operational payload).
3. A phase cannot be marked complete until its gate is `PASS`.
4. Gate evidence must be written under `platform/ops/checks/`.

## Gates and minimum criteria

### G1 - Baseline Approved

- Canonical buckets exist: `platform`, `core`, `rzl_database`, `rzl_persona`, `rzl_gpt_apps`, `plugins`, `rzl_gdrive`.
- `platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml` exists and is readable.
- Baseline sweep report exists from local repo scan.

### G2 - Design Frozen

- Agent team contract exists and references responsibilities.
- Route D roadmap exists and maps phases to gates.
- Gate checklist exists for team review.

### G3 - Build Complete

- Windows bootstrap runbook is aligned with manifest components.
- Windows stack verification runbook exists.
- `.gga` project policy is present.

### G4 - Validation OK

- `gentle-ai` command is available.
- `engram` command is available and returns stats.
- `gga` command is reachable via Git Bash and returns version/config.
- Bucket/asset/orchestration sweep executes successfully.

### G5 - Release Approved

- Gate report indicates all gates in `PASS`.
- Workbench status is updated with decisions and blockers.
- Repo is ready for commit/sync by the maintainers.
