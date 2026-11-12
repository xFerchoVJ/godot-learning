#!/usr/bin/env python3
"""Bat for Slime Scavenger: a 16x16 bat seen from the front/above, wings flapping.

Same structure as generate_sprite.py (palette, poses, parts, build_frame, SPEC).
Usage: ./run_char.sh bat [--stage fly|all]
"""
from sprite_engine import SpriteSpec, add_outline, new_grid, put, run

# =============================== TUNABLES ===============================
FRAME = 16
BASE_Y = 13              # lowest row of the lowest wing pose; not used by any check (the bat flies)
CX = 8

# ---- Palette (index 0 is transparent) ----
O, PD, PM, PL, E = range(1, 6)
PALETTE = {
    O: "#1b1535",                                  # outline (same cold dark purple as the other sprites)
    PD: "#4a2f8a", PM: "#7a4fc2", PL: "#b08af0",   # purple ramp: shadow, mid, light (light from top-left)
    E: "#ff4f8a",                                  # eyes: magenta, reads as "danger"
}

# ---- Wing poses: per column, (top_y, bottom_y). Columns go outward from the shoulder. ----
# Left wing x = 5, 4, 3, 2. The right wing mirrors it: x -> 15 - x. Keep x >= 2 so the outline stays in the frame.
WING_X = [5, 4, 3, 2]
WINGS = {
    "up":   [(7, 9), (6, 9), (4, 8), (2, 6)],
    "mid":  [(7, 9), (7, 9), (6, 9), (6, 8)],
    "down": [(7, 9), (8, 10), (9, 11), (10, 13)],
}

DEFAULT_POSE = dict(wing="mid")
FLY = [dict(wing="up"), dict(wing="mid"), dict(wing="down"), dict(wing="mid")]

ANIMS = [
    # 10 fps = 100 ms per frame (multiple of 10 ms, GIF stores centiseconds).
    dict(name="fly", fps=10, loop=True, poses=FLY),
]


# =============================== PARTS ===============================
def draw_body(g):
    put(g, 6, 5, PM)                                   # ears
    put(g, 9, 5, PM)
    for y, x0, x1 in ((6, 6, 9), (7, 6, 9), (8, 6, 9), (9, 7, 8), (10, 7, 8)):
        for x in range(x0, x1 + 1):
            put(g, x, y, PL if x == x0 else PM)
    put(g, 6, 7, E)                                    # eyes, 3 px apart
    put(g, 9, 7, E)


def draw_wings(g, p):
    for x, (top, bottom) in zip(WING_X, WINGS[p["wing"]]):
        for y in range(top, bottom + 1):
            c = PM if y == top else PD                 # lit leading edge, shadowed membrane
            put(g, x, y, c)
            put(g, 15 - x, y, c)


def build_frame(p):
    g = new_grid(FRAME)
    draw_wings(g, p)
    draw_body(g)                                       # body last: it sits on top of the wing roots
    return add_outline(g, O)


SPEC = SpriteSpec(
    frame=FRAME, base_y=BASE_Y, palette=PALETTE, outline_index=O,
    anims=ANIMS, build_frame=build_frame, default_pose=DEFAULT_POSE,
    baseline_anims=(), locked_anims=(), first_stage="fly",
    godot_sheet_path="res://assets/characters/bat/spritesheet.png",
    preview_size=(320, 180),
)

if __name__ == "__main__":
    run(SPEC)
