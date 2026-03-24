# Analisis "angels" del repositorio (v0.1)

## Fuente usada para el analisis

- `AGENTS.md` (reglas operativas)
- `platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml` (contrato de ecosistema)
- estructura actual de buckets (`platform/`, `core/`, `rzl_database/`, `rzl_gpt_apps/`, `plugins/`, `rzl_persona/`, `rzl_gdrive/`)

## Estado actual (resumen)

Fortalezas:
- El control plane de `gentle-ai` ya existe y esta integrado.
- El repo esta limpio (template-first, sin data externa pesada).
- Buckets base ya definidos.

Gaps para empezar trabajo real:
- Falta capa de gobierno operacional separada de la capa de arquitectura.
- Falta estructura de ejecucion por iniciativas/sistemas dentro de `rzl_database/`.
- Falta carril de operaciones (`runbooks`, `workbenches`, `checks`) para ciclo continuo.

## Arquitectura propuesta (v1 operativa)

### 1) Governance plane

Objetivo: reglas, contratos y decisiones.

Rutas:
- `platform/governance/agents/`
- `platform/governance/manifests/`
- `platform/governance/rules/`

### 2) Control plane IA

Objetivo: instalar, actualizar y validar ecosistema de agentes.

Ruta:
- `platform/gentle_ai/` (ya existente; mantener como SoT local)

### 3) Operations plane

Objetivo: ejecutar trabajo de forma repetible.

Rutas:
- `platform/ops/runbooks/`
- `platform/ops/workbenches/`
- `platform/ops/checks/`

### 4) Knowledge/Data plane

Objetivo: modelar sistemas y estado operativo.

Rutas:
- `rzl_database/systems/`
- `rzl_database/intake_field/`

Modelo inicial de sistema:
- `02_registry/`
- `03_knowledge/`
- `06_state/`
- `07_ops_local/`
- `08_projections/`
- `09_migration/`

### 5) Delivery plane (surfaces)

Objetivo: traduccion de trabajo a superficies ChatGPT y agentes.

Rutas:
- `rzl_gpt_apps/docs/`
- `rzl_gpt_apps/packs/`

### 6) Integration plane

Objetivo: conectores/automatizaciones externas.

Rutas:
- `plugins/apps/extensiones/`

## Secuencia recomendada para empezar a trabajar

1. Definir una iniciativa en `platform/ops/workbenches/`.
2. Crear sistema objetivo en `rzl_database/systems/`.
3. Ejecutar runbook de bootstrap `gentle-ai`.
4. Operar cambios con SDD skills en el agente elegido.
5. Publicar empaquetado/brief en `rzl_gpt_apps/packs/`.
