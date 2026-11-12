<div align="center">

# 🎮 Godot Learning

### Aprendiendo a hacer videojuegos 2D con **Godot 4** y **GDScript**, un juego a la vez.

![Godot](https://img.shields.io/badge/Godot-4.x-478CBF?logo=godotengine&logoColor=white)
![GDScript](https://img.shields.io/badge/GDScript-100%25-355570)
![Pixel Art](https://img.shields.io/badge/arte-pixel%20art-ff6fb5)
![Estado](https://img.shields.io/badge/estado-aprendiendo%20🚀-7cfc9a)

*Sprites, tilesets y sonidos hechos desde cero con código. Sin packs descargados.*

</div>

---

## 👾 ¿De qué va esto?

Soy desarrollador web (Ruby on Rails) y este repo es mi **bitácora de aprender videojuegos por hobby**.
La idea es simple: *aprender haciendo*. Cada proyecto es un juego pequeño y terminable que me enseña
un puñado de conceptos nuevos y refuerza los anteriores.

Nada de tutoriales eternos: retos pequeños, experimentar, equivocarme y volver a implementar.

## 🕹️ Juegos

| # | Juego | Género | Estado | Lo que practiqué |
|---|-------|--------|--------|------------------|
| 1 | 🟢 **Slime Scavenger** | Top-down, recolección | ✅ MVP terminado | Movimiento, `Area2D` + señales, patrullas, `Timer`, audio, reinicio |
| 2 | ⚡ **Spark Survivor** | Arena de supervivencia | 🛠️ Próximamente | Apuntar con mouse, instanciar escenas por código, vida/daño |

### 🟢 Slime Scavenger

Un slime explora una cueva fría, junta todas las gemas y esquiva a los murciélagos que patrullan.
Gana si recolecta todo antes de que se acabe el tiempo. 🦇💎

- Vista top-down con pixel art de 16×16
- Resolución base 320×180 con escala entera (look retro nítido)
- Paleta limitada "cueva fría" (≤ 12 colores)
- Efectos de sonido chiptune generados con Python

📂 [`01-micro-projects/slime-scavenger`](01-micro-projects/slime-scavenger)

## 🎨 Assets 100% propios

Cada juego tiene su identidad visual y sonora, y **todo se genera con código**:

- 🖼️ **Sprites y spritesheets:** Python (Pillow + numpy) dentro de Docker → spritesheet, GIFs de preview,
  `SpriteFrames` listos para Godot y un reporte de validación (bordes duros, paleta, outline de 1 px...).
- 🧱 **Tilesets y mapas:** generados por script y armados con `TileMapLayer`.
- 🔊 **Audio:** efectos chiptune sintetizados con Python.

La plantilla del pipeline vive en [`tools/sprite-pipeline`](tools/sprite-pipeline), con un slime de arranque
y un mago de ejemplo.

## 🧰 Stack

- **Motor:** [Godot 4](https://godotengine.org/) (2D, filtro *Nearest*, escala entera)
- **Lenguaje:** GDScript
- **Herramientas de arte/audio:** Python 3 · Pillow · numpy · Docker
- **Compañero de estudio:** [Claude Code](https://claude.com/claude-code) como mentor y asistente de assets

## 📁 Estructura

```
Godot-Learning/
├── 01-micro-projects/     # Juegos pequeños para aprender lo básico
│   └── slime-scavenger/
├── 02-mini-games/         # Juegos un poco más completos (pronto)
├── tools/
│   └── sprite-pipeline/   # Generador de sprites con Python + Docker
└── LEARNING-PROGRESS.md   # Qué he aprendido y qué falta reforzar
```

## ▶️ Cómo jugar / abrir un proyecto

1. Instala [Godot 4](https://godotengine.org/download).
2. Clona el repo:
   ```bash
   git clone https://github.com/<tu-usuario>/Godot-Learning.git
   ```
3. Abre Godot → **Import** → elige el `project.godot` del juego que quieras (por ejemplo
   `01-micro-projects/slime-scavenger/project.godot`).
4. Presiona **F5** y a jugar. 🎉

**Controles de Slime Scavenger:** `WASD` para moverte · `Shift` para caminar lento · tecla de reinicio al terminar.

## 🧠 Filosofía

- **Aprender > terminar rápido.** Yo escribo la lógica de juego; la IA ayuda con assets y configuración.
- **MVP primero.** Juegos pequeños que sí se terminan.
- **Repetir con variaciones.** Cada mecánica vuelve a aparecer en otro contexto.

## 📈 Progreso

Sigo mi avance en [`LEARNING-PROGRESS.md`](LEARNING-PROGRESS.md): conceptos dominados, dificultades
recurrentes y próximos retos.

---

<div align="center">

Hecho con ☕, pixeles y muchos `queue_free()` 💚

</div>
