# Gentle AI Control Plane (Template)

Este directorio aplica el ecosistema `gentle-ai` sobre este repositorio usando modo template (sin copiar data de otros repos).

## Jerarquia de decision

1. `gentle-ai` upstream (`main`) como fuente de maxima jerarquia para componentes, presets y contratos de agentes.
2. Este repo define solo adaptaciones locales (rutas, buckets, runbooks de ejecucion).
3. Si hay conflicto, prevalece upstream y se ajusta la capa local.

## Alcance local

- Estandarizar setup de agentes (`claude-code`, `vscode-copilot`, `opencode`, `gemini-cli`, `cursor`).
- Activar componentes del ecosistema (`engram`, `sdd`, `skills`, `context7`, `persona`, `permissions`, `gga`, `theme`).
- Mantener scripts de aplicacion reproducibles en Windows.

## Artefactos

- `MANIFEST_gentle_ai_template_v0.1.yaml`: contrato operativo local.
- `runbooks/WINDOWS_bootstrap_gentle_ai.ps1`: bootstrap y aplicacion del preset.
- `runbooks/GIT_BASH_enable_gga.sh`: activacion de GGA por proyecto.
- `.gga`: politica de ejecucion de GGA para este repositorio.

## Nota Windows + Codex (GGA)

En este entorno, `gga` con provider `codex` puede devolver respuesta valida pero sin el formato
estricto esperado por `STRICT_MODE=true`. Por eso este repo usa:
- `PROVIDER="codex"`
- `STRICT_MODE="false"`

Resultado: el hook no bloquea por parseo ambiguo, pero sigue mostrando findings para revision.
