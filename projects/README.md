# projects/

Bucket dedicado al trabajo propio de cada proyecto.

## Propósito

Separar la información del proyecto de la infraestructura de plataforma.

| Capa | Dónde vive | Qué contiene |
|------|-----------|--------------|
| **Plataforma** (sobre el proyecto) | `rzl_database/systems/{name}/` | Registry, metadata, contratos, knowledge base |
| **Plataforma** (superficie) | `rzl_gpt_apps/packs/draft/{name}/` | Packs para ChatGPT, system prompts, runbooks |
| **Plataforma** (integración) | `plugins/apps/extensions/{name}/` | Automatizaciones y conectores externos |
| **Proyecto** (trabajo propio) | `{name}/` (raíz del repo) | Código, docs, bitácora, assets del proyecto |

## Convención de creación

Al iniciar un nuevo proyecto:

1. Copiar `projects/_template/` → `{nombre-proyecto}/` (raíz del repo, junto a `platform/`, `rzl_database/`, etc.)
2. Completar `{nombre-proyecto}/README.md` con el brief
3. Crear las entradas correspondientes en los buckets de plataforma:
   - `rzl_database/systems/{nombre-proyecto}/` (desde `rzl_database/systems/_template/`)
   - `rzl_gpt_apps/packs/draft/{nombre-proyecto}/` si hay superficie ChatGPT

Ver convención completa en:
`platform/governance/standards/CONVENTION_project_workspace_v1.md`

## Estructura interna por proyecto

```
{nombre}/               ← en la raíz del repo
├── docs/       ← brief, decisiones, contexto técnico, ADRs del proyecto
├── src/        ← código fuente / implementación
├── worklog/    ← bitácora de sesiones, avances, notas de trabajo
├── assets/     ← datos, configs, outputs, artefactos propios
└── README.md   ← descripción del proyecto y estado actual
```
