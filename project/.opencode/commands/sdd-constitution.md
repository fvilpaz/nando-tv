---
description: SDD · Proponer la constitución del proyecto (principios innegociables)
agent: orquestador
---

Vamos a crear (o revisar, si ya existe) `docs/constitution.md`. Usa la skill `sdd`.
Delega esta tarea al subagente @planificador con este encargo, y cuando devuelva la
propuesta enséñamela para mi aprobación antes de que se escriba el archivo:

- Lee AGENTS.md, memoria.md y la estructura del proyecto antes de proponer nada.
- Propón 6 principios innegociables, cortos y verificables, que cubran: simplicidad del
  stack, relación entre spec y código, separación entre lógica e infraestructura, política
  de tests (pytest, sin dependencias), protección de los datos del usuario y del proyecto,
  e idioma (código en inglés; docs y especs en español). Máximo 15 líneas.
- NO escribas el archivo todavía: espera mi aprobación.

Contexto adicional: $ARGUMENTS