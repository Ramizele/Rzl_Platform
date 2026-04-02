---
asset_id: algo_i
asset_type: pack
status: draft
version: v0.1
owner: Rzl_Platform
updated: 2026-04-02
surface: claude_projects
---

# Pack: ALGO I

Pack operativo para configurar ALGO I como Claude Project. ALGO I es un agente de estudio especializado en Haskell y Python que usa la metodologia de Jugada de Ajedrez: cada concepto es un movimiento calculado con posicion, calculo, jugada y consecuencia. Se alimenta con libros y material de estudio via protocolo de ingesta.

## Alcance

- Definir el rol, metodologia y comportamiento del agente de estudio.
- Proveer el system prompt listo para pegar en Claude Projects.
- Documentar el protocolo de ingesta de libros y material de estudio.

## Activos del pack

1. `01_intake.md`: brief funcional — scope, lenguajes, libros, nivel, estilo.
2. `02_agent_system_prompt.md`: prompt listo para pegar en Claude Projects.
3. `03_knowledge_protocol.md`: protocolo para alimentar el agente con libros y contenido.

## Referencias cruzadas

- Workspace del proyecto: `algo_i/`
- Registro de sistema: `rzl_database/systems/algo_i/01_registry/project_brief.md`
- Curriculo base: `algo_i/docs/curriculum_map.md`

## Estado

Draft. Listo para uso inmediato. El curriculo y el protocolo de ingesta se expanden a medida que avanza el estudio.
