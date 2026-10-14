---
description: SDD · Revisar la spec como QA (solo detecta, no resuelve)
agent: orquestador
---

Clarificación de la spec `specs/$1/spec.md`. Usa la skill `sdd`. Delega al subagente
@evaluador con este encargo:

- Revisa `specs/$1/spec.md` como un QA muy profesional.
- Lista solo: (1) ambigüedades restantes, (2) contradicciones entre requisitos,
  (3) casos límite no cubiertos, (4) conflictos con `docs/constitution.md`.
- No propongas soluciones todavía: solo detecta. Formato: lista numerada.

Enséñame el resultado. Si hay hallazgos, se delega a @planificador que corrija la spec y
se repite la clarificación hasta que no queden problemas. No continúes al plan hasta que
yo apruebe la spec.