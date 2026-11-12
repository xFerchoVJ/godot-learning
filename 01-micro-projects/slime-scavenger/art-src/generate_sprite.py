#!/usr/bin/env python3
"""Starter character for the sprite pipeline: a 16x16 slime.

Replace the palette, the parts and the poses with your own character. Keep the structure:
  1. Tunables and palette as constants at the top.
  2. Poses: small dicts of offsets, one dict per frame.
  3. Parts: functions that draw onto the grid `g` with put().
  4. build_frame(pose): compose the parts, then add_outline().
  5. SPEC + run(SPEC).
Everything else (sheet, GIFs, previews, .tres, validation) lives in sprite_engine.py.

Usage: ./run.sh [--stage idle|all]      (--stage idle = approval gate: silhouette + idle only)
"""
from sprite_engine import SpriteSpec, add_outline, new_grid, put, run

# =============================== TUNABLES ===============================
FRAME = 16               # square frame, px
BASE_Y = 14              # sole row; the outline sits on row 15
CX = 8                   # body centre column

# ---- Palette: keep it small (characters: 8-12 colours). Index 0 is transparent. ----
O, BD, BM, BL = range(1, 5)
PALETTE = {
    O: "#1b1535",                                  # outline + eyes (cold dark purple, not pure black)
    BD: "#1f8a5a", BM: "#3fe08a", BL: "#b8ffd6",   # body ramp: shadow, mid, light (light from top-left)
}

# ---- Poses ----
# squash: which row table to use (0 = tall, 1 = squashed)   lean: upper-body shift forward, px
DEFAULT_POSE = dict(squash=0, lean=0)

IDLE = [dict(squash=0), dict(squash=1)]                       # breathing; feet stay locked
MOVE = [dict(squash=0, lean=1), dict(squash=1, lean=0)]       # hop forward

ANIMS = [
    # FPS must give a multiple of 10 ms: GIF stores centiseconds (4 -> 250 ms, 10 -> 100 ms).
    dict(name="idle", fps=4, loop=True, poses=IDLE),
    dict(name="move", fps=10, loop=True, poses=MOVE),
]

# Row widths from bottom to top. Keep the bottom two rows identical so the feet stay locked.
BODY = {0: [10, 10, 10, 8, 8, 6, 4], 1: [10, 10, 10, 8, 6, 4]}


# =============================== PARTS ===============================
def draw_body(g, p):
    for r, w in enumerate(BODY[p["squash"]]):
        y = BASE_Y - r
        x0 = CX - w // 2 + (p["lean"] if r >= 3 else 0)
        x1 = x0 + w - 1
        for x in range(x0, x1 + 1):                       # light on the left edge, shadow on the right
            put(g, x, y, BL if x == x0 else BD if x >= x1 - 1 else BM)
    put(g, CX - 2 + p["lean"], BASE_Y - 3, O)             # eyes, 1 px each, 3 px apart
    put(g, CX + 2 + p["lean"], BASE_Y - 3, O)


def build_frame(p):
    g = new_grid(FRAME)
    draw_body(g, p)
    return add_outline(g, O)


SPEC = SpriteSpec(
    frame=FRAME, base_y=BASE_Y, palette=PALETTE, outline_index=O,
    anims=ANIMS, build_frame=build_frame, default_pose=DEFAULT_POSE,
    godot_sheet_path="res://assets/characters/slime/spritesheet.png",
    preview_size=(320, 180),
)

if __name__ == "__main__":
    run(SPEC)
