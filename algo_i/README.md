# ALGO I

Agente de estudio especializado en Haskell y Python orientado al pensamiento algoritmico. Trabaja en Claude Projects mediante un pack de system prompt. Cada sesion de estudio avanza como una partida de ajedrez: concepto por concepto, movimiento por movimiento.

## Estado

draft

## Descripcion

ALGO I es un agente de estudio que acompana el aprendizaje de:

- **Python**: fundamentos funcionales, algoritmos, estructuras de datos
- **Haskell**: tipos algebraicos, programacion funcional pura, pattern matching, monads

Metodologia: **Jugada de Ajedrez** — cada concepto es un movimiento calculado con posicion, exploracion, insight y consecuencia. El agente se alimenta con libros y material de estudio via protocolo de ingesta estructurado.

## Contexto de plataforma

- Registry: `rzl_database/systems/algo_i/`
- Pack: `rzl_gpt_apps/packs/draft/algo_i/`
- Surface: Claude Projects (Claude.ai)

## Estructura

```
algo_i/
├── docs/               Curriculo y objetivos de aprendizaje
├── src/
│   ├── haskell/        Ejercicios resueltos en Haskell
│   └── python/         Ejercicios resueltos en Python
├── worklog/            Notas de sesion de estudio
└── assets/             Extractos de libros, apuntes, referencias
```

## Uso rapido

1. Abrir Claude.ai → Crear nuevo Project
2. Pegar el contenido de `rzl_gpt_apps/packs/draft/algo_i/02_agent_system_prompt.md`
3. Iniciar sesion con el modo deseado: `ESTUDIO:`, `PRACTICA:`, `REVISION:`, o `INGESTA:`
