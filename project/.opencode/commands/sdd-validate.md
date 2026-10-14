---
description: SDD · Validar la spec RF por RF con veto duro del evaluador
agent: orquestador
---

Validación de la spec `specs/$1/`. Usa la skill `sdd`. Delega al subagente @evaluador
con este encargo:

- Lee `specs/$1/spec.md`, `plan.md` y `tasks.md`, y los cambios (`git diff`, `git status`).
- Ejecuta `python3 -m pytest`.
- Recorre la spec RF por RF: qué test cubre cada uno y su resultado. Los RF que no se
  puedan testear automáticamente (interfaz/web), verifícalos con el MCP de Playwright
  (firefox) o ejecutando la CLI real según el plan.
- Si algún RF no está cubierto o falla, dilo claramente. NO arregles nada todavía.
- Comprueba los criterios de finalización y la constitución, y emite veredicto:
  `VEREDICTO: APROBADO` o `VEREDICTO: CAMBIOS NECESARIOS` con lista numerada.

Si es CAMBIOS NECESARIOS, delega a @implementador la corrección (máx. 3 vueltas con
salida temprana si el 2.º FAIL repite causa o se toca algo fuera de alcance — entonces
escala a mí) y vuelve a validar. Al final, dame el veredicto y lo pendiente.