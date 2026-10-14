---
description: "SDD · Entrevista y genera la spec (uso: /sdd-spec 002-nombre idea inicial)"
agent: orquestador
---

Nueva especificación. Usa la skill `sdd`. Delega al subagente @planificador con este
encargo exacto:

- Carpeta de la spec: `specs/$1/`.
- Idea inicial: $ARGUMENTS
- Lee `docs/constitution.md` y `memoria.md`.
- Si la petición es ambigua, devuelve SOLO una lista numerada de preguntas (máximo 5),
  de una en una al usuario: elimina ambigüedades, casos límite, comportamientos con error
  y lo que queda fuera de esta versión.
- Con las respuestas, crea `specs/$1/spec.md` con la plantilla de la skill `sdd`,
  requisitos en notación EARS (en español) y "Estado: borrador".
- Solo el QUÉ y el POR QUÉ: nada de stack, arquitectura ni nombres de archivos.

Pásame tú las preguntas de @planificador de una en una para que el usuario responda, y
devuelve a @planificador con las respuestas. No aprobemos la spec hasta que el usuario
la valide.