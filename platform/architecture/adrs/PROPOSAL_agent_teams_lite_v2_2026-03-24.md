# Propuesta Arquitectura v2 (Agent Teams Lite)

## Contexto

Analisis consolidado por 3 subagentes (estructura, ecosistema gentle-ai y operating model)
sobre `E:/GITHUB/Plataforma/Rzl_Platform`.

Fuentes base:
- `AGENTS.md`
- `platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml`
- `platform/architecture/template_architecture_map.md`
- `platform/architecture/ANALISIS_angels_repo_v0.1.md`

## Diagnostico sintetico

1. La base por buckets esta bien definida y alineada.
2. El control plane `gentle-ai` esta operativo, pero con drift entre manifiesto y runbook.
3. La capa `ops` y `governance` aun esta en modo scaffold (baja madurez operativa).
4. Hay deuda de naming/estandares documentales y residuos legacy.

## Gaps prioritarios

1. Gobierno documental insuficiente:
   - faltan contratos/rulesets reales en `platform/governance/**`.
2. Drift de implementacion en ecosistema:
   - manifiesto declara 8 componentes y runbook instala subset.
3. Calidad operativa en hooks:
   - estrategia actual advisory (no bloqueante) por robustez de provider.
4. Consistencia de rutas:
   - docs y defaults de reportes deben converger en una sola ruta canonica.

## Arquitectura objetivo v2

```text
Rzl_Platform/
  platform/
    architecture/
      maps/
      adrs/
      roadmaps/
    gentle_ai/
      manifests/
      runbooks/
      presets/
    governance/
      rules/
      contracts/
      manifests/
      standards/
        naming/
        doc_metadata/
    ops/
      runbooks/
      checks/
      workbenches/
      reports/
        sweeps/
        audits/
    schemas/
    tools/
  core/
    templates/
    shared_schemas/
    components/
  rzl_database/
    intake/
    systems/
      _template/
        01_registry/
        02_knowledge/
        03_state/
        04_ops/
        05_projections/
        06_migration/
      <system_id>/
    indexes/
  rzl_gpt_apps/
    docs/
      surfaces/
      standards/
    packs/
      draft/
      released/
  plugins/
    apps/
      extensions/
    connectors/
  rzl_persona/
    profiles/
    policies/
  rzl_gdrive/
    manifests/
    payload_index/
```

## Operating model propuesto (equipo)

Fases y gates:
1. Intake -> `G1 Intake Aprobado`
2. Diseno -> `G2 Diseno Congelado`
3. Implementacion -> `G3 Build Completo`
4. Validacion -> `G4 Validacion OK`
5. Release -> `G5 Release Aprobado`

## Plan de migracion en 5 pasos

1. Congelar baseline `as-is` + inventario de rutas.
2. Acordar estandar de naming (`lower_snake_case`) y metadata minima.
3. Crear estructura v2 en paralelo con punteros de compatibilidad.
4. Migrar governance docs a contratos/rules/manifests versionados.
5. Cerrar drift de ecosistema (manifiesto vs runbook) y activar checks de conformidad.

## Recomendacion para iniciar trabajo ahora

1. Crear primer workbench real en `platform/ops/workbenches/`.
2. Instanciar `rzl_database/systems/<system_id>/` desde `_template`.
3. Ejecutar un ciclo completo G1->G5 con evidencia en `ops/checks` y `rzl_gpt_apps/packs`.
