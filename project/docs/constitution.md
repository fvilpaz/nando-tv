# Constitución — Nandflix

Principios innegociables. Toda spec, plan y tarea debe cumplirlos.

1. **Simplicidad primero**: Python 3 con solo la librería estándar en el piloto. Sin
   dependencias de terceros ni pasos de build que no estén justificados en el plan.
2. **La spec manda**: nada se implementa si no está en la spec activa. Si falta una
   decisión, se para y se pregunta.
3. **Lógica separada de I/O**: los cálculos (fechas, rachas, estadísticas) son funciones
   puras, sin I/O ni argumentos implícitos; reciben datos por parámetro. Storage y CLI
   quedan al margen.
4. **Tests como puerta**: se prueba con `pytest`. Los tests se escriben antes que el
   código (rojo → verde). Prohibido avanzar con tests en rojo; el evaluador veta.
5. **Los datos del titular son sagrados**: persistencia con compatibilidad hacia atrás,
   fechas en hora local y nunca se destruye información sin confirmación.
6. **Idiomas**: código y salida de la CLI en inglés; spec, plan, tasks y documentación
   en español.