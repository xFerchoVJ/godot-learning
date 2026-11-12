#!/usr/bin/env python3
"""Cave tileset for Slime Scavenger: 16x16 tiles, one row atlas, plus the level layout.

Outputs (in $OUT_DIR): tileset.png, tileset.tres (TileSet with wall/rock collision),
level_layout.txt (one char per tile, read by build_map.gd), previews.
Usage: ./run_char.sh tileset
"""
import os
import random

import numpy as np
from PIL import Image

from sprite_engine import hex_rgb, new_grid, put, to_rgba

# =============================== TUNABLES ===============================
TILE = 16
MAP_W, MAP_H = 20, 11                 # tiles; 320x176 of the 320x180 base resolution
BASE_RES = (320, 180)
BG = "#0b0f24"                        # preview background behind the 4 px left over
SEED = 7                              # fixed seed: the same tiles every run
GAME_TEXTURE_PATH = "res://assets/tiles/tileset.png"

# ---- Palette (index 0 unused: tiles are fully opaque) ----
F0, F1, F2, W0, W1, W2, M, R0, R1, R2 = range(1, 11)
PALETTE = {
    F0: "#162040", F1: "#1d2a4a", F2: "#2a3a66",   # floor: dark detail, base, light detail
    W0: "#2a3560", W1: "#3f4f86", W2: "#5d73ad",   # wall: shadow, mid, light (light from top-left)
    M: "#0f1630",                                   # mortar / rock outline
    R0: "#2f3b6e", R1: "#4c5d96", R2: "#8196cc",   # rock: shadow, mid, light
}

# Atlas order = column in tileset.png. Chars are what level_layout.txt uses.
TILES = ["floor_a", "floor_b", "floor_c", "wall", "rock"]
CHAR_TO_TILE = {"a": 0, "b": 1, "c": 2, "#": 3, "R": 4}
SOLID = {"wall": 8, "rock": 6}        # half-size of the collision square, px

# Level: floor variants are decided by a fixed formula, then baked into level_layout.txt.
# Rocks give cover. Keep rows 1-2 (top bat lane), row 8 (bottom bat lane) and column 11 (vertical bat lane) free.
ROCKS = {(4, 4), (4, 5), (7, 6), (13, 4), (13, 5), (16, 5), (16, 6)}


# =============================== TILES ===============================
def floor_base(rng):
    g = np.full((TILE, TILE), F1, np.uint8)
    for _ in range(6):
        put(g, rng.randint(1, TILE - 2), rng.randint(1, TILE - 2), F2)
    for _ in range(4):
        put(g, rng.randint(1, TILE - 2), rng.randint(1, TILE - 2), F0)
    return g


def tile_floor_b(rng):
    g = floor_base(rng)
    for i in range(6):                                     # diagonal crack
        put(g, 4 + i, 5 + i // 2 + (i % 2), F0)
    return g


def tile_floor_c(rng):
    g = floor_base(rng)
    for x, y in ((4, 4), (10, 9)):                         # two pebbles, light above and dark below
        put(g, x, y, F2); put(g, x + 1, y, F2)
        put(g, x, y + 1, F0); put(g, x + 1, y + 1, F0)
    return g


def tile_wall():
    g = np.full((TILE, TILE), W1, np.uint8)
    rows = ((0, 4, (7,)), (6, 9, (15,)), (11, 14, (7,)))   # (top, bottom, joint x); joints are staggered
    for top, bottom, joints in rows:
        for x in range(TILE):
            put(g, x, top, W2)                             # lit top edge
            put(g, x, bottom, W0)                          # shaded bottom edge
        for j in joints:
            for y in range(top, bottom + 1):
                put(g, j, y, M)
    for y in (5, 10, 15):                                  # mortar lines
        for x in range(TILE):
            put(g, x, y, M)
    return g


def tile_rock(rng):
    g = floor_base(rng)
    spans = {3: (5, 10), 4: (4, 11), 5: (3, 12), 6: (3, 12), 7: (3, 12),
             8: (3, 12), 9: (3, 12), 10: (3, 12), 11: (4, 11), 12: (5, 10)}
    for y, (x0, x1) in spans.items():
        for x in range(x0, x1 + 1):
            put(g, x, y, R2 if (x - x0 <= 1 or y == 3) else R0 if (x1 - x <= 1 or y >= 11) else R1)
    outline = g.copy()
    filled = np.zeros_like(g, bool)
    for y, (x0, x1) in spans.items():
        filled[y, x0:x1 + 1] = True
    pad = np.pad(filled, 1)
    near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    outline[(~filled) & near] = M
    return outline


def build_tiles():
    rng = random.Random(SEED)
    return [floor_base(rng), tile_floor_b(rng), tile_floor_c(rng), tile_wall(), tile_rock(rng)]


# =============================== LEVEL ===============================
def floor_char(x, y):
    v = (x * 7 + y * 13 + x * y) % 10
    return "b" if v == 0 else "c" if v == 1 else "a"


def build_layout():
    rows = []
    for y in range(MAP_H):
        row = ""
        for x in range(MAP_W):
            edge = x in (0, MAP_W - 1) or y in (0, MAP_H - 1)
            row += "#" if edge else "R" if (x, y) in ROCKS else floor_char(x, y)
        rows.append(row)
    return rows


# =============================== EXPORT ===============================
def square(half):
    return f"PackedVector2Array({-half}, {-half}, {half}, {-half}, {half}, {half}, {-half}, {half})"


def write_tres(path):
    lines = [
        '[gd_resource type="TileSet" load_steps=3 format=3]', "",
        f'[ext_resource type="Texture2D" path="{GAME_TEXTURE_PATH}" id="1_tex"]', "",
        '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_1"]',
        'texture = ExtResource("1_tex")',
        f"texture_region_size = Vector2i({TILE}, {TILE})",
    ]
    for i, name in enumerate(TILES):
        lines.append(f"{i}:0/0 = 0")
        if name in SOLID:
            lines.append(f"{i}:0/0/physics_layer_0/polygon_0/points = {square(SOLID[name])}")
    lines += ["", "[resource]", f"tile_size = Vector2i({TILE}, {TILE})",
              "physics_layer_0/collision_layer = 1", 'sources/0 = SubResource("TileSetAtlasSource_1")', ""]
    open(path, "w").write("\n".join(lines))


def render_map(tile_imgs, layout):
    img = Image.new("RGBA", BASE_RES, hex_rgb(BG) + (255,))
    for y, row in enumerate(layout):
        for x, ch in enumerate(row):
            img.paste(tile_imgs[CHAR_TO_TILE[ch]], (x * TILE, y * TILE))
    return img


def report(grids, layout):
    used = {int(i) for g in grids for i in np.unique(g)}
    checks = [
        (f"palette <= 12 colours ({len(used)})", len(used) <= 12),
        ("every tile is 16x16", all(g.shape == (TILE, TILE) for g in grids)),
        ("tiles fully opaque (no transparent cells)", all((g != 0).all() for g in grids)),
        ("layout is 20x11", len(layout) == MAP_H and all(len(r) == MAP_W for r in layout)),
        ("border is all wall", all(r[0] == "#" and r[-1] == "#" for r in layout)
         and set(layout[0]) == {"#"} and set(layout[-1]) == {"#"}),
        ("bat lanes free of rocks (rows 1-2, row 8, column 11)",
         all("R" not in layout[y] for y in (1, 2, 8)) and all(r[11] != "R" for r in layout)),
    ]
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def main():
    out = os.environ.get("OUT_DIR", "output")
    os.makedirs(out, exist_ok=True)
    grids = build_tiles()
    imgs = [Image.fromarray(to_rgba(g, PALETTE)) for g in grids]

    atlas = Image.new("RGBA", (TILE * len(imgs), TILE))
    for i, im in enumerate(imgs):
        atlas.paste(im, (i * TILE, 0))
    atlas.save(f"{out}/tileset.png")
    atlas.resize((atlas.width * 8, atlas.height * 8), Image.NEAREST).save(f"{out}/tileset_x8.png")

    layout = build_layout()
    open(f"{out}/level_layout.txt", "w").write("\n".join(layout) + "\n")
    write_tres(f"{out}/tileset.tres")

    prev = render_map(imgs, layout)
    prev.save(f"{out}/preview_map_1x.png")
    prev.resize((prev.width * 6, prev.height * 6), Image.NEAREST).save(f"{out}/preview_map_x6.png")

    print(f"Wrote tileset ({len(imgs)} tiles) and a {MAP_W}x{MAP_H} layout to {out}")
    report(grids, layout)


if __name__ == "__main__":
    main()
