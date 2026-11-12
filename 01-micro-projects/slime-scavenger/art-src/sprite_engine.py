"""Reusable engine for procedural pixel-art sprites -> Godot 4.

A project's generate_sprite.py draws frames onto palette-index grids and hands this
engine a SpriteSpec. The engine owns everything that is the same for every character:
spritesheet, GIFs, 1x preview, silhouette test, SpriteFrames .tres and a validation
report (rules taken from the pixel-art-sprites skill: hard edges, small palette,
1 px outline, stable feet, real animation timing).

Grid convention: a (frame x frame) uint8 array of palette indices. 0 is transparent.
"""
import argparse
import os
import sys
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from PIL import Image, ImageSequence


@dataclass
class SpriteSpec:
    frame: int                       # square frame size, px
    base_y: int                      # row of the soles (feet baseline)
    palette: dict                    # {index: "#rrggbb"}; index 0 is reserved for transparent
    outline_index: int               # palette index used by add_outline()
    anims: list                      # [dict(name, fps, loop, poses=[pose dict, ...]), ...]
    build_frame: Callable            # pose dict -> finished grid (outline included)
    default_pose: dict = field(default_factory=dict)
    godot_sheet_path: str = "res://assets/characters/spritesheet.png"
    out_dir: str = field(default_factory=lambda: os.environ.get("OUT_DIR", "output"))
    sheet_cols: int = 6
    gif_scale: int = 8
    preview_scale: int = 6           # base resolution -> integer scale on screen
    preview_size: tuple = (320, 180)  # the game's base resolution
    bg_color: tuple = (31, 53, 38)   # previews only
    ground_color: tuple = (58, 42, 32)
    max_colors: int = 12             # skill guideline for characters: 8-12
    baseline_anims: tuple = ("idle", "run")   # feet must touch base_y in every frame
    locked_anims: tuple = ("idle",)           # feet locked, head/hat may drift at most 1 px
    first_stage: str = "idle"        # --stage <this> renders only that animation (approval gate)


# =============================== DRAWING HELPERS ===============================
def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def new_grid(frame):
    return np.zeros((frame, frame), np.uint8)


def put(g, x, y, c):
    """Set one pixel; silently ignores coordinates outside the frame."""
    h, w = g.shape
    if 0 <= x < w and 0 <= y < h:
        g[y, x] = c


def add_outline(g, outline_index):
    """1 px outline on transparent cells that touch the sprite (outside edge only)."""
    filled = g != 0
    pad = np.pad(filled, 1)
    near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    out = g.copy()
    out[(~filled) & near] = outline_index
    return out


# =============================== EXPORT ===============================
def to_rgba(g, palette):
    lut = np.zeros((max(palette) + 1, 4), np.uint8)
    for i, h in palette.items():
        lut[i] = (*hex_rgb(h), 255)
    return lut[g]


def build_sheet(spec, anim_frames):
    f = spec.frame
    sheet = np.zeros((len(anim_frames) * f, spec.sheet_cols * f, 4), np.uint8)
    for r, (_, frames) in enumerate(anim_frames):
        assert len(frames) <= spec.sheet_cols, "more frames than sheet_cols"
        for i, g in enumerate(frames):
            sheet[r * f:(r + 1) * f, i * f:(i + 1) * f] = to_rgba(g, spec.palette)
    return sheet


def save_gif(spec, path, grids, fps):
    f = spec.frame
    pal = [0, 0, 0]
    for i in range(1, max(spec.palette) + 1):
        pal += list(hex_rgb(spec.palette[i])) if i in spec.palette else [0, 0, 0]
    pal += [0] * (768 - len(pal))
    imgs = []
    for g in grids:
        im = Image.new("P", (f, f))
        im.putpalette(pal)
        im.putdata(g.flatten().tolist())
        imgs.append(im.resize((f * spec.gif_scale,) * 2, Image.NEAREST))
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=round(1000 / fps),
                 loop=0, transparency=0, disposal=2, optimize=False)


def build_preview(spec, anim_frames):
    """Base-resolution image (true 1x) so the sprite is judged at the size the player sees."""
    f = spec.frame
    img = Image.new("RGBA", spec.preview_size, spec.bg_color + (255,))
    for r, (_, frames) in enumerate(anim_frames):
        y0 = 4 + r * (f + 12)
        for i, g in enumerate(frames):
            x0 = 16 + i * (f + 8)
            ground = Image.new("RGBA", (f + 4, 3), spec.ground_color + (255,))
            img.paste(ground, (x0 - 2, y0 + spec.base_y + 1))
            spr = Image.fromarray(to_rgba(g, spec.palette))
            img.paste(spr, (x0, y0), spr)
    return img


def build_silhouette(spec, anim_frames, scale=4):
    sheet = build_sheet(spec, anim_frames)
    solid = np.zeros_like(sheet[..., :3])
    solid[sheet[..., 3] == 255] = (0, 0, 0)
    solid[sheet[..., 3] == 0] = (214, 214, 214)
    img = Image.fromarray(solid)
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


def write_tres(spec, path, anim_frames):
    f = spec.frame
    n_sub = sum(len(fr) for _, fr in anim_frames)
    lines = [f'[gd_resource type="SpriteFrames" load_steps={n_sub + 2} format=3]', "",
             f'[ext_resource type="Texture2D" path="{spec.godot_sheet_path}" id="1_sheet"]', ""]
    for r, (a, frames) in enumerate(anim_frames):
        for i in range(len(frames)):
            lines += [f'[sub_resource type="AtlasTexture" id="AtlasTexture_{a["name"]}_{i}"]',
                      'atlas = ExtResource("1_sheet")',
                      f"region = Rect2({i * f}, {r * f}, {f}, {f})", ""]
    blocks = []
    for a, frames in anim_frames:
        fr = ", ".join('{\n"duration": 1.0,\n"texture": SubResource("AtlasTexture_%s_%d")\n}'
                       % (a["name"], i) for i in range(len(frames)))
        blocks.append('{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %.1f\n}'
                      % (fr, "true" if a["loop"] else "false", a["name"], float(a["fps"])))
    lines += ["[resource]", "animations = [" + ", ".join(blocks) + "]", ""]
    with open(path, "w") as out:
        out.write("\n".join(lines))


# =============================== VALIDATION ===============================
def validate(spec, anim_frames, sheet, gif_paths):
    """Mechanical checks drawn from the skill's validations.md / sharp_edges.md. True if all pass."""
    f, o = spec.frame, spec.outline_index
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))

    alpha = sheet[..., 3]
    check("hard edges: alpha only 0/255 (no halos)", bool(np.isin(alpha, (0, 255)).all()))
    n_colors = len({tuple(c) for c in sheet[alpha == 255][:, :3]})
    check(f"palette <= {spec.max_colors} colours", n_colors <= spec.max_colors, f"{n_colors} colours")
    rows = len(anim_frames)
    check("sheet size, uniform frames", sheet.shape == (rows * f, spec.sheet_cols * f, 4),
          f"{sheet.shape[1]}x{sheet.shape[0]}")

    all_grids = [g for _, fr in anim_frames for g in fr]
    clipped = any(g[:, 0].any() or g[:, f - 1].any() or g[0, :].any() for g in all_grids)
    check("no pixel touches left/right/top frame edge", not clipped)

    def has_2x2_outline(g):
        m = g == o
        return bool((m[:-1, :-1] & m[1:, :-1] & m[:-1, 1:] & m[1:, 1:]).any())
    check("outline is 1 px (no 2x2 outline blocks)", not any(has_2x2_outline(g) for g in all_grids))

    for a, frames in anim_frames:
        if a["name"] in spec.baseline_anims:
            base = [int(np.where((g != 0) & (g != o))[0].max()) for g in frames]
            check(f"{a['name']}: feet on baseline row {spec.base_y}",
                  all(b == spec.base_y for b in base), str(base))
        if a["name"] in spec.locked_anims:
            band = slice(spec.base_y - 1, spec.base_y + 1)
            feet = [tuple(int(v) for v in np.where(g[band].any(axis=0))[0][[0, -1]]) for g in frames]
            check(f"{a['name']}: feet locked (same x-extent every frame)", len(set(feet)) == 1, str(feet))
            centres = []
            for g in frames:
                xs = np.where(((g != 0) & (g != o))[:f // 2 + 1].any(axis=0))[0]
                if xs.size:
                    centres.append((xs[0] + xs[-1]) / 2)
            drift = (max(centres) - min(centres)) if centres else 0
            check(f"{a['name']}: upper-body centre drift <= 1 px", drift <= 1, str([float(c) for c in centres]))

    for (a, frames), path in zip(anim_frames, gif_paths):
        with Image.open(path) as im:
            durs = [fr.info.get("duration") for fr in ImageSequence.Iterator(im)]
        want = round(1000 / a["fps"])
        check(f"{a['name']}.gif duration = {want} ms/frame ({a['fps']} fps)",
              all(d == want for d in durs) and len(durs) == len(frames), f"{durs}")
    return all(results)


# =============================== ENTRY POINT ===============================
def run(spec):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=[spec.first_stage, "all"], default="all")
    args = ap.parse_args()

    assert 0 not in spec.palette, "palette index 0 is reserved for transparent"
    os.makedirs(spec.out_dir, exist_ok=True)
    anims = [a for a in spec.anims if args.stage == "all" or a["name"] == spec.first_stage]
    anim_frames = [(a, [spec.build_frame({**spec.default_pose, **p}) for p in a["poses"]])
                   for a in anims]

    sheet = build_sheet(spec, anim_frames)
    Image.fromarray(sheet).save(os.path.join(spec.out_dir, "spritesheet.png"), optimize=True)
    gif_paths = []
    for a, frames in anim_frames:
        path = os.path.join(spec.out_dir, f"{a['name']}.gif")
        save_gif(spec, path, frames, a["fps"])
        gif_paths.append(path)
    preview = build_preview(spec, anim_frames)
    preview.save(os.path.join(spec.out_dir, "preview_1x.png"))
    preview.resize((preview.width * spec.preview_scale, preview.height * spec.preview_scale),
                   Image.NEAREST).save(os.path.join(spec.out_dir, f"preview_x{spec.preview_scale}.png"))
    build_silhouette(spec, anim_frames).save(os.path.join(spec.out_dir, "silhouette.png"))
    write_tres(spec, os.path.join(spec.out_dir, "character.tres"), anim_frames)

    print(f"Wrote {len(anim_frames)} animation(s) to {spec.out_dir}")
    ok = validate(spec, anim_frames, sheet, gif_paths)
    sys.exit(0 if ok else 1)
