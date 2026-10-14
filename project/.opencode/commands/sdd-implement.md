---
description: "SDD · Implementar UNA tarea con tests primero (uso: /sdd-implement 001-nombre T3)"
agent: orquestador
---

Implementación de la tarea `$2` de `specs/$1/tasks.md`. Usa la skill `sdd`. Delega al
subagente @implementador con este encargo y pásale todo el contexto (fase, tarea,
rutas de spec/plan/tasks y estado actual):

- Implementa SOLO `$2`, siguiendo `specs/$1/plan.md`, `docs/constitution.md` y AGENTS.md.
- 1. Escribe primero los tests y comprueba que fallan (rojo).
  2. Escribe el código hasta que pasen (verde).
  3. Ejecuta `python3 -m pytest` y muéstrame el resultado.
  4. Marca `$2` como hecha en `tasks.md` e indica qué RF cubre.
- Después PARA. No empieces la siguiente tarea.

Cuando @implementador termine, decide si merece una validación inmediata de @evaluador
o seguimos con la siguiente tarea. No marques la spec como validada sin el veredicto
del evaluador.