# AGENTS.md — Nandflix (metodología SDD + piloto habits-cli)

Proyecto que combina (1) un sistema multiagente de desarrollo basado en Spec-Driven
Development y (2) su validación con un piloto: una CLI de hábitos en Python.

## Stack y estructura
- Piloto: **Python 3 (solo stdlib)**, sin dependencias de terceros. Tests con `pytest`.
- `.opencode/agents/` → roles: `orquestador` (primary), `planificador`, `implementador`,
  `evaluador` (subagentes).
- `.opencode/skills/sdd/` → flujo y plantillas SDD. `.opencode/commands/` → `/sdd-*`.
- `docs/constitution.md` → principios innegociables. `memoria.md` → memoria entre sesiones.
- `specs/NNN-nombre/{spec,plan,tasks}.md` → una carpeta por funcionalidad.

## Comandos
- Tests: `python3 -m pytest` (o `python3 -m unittest` si el plan lo indica).
- Ejecutar la CLI del piloto: `python3 -m habits ...` según la spec.

## Convenciones
- Código y mensajes CLI en inglés; spec/plan/tasks y documentación en español.
- Tests primero (rojo → verde). Una tarea de tasks.md por turno; nunca se salta una tarea.
- Separación de responsabilidades: lógica de dominio pura (sin I/O) separada de
  storage y de la CLI.

## Metodología (SDD)
- Flujo: Constitución → Spec → Clarificación → Plan → Tareas → Implementación →
  Validación → Cambio. Ninguna fase avanza sin aprobación explícita del usuario.
- La spec manda: nada se implementa si no está en la spec activa; si falta una
  decisión, se para y se pregunta.
- Cambio de requisitos: primero `spec.md`, luego plan/tareas, por último el código.
- Requisitos en notación EARS, cada RF verificable (se convierte en test).

## Separación de funciones
- `orquestador`: coordina y delega; NUNCA escribe código ni specs (solo `memoria.md`,
  `DEBATE.md`).
- `planificador`: spec, plan y tareas (solo escribe en `specs/` y `docs/`).
- `implementador`: código + tests de UNA tarea, la marca hecha y para.
- `evaluador`: veta (APROBADO / CAMBIOS NECESARIOS), solo ejecuta tests y git.
- Los subagentes NO ven la conversación del orquestador: se les pasa todo el contexto.

## Límites
- ✅ Siempre: seguir la skill `sdd`; respetar la constitución; actualizar `memoria.md`.
- ⚠️ Pregunta antes: nuevas dependencias, archivos nuevos fuera del plan, cambios en
  el formato de datos persistidos.
- 🚫 Nunca: instalar dependencias en el piloto; el orquestador tocando código; escribir
  código sin spec aprobada.

## Verificación
- `python3 -m pytest` en verde antes de dar por hecha una tarea.
- Validación final: el evaluador recorre la spec RF por RF y da veredicto.