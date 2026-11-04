"""
Turn Duo Display stage renders into build-log visuals.

Inputs: stage1-hero.png ... stage6-hero.png (and optionally a convergence
ladder: ladder-spp0001-hero.png ...). Outputs, all in --out:

  stamped/stageN.png     each stage with a HUD label and progress bar
  build-log.mp4          crossfading timelapse of the six stages
  build-log.gif          the same, 640 px wide, for READMEs
  build-log-sheet.jpg    3 x 2 contact sheet
  before-after.jpg       blockout left, final right, split down the middle
  convergence.mp4/.gif   Cycles converging from 1 sample to the denoised final

Usage:
  python3 assemble_build_log.py --stages DIR [--ladder DIR] --out DIR \
      --title "SUSHIR x STUDIO" --font ChakraPetch-Bold.ttf --mono DejaVuSansMono.ttf
"""

import argparse
import glob
import os
import re
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

# Winding Sky palette.
VOID = (5, 7, 11)
ACID = (184, 255, 115)
CYAN = (111, 233, 255)
TEXT = (244, 248, 252)
MUTED = (147, 162, 179)
PANEL = (15, 22, 31, 205)
LINE = (224, 242, 255, 40)

STAGES = {
    1: ("Blockout", "Clay geometry and one key light. Proportions only."),
    2: ("Materials", "Metal, glass screens, emissive 3D type, grid floor."),
    3: ("Lighting", "Coloured spots, rim, fill and a top light."),
    4: ("Set dressing", "HUD brackets, wireframe cores, the team-up arc, dust."),
    5: ("Atmosphere", "Volumetric haze turns the spotlights into god rays."),
    6: ("Lens + grade", "Depth of field, AgX Punchy, bloom, streaks, dispersion."),
}
FPS = 25


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def spaced(draw, xy, text, fnt, fill, tracking):
    """Draw text with letter-spacing (Pillow has none built in)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def stamp(img, stage, total, readout, title, fonts):
    """Bottom-left glass label, top-right readout, segmented progress bar."""
    img = img.convert("RGBA")
    w, h = img.size
    s = w / 960.0
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)

    name, desc = STAGES[stage]
    f_eyebrow = font(fonts["sans"], int(11 * s))
    f_name = font(fonts["display"], int(30 * s))
    f_desc = font(fonts["sans"], int(13 * s))
    f_mono = font(fonts["mono"], int(11 * s))

    pad = int(18 * s)
    box_w, box_h = int(430 * s), int(104 * s)
    x0, y0 = pad, h - pad - box_h - int(14 * s)
    d.rounded_rectangle((x0, y0, x0 + box_w, y0 + box_h), radius=int(14 * s), fill=PANEL, outline=LINE, width=1)
    d.ellipse((x0 + int(16 * s), y0 + int(20 * s), x0 + int(23 * s), y0 + int(27 * s)), fill=ACID)
    spaced(d, (x0 + int(30 * s), y0 + int(16 * s)), f"STAGE {stage:02d} / {total:02d}", f_eyebrow, ACID, 2 * s)
    d.text((x0 + int(16 * s), y0 + int(34 * s)), name.upper(), font=f_name, fill=TEXT)
    d.text((x0 + int(16 * s), y0 + int(74 * s)), desc, font=f_desc, fill=MUTED)

    # Progress: one segment per stage.
    seg_gap = int(6 * s)
    bar_y = h - pad - int(6 * s)
    seg_w = (w - 2 * pad - seg_gap * (total - 1)) / total
    for i in range(total):
        sx = pad + i * (seg_w + seg_gap)
        col = ACID + (255,) if i < stage else (224, 242, 255, 46)
        d.rounded_rectangle((sx, bar_y, sx + seg_w, bar_y + int(4 * s)), radius=2, fill=col)

    # Top-right readout and top-left title.
    tw = d.textlength(readout, font=f_mono) + 2 * s * len(readout)
    spaced(d, (w - pad - tw, pad), readout, f_mono, CYAN, 2 * s)
    spaced(d, (pad, pad), title, f_mono, MUTED, 2 * s)
    return Image.alpha_composite(img, over).convert("RGB")


def stamp_ladder(img, spp, note, fonts):
    img = img.convert("RGBA")
    w, h = img.size
    s = w / 960.0
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    pad = int(18 * s)
    f_big = font(fonts["display"], int(44 * s))
    f_small = font(fonts["mono"], int(11 * s))
    box_w, box_h = int(300 * s), int(92 * s)
    x0, y0 = pad, h - pad - box_h
    d.rounded_rectangle((x0, y0, x0 + box_w, y0 + box_h), radius=int(14 * s), fill=PANEL, outline=LINE, width=1)
    d.text((x0 + int(16 * s), y0 + int(8 * s)), spp, font=f_big, fill=ACID)
    spaced(d, (x0 + int(18 * s), y0 + int(64 * s)), note, f_small, MUTED, 1.5 * s)
    return Image.alpha_composite(img, over).convert("RGB")


def write_video(frames_dir, mp4, gif, gif_width=640, gif_fps=12):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(frames_dir, "f%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-movflags", "+faststart", mp4], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf",
                    f"fps={gif_fps},scale={gif_width}:-1:flags=lanczos,split[a][b];"
                    "[a]palettegen=max_colors=192:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a",
                    "-loop", "0", gif], check=True)


def sequence(images, frames_dir, hold_s, fade_s):
    """Write a frame sequence: hold each image, crossfade into the next."""
    if os.path.isdir(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    n = 0
    hold, fade = int(hold_s * FPS), int(fade_s * FPS)
    for i, im in enumerate(images):
        first = os.path.join(frames_dir, f"f{n:05d}.png")
        im.save(first)
        n += 1
        for _ in range(hold - 1):
            os.link(first, os.path.join(frames_dir, f"f{n:05d}.png"))
            n += 1
        if i + 1 < len(images) and fade > 0:
            for k in range(1, fade + 1):
                Image.blend(im, images[i + 1], k / (fade + 1)).save(os.path.join(frames_dir, f"f{n:05d}.png"))
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", required=True)
    ap.add_argument("--ladder", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="DUO DISPLAY")
    ap.add_argument("--samples", default="32 SPP")
    ap.add_argument("--font", required=True, help="display face for stage names")
    ap.add_argument("--sans", default="", help="face for small labels (defaults to --font)")
    ap.add_argument("--mono", required=True)
    ap.add_argument("--gif-width", type=int, default=640)
    ap.add_argument("--gif-fps", type=int, default=12)
    a = ap.parse_args()
    fonts = {"display": a.font, "sans": a.sans or a.font, "mono": a.mono}
    os.makedirs(os.path.join(a.out, "stamped"), exist_ok=True)

    stage_files = sorted(glob.glob(os.path.join(a.stages, "stage*-hero.png")))
    stages = []
    for path in stage_files:
        st = int(re.search(r"stage(\d)", os.path.basename(path)).group(1))
        img = stamp(Image.open(path), st, 6, f"BLENDER 4.2 · CYCLES · {a.samples}", a.title, fonts)
        img.save(os.path.join(a.out, "stamped", f"stage{st}.png"))
        stages.append(img)
    print(f"stamped {len(stages)} stages")

    if len(stages) >= 2:
        n = sequence(stages, os.path.join(a.out, "_frames"), hold_s=1.5, fade_s=0.6)
        write_video(os.path.join(a.out, "_frames"), os.path.join(a.out, "build-log.mp4"),
                    os.path.join(a.out, "build-log.gif"), a.gif_width, a.gif_fps)
        shutil.rmtree(os.path.join(a.out, "_frames"))
        print(f"build-log: {n} frames")

        # Contact sheet, 3 x 2.
        tw, th, g = 640, 360, 14
        cols = 3
        rows = (len(stages) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * g, rows * th + (rows + 1) * g), VOID)
        for i, im in enumerate(stages):
            r, c = divmod(i, cols)
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (g + c * (tw + g), g + r * (th + g)))
        sheet.save(os.path.join(a.out, "build-log-sheet.jpg"), quality=90)

        # Before / after split.
        raw_first = Image.open(stage_files[0]).convert("RGB")
        raw_last = Image.open(stage_files[-1]).convert("RGB")
        w, h = raw_last.size
        ba = raw_last.copy()
        ba.paste(raw_first.crop((0, 0, w // 2, h)), (0, 0))
        d = ImageDraw.Draw(ba)
        d.rectangle((w // 2 - 1, 0, w // 2 + 1, h), fill=ACID)
        f = font(fonts["mono"], 13)
        spaced(d, (18, 18), "STAGE 01 · BLOCKOUT", f, TEXT, 2)
        label = "STAGE 06 · FINAL"
        spaced(d, (w - 18 - d.textlength(label, font=f) - 2 * len(label), 18), label, f, ACID, 2)
        ba.save(os.path.join(a.out, "before-after.jpg"), quality=92)

    if a.ladder:
        ladder_files = sorted(glob.glob(os.path.join(a.ladder, "ladder-spp*-hero.png")))
        frames = []
        for path in ladder_files:
            spp = int(re.search(r"spp(\d+)", path).group(1))
            frames.append(stamp_ladder(Image.open(path), f"{spp} SPP", "PATH TRACING · NO DENOISER", fonts))
        if stage_files:
            frames.append(stamp_ladder(Image.open(stage_files[-1]), "FINAL", "32 SPP · OIDN DENOISED · GRADED", fonts))
        for i, im in enumerate(frames):
            im.save(os.path.join(a.out, "stamped", f"ladder{i:02d}.png"))
        n = sequence(frames, os.path.join(a.out, "_frames"), hold_s=0.9, fade_s=0.0)
        write_video(os.path.join(a.out, "_frames"), os.path.join(a.out, "convergence.mp4"),
                    os.path.join(a.out, "convergence.gif"), a.gif_width, a.gif_fps)
        shutil.rmtree(os.path.join(a.out, "_frames"))
        print(f"convergence: {len(frames)} steps")

    for name in sorted(os.listdir(a.out)):
        p = os.path.join(a.out, name)
        if os.path.isfile(p):
            print(f"  {name}  {os.path.getsize(p) // 1024} KB")


if __name__ == "__main__":
    main()
