---
description: SDD · Generar el plan técnico de una spec aprobada
agent: orquestador
---

Plan técnico de la spec `specs/$1/`. Usa la skill `sdd`. Delega al subagente
@planificador con este encargo:

- Lee `docs/constitution.md`, `AGENTS.md` y `specs/$1/spec.md`. NO escribas código.
- Genera `specs/$1/plan.md` con: archivos que se crean o modifican y la responsabilidad
  de cada uno, funciones puras de lógica (sin I/O, con "hoy" como parámetro cuando
  aplique), algoritmo en pseudocódigo, cómo se expone en la CLI/interfaz, decisiones
  técnicas justificadas (con alternativa descartada) y estrategia de tests con
  `python3 -m pytest`.
- Todo debe respetar la constitución y cubrir todos los RF. Marca qué RF cubre cada parte.
- Si la spec no está aprobada o tiene dudas abiertas, para y avísame: no planees sobre
  una spec en borrador.

Enséñame un resumen del plan y espera mi aprobación antes de generar tareas.