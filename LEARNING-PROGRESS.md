# LEARNING-PROGRESS

Entorno: Godot 4.7.2 stable (`/Applications/Godot.app`, no está en el PATH).

## Proyectos completados
- **Slime Scavenger** (01-micro-projects): MVP jugable completo (2026-11-11). Pendiente de pulir: HUD (fuente grande a 320x180) y renombrar `test_scene`/`Label2`. Autonomía por verificar en el siguiente proyecto.

## Diagnóstico inicial (2026-11-11, autorreportado, sin verificar en práctica)
- Escenas = conjunto de nodos; player típico con CharacterBody2D + Sprite2D + CollisionShape2D + AnimationPlayer + script.
- `move_and_slide()` en `_physics_process`.
- Señales: Area2D `body_entered`, señales custom (emisor desconoce al receptor, conexión en `_ready`).
- Experiencia previa: juegos siguiendo tutoriales.

## Autonomía comprobada
- Slime Scavenger, movimiento del player (hecho sin ayuda, desde cero): escena CharacterBody2D + AnimatedSprite2D + CollisionShape2D, Input Map (WASD), `Input.get_vector()`, `move_and_slide()` en `_physics_process`, `flip_h`, `@export`. Modificó el movimiento sin ayuda (Shift = media velocidad con `slow_walk` y `@export slow_factor`) y corrigió el bug de animar según `velocity` en vez de `direction`, explicando por qué. Falta: re-implementarlo en otro proyecto sin mirar este código.

- Gemas (Area2D + `body_entered` + grupos), señal custom `collected` conectada por código en `_ready`, contador "x / total" con condición de victoria. Hecho sin ayuda; falta re-implementar en otro contexto (p. ej. instanciando gemas por código).

- Patrulla del murciélago A↔B (variable `target`, `distance_to`, `direction_to`, `@export Vector2`). Necesitó 3 pistas para arrancar (le costó pasar de la idea a las variables), luego lo armó solo. Anotar: pedir "esqueleto con huecos" funciona bien con este tipo de lógica.

- Estado de partida con `bool game_over`, reinicio con `reload_current_scene()` y Input Map `reload_game`, congelar nodos con `set_physics_process(false)` + `stop()`. Usó `_process` para leer input de reinicio (falta que explique por qué).

- `Timer` (señal `timeout` conectada en el editor, `time_left` mostrado en `_process`), derrota por tiempo reutilizando `game_over`. Eligió `_process` para la UI tras el experimento de `delta`.

- Refactor a `_end_game(message)`, `Timer.one_shot` y `paused`. Al refactorizar perdió el guard `if game_over: return` (reabre un caso de mismo frame). Patrón a vigilar: al unificar código, revisar qué protecciones tenían las versiones anteriores.

- Audio: `AudioStreamPlayer` en la escena principal (no dentro de la gema, que se libera), `play()` por evento, `_end_game(won: bool)`. Resolvió el corte del sonido de reinicio conectando `finished` del reproductor para recargar después (entendió que un sonido vive lo que vive su nodo).

## Por reforzar (actualización)
- `_process` vs `_physics_process` sigue sin comprobarse en práctica.

## Por reforzar
- `_process` vs `_physics_process` (cuál y por qué; `delta`).
- Pasar de seguir tutoriales a implementar desde cero.

## Dificultades recurrentes
- Nombres de función que no dicen lo que hacen (`_update_label_text` que solo devuelve texto; `_loop_and_connect_signals` que además calcula `total_gems`). Revisar en cada código nuevo.
- Estado de partida: win/lose no son excluyentes todavía.

## Siguiente proyecto (aprobado 2026-11-12, aún sin crear)
- **Spark Survivor** (02-mini-games): arena top-down de supervivencia, disparo con mouse, enemigos que persiguen, 3 vidas, oleadas por tiempo. Nuevo: instanciar por código, apuntar con mouse, vida/daño con señales. Refuerza: movimiento (prueba de autonomía), persecución, Area2D, Timer, audio. Pendiente: preparar su `CLAUDE.md` y entrevista de arte (identidad nueva, sin reutilizar assets de Slime Scavenger).

## Próximas oportunidades
- Input Map + `Input.get_vector()`, instanciar escenas por código, grupos, Timer, HUD con CanvasLayer, reinicio de escena.
