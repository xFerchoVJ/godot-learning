#!/usr/bin/env python3
"""Reference example: pixel-art wizard (32x32, side view, facing right) on sprite_engine.

Shows a full character: parts drawn onto an index grid, poses as small dicts, four
animations. It is an example of HOW to build a character, not a design to reuse:
each project gets its own palette, proportions and parts.

To try it: copy this file over art-src/generate_sprite.py (next to sprite_engine.py)
and run ./run.sh.
"""
import os
import sys

# Lets the example run in place (examples/wizard/ -> ../../sprite_engine.py).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from sprite_engine import SpriteSpec, add_outline, new_grid, put, run  # noqa: E402

# =============================== TUNABLES ===============================
FRAME = 32               # square frame, px
BASE_Y = 30              # row of the soles (feet baseline); the outline sits on row 31
CX = 13                  # body centre column
HEM_Y = 27               # last row of the robe
STAFF_X = 25             # staff column (idle)

# ---- Palette: 10 colours (characters should stay within 8-12) ----
O, RD, RM, RL, SL, SD, WD, GD, GM, GL = range(1, 11)
PALETTE = {
    O: "#1a1a2e",                                  # outline + eye (near-black, not pure black)
    RD: "#2b2f7a", RM: "#3f5fc8", RL: "#6fa8f0",   # robe ramp: shadow -> purple, light -> cyan
    SL: "#f2c6a0", SD: "#c98a6b",                  # skin
    WD: "#7a4a2a",                                 # wood (staff) / boots
    GD: "#e8b84a",                                 # gold trim
    GM: "#5ef2ff", GL: "#e8ffff",                  # gem
}

# ---- Poses ----
# dy: upper-body vertical offset (+ = down)   lean: upper-body forward shift
# tip: hat-tip horizontal lag                 far/near: (foot x offset, foot lift)
# trail: robe hem trailing backwards          flare: hem widening
# jag: None or phase of a ragged hem          staff: (top y, bottom y, bottom x shift)
DEFAULT_POSE = dict(dy=0, lean=0, tip=0, far=(-3, 0), near=(2, 0),
                    trail=0, flare=0, jag=None, staff=(4, 30, 0), far_boot=WD)

# Breathing: the body drops 1 px for two frames while the feet stay locked.
IDLE = [dict(dy=0, tip=0), dict(dy=0, tip=1), dict(dy=1, tip=0), dict(dy=1, tip=-1)]

# Run: contact -> down -> passing, once per leg. Body leans into the run, hem and hat trail behind,
# staff is carried raised and tilted. The body is lowest on "down" and highest on "passing".
RUN_STAFF = (5, 27, -1)   # tilt kept small: -2 pushes the staff outline against the robe outline
# Half B swaps near/far legs; the far leg is drawn darker, and the hem flutter phase differs,
# so the two halves of the cycle are not pixel-identical.
RUN = [
    dict(dy=1, lean=1, tip=-1, far=(-5, 0), near=(4, 0), trail=1, jag=0, staff=RUN_STAFF),   # contact A
    dict(dy=1, lean=1, tip=0, far=(-4, 1), near=(1, 0), trail=2, jag=1, staff=RUN_STAFF),    # down A
    dict(dy=0, lean=1, tip=-1, far=(3, 1), near=(-1, 0), trail=2, jag=2, staff=RUN_STAFF),   # passing A
    dict(dy=1, lean=1, tip=-1, far=(4, 0), near=(-5, 0), trail=1, jag=1, staff=RUN_STAFF),   # contact B
    dict(dy=1, lean=1, tip=0, far=(1, 0), near=(-4, 1), trail=2, jag=2, staff=RUN_STAFF),    # down B
    dict(dy=0, lean=1, tip=-1, far=(-1, 0), near=(3, 1), trail=2, jag=0, staff=RUN_STAFF),   # passing B
]
RUN = [dict(p, far_boot=RD) for p in RUN]   # far boot in shadow (depth cue); idle keeps brown

# Jump: takeoff squash, then rise with feet tucked and the staff pulled up.
JUMP = [
    dict(dy=2, tip=1, far=(-3, 0), near=(3, 0), flare=1),
    dict(dy=0, tip=-1, flare=-1, far=(-2, 1), near=(2, 1), staff=(3, 29, -1)),   # narrow hem = stretch
]

# Fall: hem flares and flaps, hat tip streams, feet dangle.
FALL = [
    dict(dy=0, tip=1, flare=1, jag=0, far=(-3, 1), near=(3, 1), staff=(3, 29, -1)),
    dict(dy=1, tip=-1, flare=1, jag=1, far=(-3, 1), near=(3, 0), staff=(4, 29, 0)),
]

ANIMS = [
    dict(name="idle", fps=4, loop=True, poses=IDLE),    # 250 ms per frame
    dict(name="run", fps=10, loop=True, poses=RUN),     # 100 ms
    # 100 ms (not 125): GIF stores centiseconds, so 125 ms would round and drift from the .tres
    dict(name="jump", fps=10, loop=False, poses=JUMP),
    dict(name="fall", fps=10, loop=True, poses=FALL),
]


# =============================== PARTS ===============================
def shaded_span(g, y, x0, x1):
    """Light on the left edge, shadow on the two right-most pixels (top-left light)."""
    for x in range(x0, x1 + 1):
        put(g, x, y, RL if x == x0 else RD if x >= x1 - 1 else RM)


def draw_hat(g, p):
    """Pointed hat leaning back: nearly vertical left edge, diagonal right edge."""
    top = 2 + p["dy"]
    cx = CX + p["lean"]
    rows = 9
    for r in range(rows):
        sh = round(p["tip"] * max(0, 3 - r) / 3) - (1 if r < 2 else 0)  # tip sways; base curl hooks it back
        x0 = cx - 3 - round(r / 4) + sh
        x1 = cx - 2 + r + sh
        shaded_span(g, top + r, x0, x1)
        if r == rows - 1:  # gold band on the last cone row
            for x in range(x0, x1 + 1):
                put(g, x, top + r, GD)
    by = top + rows
    shaded_span(g, by, cx - 8, cx + 9)             # brim, top face
    for x in range(cx - 6, cx + 8):                # brim, underside in shadow
        put(g, x, by + 1, RD)


def draw_head(g, p):
    y = 13 + p["dy"]
    cx = CX + p["lean"]
    rows = [(-3, 4, SD), (-4, 5, SL), (-4, 5, SL), (-3, 5, SL), (-3, 4, SD)]
    for i, (a, b, c) in enumerate(rows):  # first/last rows are shadow (brim / chin)
        for x in range(cx + a, cx + b + 1):
            put(g, x, y + i, c)
    put(g, cx + 6, y + 2, SL)  # nose
    put(g, cx + 3, y + 1, O)   # eye, 1 px
    put(g, cx - 2, y + 2, SD)  # ear


def draw_robe(g, p):
    top = 18 + p["dy"]
    span = HEM_Y - top
    for y in range(top, HEM_Y + 1):
        t = (y - top) / span
        cxy = CX + round(p["lean"] * (1 - t))          # lean fades out toward the hem
        low = t > 0.5
        x0 = (cxy - 4 - round(t * 3) - (p["flare"] if low else 0)
              - round(p["trail"] * max(0.0, (t - 0.4) / 0.6)))
        x1 = cxy + 4 + round(t * 3) + (p["flare"] if low else 0)
        for x in range(x0, x1 + 1):
            if y == HEM_Y and p["jag"] is not None and (x + p["jag"]) % 3 == 0:
                continue
            if y == top + 4:
                c = GD                                  # belt
            elif x == cxy - 1 and top + 6 <= y <= HEM_Y - 1:
                c = RD                                  # one fold line on the skirt
            else:
                c = RL if x == x0 else RD if x >= x1 - 1 else RM
            put(g, x, y, c)


def draw_leg(g, xo, lift, boot, trouser=RD):
    c = CX + xo
    sole = BASE_Y - lift
    for x in range(c - 1, c + 2):                       # sole: 3 px; the 2 px ankle sits left, so the toe points right
        put(g, x, sole, boot)
    put(g, c - 1, sole - 1, boot)                       # ankle
    put(g, c, sole - 1, boot)
    hip = CX + round(xo * 0.4)
    for y in range(HEM_Y + 1, sole - 1):                # trousers from the hem to the ankle
        t = (y - HEM_Y) / max(1, (sole - 1) - HEM_Y)
        x = round((hip - 1) + ((c - 1) - (hip - 1)) * t)
        put(g, x, y, trouser)
        put(g, x + 1, y, trouser)


def staff_x(p, y):
    top_y, bot_y, bot_dx = p["staff"]
    y0 = top_y + 4
    t = 0.0 if bot_y <= y0 else min(1.0, max(0.0, (y - y0) / (bot_y - y0)))
    return STAFF_X + round(bot_dx * t)


def draw_staff(g, p):
    top_y, bot_y, _ = p["staff"]
    gy = top_y + 1
    for dx, dy, c in [(0, -1, GL), (-1, 0, GM), (0, 0, GM), (1, 0, GM), (0, 1, GM)]:
        put(g, STAFF_X + dx, gy + dy, c)                # diamond gem, highlight on top
    put(g, STAFF_X, top_y + 3, GD)                      # gold cap
    for y in range(top_y + 4, bot_y + 1):
        put(g, staff_x(p, y), y, WD)


def draw_arm(g, p):
    cx = CX + p["lean"]
    hy = 21 + p["dy"]
    hx = staff_x(p, hy)
    sx, sy = cx + 3, 19 + p["dy"]
    ex = hx - 2
    for x in range(sx, ex + 1):                         # sleeve, 2 px thick, shaded underneath
        y = round(sy + (hy - sy) * (x - sx) / max(1, ex - sx))
        put(g, x, y, RM)
        put(g, x, y + 1, RD)
    for x in (hx - 1, hx):                              # fist gripping the staff
        put(g, x, hy, SL)
        put(g, x, hy + 1, SD)


def build_frame(p):
    g = new_grid(FRAME)
    draw_leg(g, *p["far"], p["far_boot"])   # far leg behind the robe
    draw_robe(g, p)
    draw_leg(g, *p["near"], WD)             # near leg in front of it
    draw_staff(g, p)
    draw_arm(g, p)
    draw_head(g, p)
    draw_hat(g, p)
    return add_outline(g, O)


SPEC = SpriteSpec(
    frame=FRAME, base_y=BASE_Y, palette=PALETTE, outline_index=O,
    anims=ANIMS, build_frame=build_frame, default_pose=DEFAULT_POSE,
)

if __name__ == "__main__":
    run(SPEC)
