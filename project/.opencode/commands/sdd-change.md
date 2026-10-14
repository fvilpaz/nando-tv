---
description: "SDD · Nuevo requisito - primero la spec, luego el código (uso: /sdd-change 001-nombre descripción del cambio)"
agent: orquestador
---

Nuevo requisito para la spec `specs/$1/`: $ARGUMENTS

NO toques código. Usa la skill `sdd`. Delega al subagente @planificador con este encargo:
1. Actualiza `specs/$1/spec.md`: nuevo RF (o cambio de uno existente) en EARS, sus casos
   límite y lo que queda fuera de alcance.
2. Indica qué partes de `plan.md` y `tasks.md` habría que cambiar después.
3. Devuelve el diff de la spec.

Enséñame el diff y espera mi aprobación. Tras aprobar, y solo entonces, se actualizan
plan y tareas y se implementa.