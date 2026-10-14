# MEMORIA — Nandflix

Memoria entre sesiones. Cabecera "Estado actual" (la sobreescribe el orquestador) + log
fechado append-only. Tachar con `~~ ~~`, nunca borrar. Red de datos: el orquestador es
el único escritor; los subagentes leen.

## Estado actual
- Metodología SDD + multiagente montada: 4 agentes (`.opencode/agents/`), skill `sdd`,
  comandos `/sdd-*`, `AGENTS.md`, `docs/constitution.md` y este archivo.
- Piloto: `habits-cli` (CLI de hábitos en Python, stdlib) — pendiente de crear la spec
  `specs/001-habits-mvp/`.
- `opencode.json`: MCP Playwright (firefox) activo; `default_agent=orquestador`. Pendiente
  reiniciar opencode para cargar config, agentes, skill y comandos. Falta `npx playwright
  install firefox` para usar el MCP.
- Telegram 7.2.9 (flatpak) lanzado; `.desktop` copiado a `~/.local/share/applications/`
  y añadido al dock (fix temporal; el fix de raíz es reloguearse para refrescar
  `XDG_DATA_DIRS`).
- Curso MoureDev (apuntes días 1-3 en `~/Documentos/DOC-*.pdf`): validan la arquitectura
  (día 2 = SDD + comandos/skills, día 3 = multiagentes). Sintaxis `permissions:` del curso
  es obsoleta → se usa `permission:` del schema real.

## Decisiones (y por qué)
- Piloto = `habits-cli` (no Nandoflix directo): validar la metodología contra un
  resultado conocido antes de aplicarla al proyecto real. Nandoflix será `002-` cuando
  toque.
- 4 roles, sin clarificador separado (clarifica el planificador). Veto duro del evaluador
  con 3 vueltas de refactor y salida temprana si el 2.º FAIL repite causa o se sale del
  alcance.
- `memoria.md` híbrido (estado + log append-only). Tests los escribe el implementador; el
  evaluador verifica/veta (imparcialidad).
- Especialistas (legal/UX/…) = skills bajo demanda + subagente consultor, no agentes fijos
  (pendiente de crear el `consultor` si hace falta).
- Alfa/Bravo (2 terminales): RESERVADO como evolución futura, no para el piloto — solo
  aporta cuando haya paralelismo real.
- Canal entre instancias: `DEBATE.md` (buzón) + BD compartida de opencode. Prueba manual
  en curso; MCP de buzón (config global) como siguiente paso si se quiere automatizar.

## Aprendizajes y errores a evitar
- Los agentes del curso (y el `permissions:`/`prompts.md`) usan sintaxis que opencode ya
  no acepta: validar siempre contra el schema (`opencode.ai/config.json`).
- `XDG_DATA_DIRS` de una sesión gráfica no ve flatpaks hasta el relogin (no tocar config,
  es perfil de login).
- MCP Playwright requiere `npx playwright install firefox` antes del primer uso.

## Próximos pasos
- Reiniciar opencode (carga config, agentes, skill y comandos).
- Arrancar el piloto: `/sdd-spec 001-habits-mvp <idea>` para crear la spec y validar el
  flujo completo (spec → clarificación → plan → tareas → implementación → validación).
- Responder/cerrar el hilo de `DEBATE.md` con la otra instancia.

## Log
- **2026-10-08**: Constitución SDD+multiagente; aprobado el diseño del curso MoureDev con
  correcciones (permisos, pytest, roles en español).