# Convention - Project Workspace v1

## Objetivo

Definir el modelo de dos capas para organizar proyectos dentro de Rzl_Platform:
separar la información de la plataforma sobre el proyecto de la información propia del proyecto.

## Modelo de dos capas

### Capa 1: Plataforma (sobre el proyecto)

Gestionada por los buckets de infraestructura. Contiene lo que la plataforma sabe y expone del proyecto.

| Bucket | Ruta | Contenido |
|--------|------|-----------|
| `rzl_database` | `rzl_database/systems/{name}/` | Registry, metadata, owners, knowledge base, estado operativo |
| `rzl_gpt_apps` | `rzl_gpt_apps/packs/draft/{name}/` | Packs ChatGPT, system prompts, runbooks de superficie |
| `plugins` | `plugins/apps/extensions/{name}/` | Automatizaciones y conectores externos del proyecto |

### Capa 2: Proyecto (trabajo propio)

Cada proyecto tiene su propia carpeta en la **raíz del repo**, como un bucket más junto a `platform/`, `rzl_database/`, etc.

| Carpeta | Contenido |
|---------|-----------|
| `{name}/docs/` | Brief, decisiones técnicas, contexto, ADRs del proyecto |
| `{name}/src/` | Código fuente / implementación |
| `{name}/worklog/` | Bitácora de sesiones, avances, notas de trabajo diario |
| `{name}/assets/` | Datos, configs, outputs, artefactos propios del proyecto |
| `{name}/README.md` | Descripción y estado actual del proyecto |

```
Rzl_Platform/
├── platform/           ← control plane
├── rzl_database/       ← metadata de sistemas
├── rzl_gpt_apps/       ← packs ChatGPT
├── plugins/            ← integraciones
├── whatsapp_bot/       ← workspace del proyecto (raíz)
└── {nombre_proyecto}/  ← próximo proyecto
```

## Proceso de creación de nuevo proyecto

### Checklist

- [ ] 1. Crear carpeta del proyecto en la raíz: `{nombre}/` usando `projects/_template/` como referencia
- [ ] 2. Completar `{nombre}/README.md` con descripción y estado
- [ ] 3. Crear entry de plataforma: copiar `rzl_database/systems/_template/` → `rzl_database/systems/{nombre}/`
- [ ] 4. Completar `rzl_database/systems/{nombre}/01_registry/` con metadata del proyecto
- [ ] 5. (Opcional) Crear pack ChatGPT: `rzl_gpt_apps/packs/draft/{nombre}/` si tiene superficie
- [ ] 6. (Opcional) Crear integración: `plugins/apps/extensions/{nombre}/` si tiene automatización
- [ ] 7. Registrar en engram: `mem_save` con título del proyecto, tipo `decision`, topic_key `projects/{nombre}/init`

### Regla de nomenclatura

- Usar `snake_case` para nombres de carpeta
- El nombre debe ser consistente en todos los buckets donde aparezca

## Regla de separación

> Lo que pertenece al proyecto va en `{nombre}/` (raíz del repo).
> Lo que la plataforma necesita saber del proyecto va en `rzl_database/systems/{nombre}/`.
> No mezclar documentación de governance con documentación de trabajo del proyecto.

## Template de referencia

Ver estructura base en: `projects/_template/`
(Copiar manualmente a la raíz con el nombre del proyecto)

## Referencia de arquitectura

Ver: `platform/architecture/maps/template_architecture_map.md`
