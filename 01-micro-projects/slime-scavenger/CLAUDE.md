# Slime Scavenger

Micro-proyecto top-down. Un slime recolecta gemas en una cueva mientras un murciélago patrulla. Gana si junta todas antes de que acabe el tiempo; pierde si el murciélago lo toca o se acaba el tiempo.

Estado: proyecto aprobado. Assets del MVP listos (slime, gema, murciélago) en `assets/`, `project.godot` creado (320x180, escala entera, Nearest). Lógica del MVP implementada por el usuario (movimiento, gemas, murciélago, temporizador, ganar/perder/reiniciar). Mapa 20x11 con TileMapLayer listo (`scenes/level_map.tscn`, generado desde `art-src/generate_tileset.py` + `art-src/build_map.gd`). Sonidos listos y conectados (`assets/audio/`, generados con `art-src/generate_audio.py`). MVP completo; pendiente opcional: pulir HUD y renombrar `test_scene` a `main`.

## Alcance (MVP)
- 1 mapa, 1 slime, 1 tipo de gema, 1 murciélago, contador de gemas + temporizador, pantalla de victoria/derrota con reinicio.
- Fuera de MVP (versión futura): más enemigos, power-ups, niveles, música dinámica.

## Habilidades a practicar
- Input Map + `Input.get_vector()`, `CharacterBody2D` en `_physics_process`.
- `Area2D` + señales (gemas, daño) y señales custom hacia el HUD/mapa.
- Instanciar escenas por código, grupos de nodos.
- `Timer`, HUD con `CanvasLayer`, reinicio de escena.
- IA simple de patrulla.

## Reparto de trabajo
- **Usuario:** movimiento del slime, murciélago (patrulla + contacto), recolección de gemas, señales, lógica de ganar/perder, HUD.
- **Claude:** estructura de carpetas, `project.godot`/configuración, assets (sprites, tileset, sonidos), integración de recursos, TileMapLayer del mapa.

## Dirección artística y sonora
- Vista top-down, frames de 16x16.
- Resolución base 320x180, escala entera 6x (1920x1080), Texture Filter Nearest.
- Paleta "cueva fría": fondo azul/morado oscuro, slime verde brillante, gemas cian/magenta, máx. 12 colores. Luz desde arriba a la izquierda.
- Animaciones MVP: slime `idle` + `move` (flip_h para voltear), murciélago aleteo, gema brillo.
- Audio: pendiente.
- Pipeline: `tools/sprite-pipeline/` copiado a `art-src/`, resultados en `assets/`.

## Criterios de finalización
- Se puede jugar una partida completa: mover, recolectar, evitar al murciélago, ganar o perder, reiniciar.
- El usuario puede explicar cómo funcionan sus señales y reimplementar el movimiento sin consultar el código.
- Assets propios integrados, legibles a 1x.
