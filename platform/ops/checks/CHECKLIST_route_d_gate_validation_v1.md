# Checklist - Route D Gate Validation v1

## Pre-check

1. Open repository root in terminal.
2. Confirm `AGENTS.md` and `.gga` exist.
3. Confirm Git Bash exists at `C:\Program Files\Git\bin\bash.exe`.

## Gate validation commands

1. Stack baseline:

```powershell
gentle-ai --version
engram stats
```

2. GGA via Git Bash:

```powershell
& "C:\Program Files\Git\bin\bash.exe" -lc "cd '/e/GITHUB/Plataforma/Rzl_Platform' && gga version && gga config"
```

3. Architecture sweep:

```powershell
python platform/tools/bucket_asset_orchestration_sweep.py --root . --output-dir platform/reports/local --tag route_d_gate_check
```

4. Full gate validator:

```powershell
powershell -ExecutionPolicy Bypass -File platform/ops/checks/WINDOWS_validate_route_d_gates.ps1
```

## Exit criteria

1. Report `platform/ops/checks/REPORT_route_d_gate_status_latest.md` exists.
2. All gates in report summary are `PASS`.
3. Workbench status is updated before commit/sync.
