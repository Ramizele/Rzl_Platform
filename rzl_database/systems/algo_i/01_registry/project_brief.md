---
system_id: algo_i
status: draft
owner: Rzl_Platform
updated: 2026-04-02
---

# ALGO I — Project Brief

## Objetivo

Construir un agente de estudio profundo en Haskell y Python que funcione como tutor interactivo en Claude Projects. El agente acompana el aprendizaje algoritmico usando la metodologia de Jugada de Ajedrez: cada concepto es un movimiento calculado con contexto, exploracion, insight y consecuencia.

## Entradas

- Fragmentos de libros y material de estudio pegados por el usuario (modo INGESTA)
- Preguntas y solicitudes de explicacion (modo ESTUDIO)
- Intentos de ejercicios del usuario (modo PRACTICA)
- Solicitudes de repaso (modo REVISION)

## Salidas

- Explicaciones estructuradas siguiendo el formato Movimiento de Ajedrez
- Ejercicios graduados al nivel actual del estudiante
- Notas de conocimiento para guardar en `algo_i/assets/`
- Codigo ejecutable en Python y Haskell con explicacion linea a linea

## Stack

- Surface: Claude.ai Projects
- Configuracion: system prompt en `rzl_gpt_apps/packs/draft/algo_i/02_agent_system_prompt.md`
- Sin dependencias de infraestructura — es un pack de instrucciones para Claude

## Restricciones operativas

- El agente no revela soluciones sin que el estudiante intente primero (modo PRACTICA)
- Todo codigo debe ser ejecutable y correcto
- Se explica cada patron nuevo la primera vez que aparece
- Soporta Haskell y Python de forma paralela para cada concepto

## Curriculo base

Ver `algo_i/docs/curriculum_map.md`:
- Apertura: fundamentos (tipos, funciones, recursion, HOF)
- Medio juego: estructuras de datos y algoritmos clasicos
- Final: algoritmos avanzados, monads, concurrencia
