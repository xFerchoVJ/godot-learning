#!/usr/bin/env python3
"""Gem for Slime Scavenger: a 16x16 cyan gem with a sparkle animation.

Same structure as generate_sprite.py (palette, poses, parts, build_frame, SPEC).
Usage: ./run_gem.sh [--stage idle|all]
"""
from sprite_engine import SpriteSpec, add_outline, new_grid, put, run

# =============================== TUNABLES ===============================
FRAME = 16
BASE_Y = 14              # bottom tip row; the outline sits on row 15
CX = 8

# ---- Palette (index 0 is transparent) ----
O, GD, GM, GL, W = range(1, 6)
PALETTE = {
    O: "#1b1535",                                  # outline (same cold dark purple as the slime)
    GD: "#1a7fb0", GM: "#35c8ee", GL: "#aaf0ff",   # cyan ramp: shadow, mid, light (light from top-left)
    W: "#ffffff",                                  # sparkle
}

# Row widths from top to bottom. The last two rows are identical so the tip stays locked.
ROWS = [4, 6, 8, 8, 6, 4, 2, 2]

# ---- Poses: spark = sparkle phase (0 none, 1 dot, 2 plus) ----
DEFAULT_POSE = dict(spark=0)
IDLE = [dict(spark=0), dict(spark=1), dict(spark=2), dict(spark=1)]

ANIMS = [
    # 5 fps = 200 ms per frame (multiple of 10 ms, GIF stores centiseconds).
    dict(name="idle", fps=5, loop=True, poses=IDLE),
]

SPARK_X, SPARK_Y = CX - 2, BASE_Y - 5      # sparkle centre, inside the crown


# =============================== PARTS ===============================
def draw_gem(g):
    top = BASE_Y - len(ROWS) + 1
    for r, w in enumerate(ROWS):
        y = top + r
        x0 = CX - w // 2
        x1 = x0 + w - 1
        for x in range(x0, x1 + 1):
            if r == 0 or x == x0:
                c = GL                      # top facet and left edge catch the light
            elif x >= x1 - 1 or r >= 4:
                c = GD                      # right edge and lower tip in shadow
            else:
                c = GM
            put(g, x, y, c)


def draw_sparkle(g, p):
    if p["spark"] >= 1:
        put(g, SPARK_X, SPARK_Y, W)
    if p["spark"] == 2:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            put(g, SPARK_X + dx, SPARK_Y + dy, W)


def build_frame(p):
    g = new_grid(FRAME)
    draw_gem(g)
    draw_sparkle(g, p)
    return add_outline(g, O)


SPEC = SpriteSpec(
    frame=FRAME, base_y=BASE_Y, palette=PALETTE, outline_index=O,
    anims=ANIMS, build_frame=build_frame, default_pose=DEFAULT_POSE,
    godot_sheet_path="res://assets/items/gem/spritesheet.png",
    preview_size=(320, 180),
)

if __name__ == "__main__":
    run(SPEC)
