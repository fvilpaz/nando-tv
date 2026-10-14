---
description: SDD · Dividir el plan en tareas pequeñas y verificables
agent: orquestador
---

Tareas de la spec `specs/$1/`. Usa la skill `sdd`. Delega al subagente @planificador
con este encargo:

- A partir de `specs/$1/spec.md` y `specs/$1/plan.md`, genera `specs/$1/tasks.md`
  siguiendo el formato de la skill `sdd`:
  - Tareas pequeñas (máx. 20-30 min), en orden de dependencia.
  - Cada una con los RF que cubre y una línea "Hecho cuando:" verificable.
  - Checkboxes.
  - Que no sean más de 10: si salen más, propón dividir la spec.

Enséñame la lista de tareas y espera mi aprobación antes de empezar a implementar.