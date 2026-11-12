# Sprite pipeline (template)

Procedural pixel-art sprites for Godot 4. Python runs inside Docker (Pillow + numpy);
nothing is installed on the host. Art rules come from the `pixel-art-sprites` skill.

## What is here

| File | Role |
|---|---|
| `sprite_engine.py` | Shared engine: spritesheet, GIFs, 1x preview, silhouette, `SpriteFrames` `.tres`, validation report. Do not edit per project. |
| `generate_sprite.py` | Starter character (16x16 slime). This is the file you replace with your own character. |
| `examples/wizard/` | Full reference character (32x32, 4 animations). Shows how parts and poses scale up. |
| `Dockerfile`, `docker-compose.yml`, `run.sh` | Docker workflow. One shared image for every project. |

## Use it in a project

1. Copy this folder to `<project>/art-src/` (without `examples/` if you do not need it).
2. Define the art direction first (skill interview: view, frame size, base resolution,
   palette, priority animations) and write it into the project's `CLAUDE.md`.
3. Edit `art-src/generate_sprite.py`: palette, parts, poses, `ANIMS`.
4. `./run.sh --stage idle` renders only the first animation: judge silhouette and idle
   (look at `output/preview_x6.png`) **before** animating the rest.
5. `./run.sh` renders everything and prints a PASS/FAIL report.
6. Copy `output/spritesheet.png` and `output/character.tres` to `<project>/assets/...`
   and set `godot_sheet_path` in the spec to that `res://` path.

## Output (`output/`)

`spritesheet.png` (one row per animation, no padding), one `<anim>.gif` per animation (x8),
`preview_1x.png` (true size, base resolution), `preview_x6.png`, `silhouette.png`, `character.tres`.

## Authoring model

A character is: palette constants, poses (one small dict per frame), parts (functions that
draw with `put(g, x, y, colour_index)`), `build_frame(pose)` and a `SpriteSpec`.
Draw every frame from the same parts and a fixed feet row so nothing wobbles between frames.
`add_outline()` adds the 1 px outside outline automatically.

`SpriteSpec` knobs: `frame`, `base_y`, `palette`, `sheet_cols`, `gif_scale`, `preview_size`
(the game's base resolution), `max_colors`, `baseline_anims`, `locked_anims`, `first_stage`.

## What the report checks

Hard edges (alpha 0 or 255 only), palette size, uniform sheet, nothing touching the frame
edges, 1 px outline, feet on the baseline row, locked idle feet, GIF timing equals FPS.

## Gotchas learned

- A gap of exactly 2 px between two outlined parts fills with outline and makes a 2x2 block.
  Keep gaps at 1 px or 3 px and more.
- GIF stores centiseconds: use FPS that give multiples of 10 ms (4, 5, 10, 20), not 8.
- Mirrored run halves are identical in silhouette. Shade the far leg and vary the hem or hat phase.
- Light comes from the top-left: light on the left edge, shadow on the right and bottom.
- In Godot: Texture Filter = Nearest, integer stretch scale, and pick `jump` or `fall` from `velocity.y`.

## Not built yet

`TileSet`/`TileMapLayer` export and audio generation. Add them to the engine when a project needs them.
