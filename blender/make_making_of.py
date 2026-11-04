"""
Making-of video for the Duo Display. For each build stage, the prompt and the
code from duo_display.py that adds that stage type out on the left while the
render builds on the right. It ends on the final frame and also writes a
contact sheet of the six finished stages.

  python3 blender/make_making_of.py --stages blender/renders/stages \
      --final blender/renders/final/duo-display-hero.png \
      --out blender/renders/making-of/making-of.mp4 --title "SUSHIR × STUDIO"

Fonts default to Chakra Petch (bundled in fonts/) for the headings and a
system sans and monospace font for the prompt and code; pass --ui or --mono to
choose others. Needs Pillow and ffmpeg.
"""

import argparse
import os
import re
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
UI_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    os.path.join(HERE, "fonts", "ChakraPetch-SemiBold.ttf"),
]
MONO_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    r"C:\Windows\Fonts\consola.ttf",
]

W, H, FPS = 1280, 720, 25
VOID = (5, 7, 11)
INK = (11, 16, 23)
LINE = (38, 50, 64)
TEXT = (226, 233, 241)
MUTED = (147, 162, 179)
ACID = (184, 255, 115)
CYAN = (111, 233, 255)
VIOLET = (168, 145, 255)
MINT = (113, 239, 183)
GOLD = (255, 201, 121)

STAGES = [
    ("Blockout", "Clay geometry and one key light.",
     "Build two hex-pedestal display monoliths in Blender from Python, with extruded, bevelled names that share one letter height.",
     '''# Pedestal: stacked hex prisms with glowing seams
hex_prism("ped_base", 1.05, 0.22, (0, 0, 0.11), metal_dark, root, bevel=0.02)
hex_prism("ped_top", 0.92, 0.2, (0, 0, 0.345), metal, root, bevel=0.015)
cylinder("column", 0.11, 0.8, (0, 0.05, 0.86), metal, root)
# Panel: back plate, screen, glowing frame
box("backplate", (pw + 0.16, 0.12, ph + 0.16), (0, 0.06, pz), metal_dark, root)
box("screen", (pw, 0.02, ph), (0, -0.01, pz), screen, root)
# One scale fits both names, so they share a letter height
scale = fit_scale([left, right], font, 2.5, 0.62)
text_mesh("name", name, font, scale, 0.07, 0.012, 1.04, glow, side, root, (0, -0.075, pz + 0.12))'''),
    ("Materials", "Metal, glass screens, glowing 3D type.",
     "Give it real materials: brushed metal, dark glass screens with holographic scanlines, glowing type with metal sides, and a grid floor that fades with distance.",
     '''def mat_screen(name, color):
    """Dark glass screen with holographic scanlines."""
    k.inputs[1].default_value = 140.0       # scanline frequency
    sine.operation = "SINE"
    lines.inputs["From Min"].default_value = 0.82
    glass = nodes.new("ShaderNodeBsdfPrincipled")
    glass.inputs["Base Color"].default_value = (0.004, 0.005, 0.007, 1.0)
    glass.inputs["Coat Weight"].default_value = 1.0
    glass.inputs["Emission Color"].default_value = color
    links.new(total.outputs[0], glass.inputs["Emission Strength"])'''),
    ("Lighting", "Coloured spots, rim, fill and a top light.",
     "Light it like a stage: a coloured spotlight behind each display, a soft key, a warm fill and a cool rim.",
     '''spot = bpy.data.lights.new(f"{tag}_spot", type="SPOT")
spot.energy = 2200
spot.color = color[:3]
spot.spot_size = math.radians(38)
spot_obj.location = (0, 2.6, 6.2)
look_at(spot_obj, (0, -1.6, 0))

area("key", 420, 5.0, (-4.5, -7.0, 6.5), (0, 0, 1.6), (0.85, 0.9, 1.0))
area("fill", 160, 6.0, (5.5, -6.0, 2.0), (0, 0, 1.4), (1.0, 0.86, 0.75))
area("rim", 260, 9.0, (0, 6.0, 4.0), (0, 0, 2.0), (0.7, 0.75, 1.0))'''),
    ("Set dressing", "HUD, wireframe cores, the team-up arc, dust.",
     "Dress the set: HUD corner brackets, wireframe cores in orbit rings, a glowing arc linking the two players, light strips and dust.",
     '''core = mesh_object(f"{tag}_core", bm, glow, root)
wire = core.modifiers.new("wire", "WIREFRAME")
wire.thickness = 0.022
# Team-up link: an energy arc from core to core
spline = curve.splines.new("BEZIER")
spline.bezier_points.add(2)
for bp, co in zip(spline.bezier_points, (core_l, apex, core_r)):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = "AUTO"
for _ in range(420):                         # dust motes
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=at)'''),
    ("Atmosphere", "Volumetric haze turns spotlights into god rays.",
     "Add volumetric haze so the spotlights become god rays, without slowing the render to a crawl.",
     '''def mat_haze(name, density):
    vol = nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = density
    vol.inputs["Anisotropy"].default_value = 0.4  # god rays
    links.new(vol.outputs["Volume"], out.inputs["Volume"])

box("haze", (30, 26, 11), (0, 0.5, 5.4), mat_haze("haze", 0.009))
cy.volume_step_rate = 2.5         # bigger steps, faster
cy.volume_bounces = 0'''),
    ("Lens + grade", "Depth of field, AgX Punchy, bloom, streaks.",
     "Finish it like a film: depth of field, the AgX Punchy grade, bloom, anamorphic streaks and a touch of lens dispersion.",
     '''cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 3.2
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"
glare.glare_type = "BLOOM"
streaks.glare_type = "STREAKS"                # anamorphic flare
streaks.streaks = 2
lens.inputs["Dispersion"].default_value = 0.012
bpy.ops.render.render(write_still=True)'''),
]

STAGE_CHIPS = [[] for _ in range(6)]

TOKEN = re.compile(
    r'(?P<comment>#.*$)|(?P<string>"""[^"]*"""|"[^"]*"|\'[^\']*\')|'
    r'(?P<kw>\b(?:def|for|in|if|else|return|import|from|True|False|None|and|or|not)\b)|'
    r'(?P<call>\b[A-Za-z_][A-Za-z0-9_]*(?=\())|(?P<num>\b\d+(?:\.\d+)?\b)|(?P<other>.)'
)
COLORS = {"comment": MUTED, "string": MINT, "kw": VIOLET, "call": ACID, "num": CYAN, "other": TEXT}


def tokens(line):
    return [(m.lastgroup, m.group()) for m in TOKEN.finditer(line)]


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def wrap_code(code, maxc):
    out = []
    for line in code.split("\n"):
        indent = len(line) - len(line.lstrip())
        while len(line) > maxc:
            limit = maxc
            hash_at = line.find("#")
            if hash_at > indent:
                limit = min(limit, hash_at)
            cut = line.rfind(", ", 0, limit)
            if cut <= indent:
                break
            out.append(line[:cut + 1].rstrip())
            line = " " * (indent + 4) + line[cut + 1:].lstrip()
        out.append(line)
    return "\n".join(out)


def fit(img, w, h):
    return img.convert("RGB").resize((w, h), Image.LANCZOS)


def frame(stage_i, typed, render, fonts, title):
    im = Image.new("RGB", (W, H), VOID)
    d = ImageDraw.Draw(im)
    name, desc, prompt, code = STAGES[stage_i]

    # Header.
    d.text((24, 20), f"{title}  ·  MAKING OF", font=fonts["mono_s"], fill=MUTED)
    rt = "BLENDER 4.2  ·  CYCLES  ·  PYTHON"
    d.text((W - 24 - d.textlength(rt, font=fonts["mono_s"]), 20), rt, font=fonts["mono_s"], fill=CYAN)

    # Left: prompt + code.
    x0, y0, x1, y1 = 24, 56, 640, H - 24
    d.rounded_rectangle((x0, y0, x1, y1), radius=16, fill=INK, outline=LINE)
    d.ellipse((x0 + 18, y0 + 22, x0 + 25, y0 + 29), fill=ACID)
    d.text((x0 + 34, y0 + 17), f"PROMPT  ·  STAGE {stage_i + 1:02d}", font=fonts["mono_s"], fill=ACID)
    y = y0 + 44
    for ln in wrap(d, prompt, fonts["ui"], x1 - x0 - 40):
        d.text((x0 + 20, y), ln, font=fonts["ui"], fill=TEXT)
        y += 22
    y += 12
    d.line((x0 + 20, y, x1 - 20, y), fill=LINE)
    y += 14
    d.text((x0 + 20, y), "duo_display.py", font=fonts["mono_s"], fill=MUTED)
    y += 26

    remaining = typed
    cursor = None
    for n, line in enumerate(code.split("\n"), 1):
        if remaining < 0:
            break
        d.text((x0 + 16, y), f"{n:>2}", font=fonts["mono"], fill=(70, 84, 100))
        cx = x0 + 50
        shown = 0
        for kind, text in tokens(line):
            if shown >= remaining:
                break
            part = text[: max(0, remaining - shown)]
            d.text((cx, y), part, font=fonts["mono"], fill=COLORS[kind])
            cx += d.textlength(part, font=fonts["mono"])
            shown += len(text)
        cursor = (cx, y)
        remaining -= len(line) + 1
        y += 21
    if cursor and typed < len(code):
        d.rectangle((cursor[0] + 1, cursor[1] + 2, cursor[0] + 9, cursor[1] + 18), fill=ACID)

    # Right: render, stage name, progress.
    rx0, ry0 = 656, 56
    rw, rh = W - 24 - rx0, int((W - 24 - rx0) * 9 / 16)
    im.paste(fit(render, rw, rh), (rx0, ry0))
    d.rounded_rectangle((rx0, ry0, rx0 + rw, ry0 + rh), radius=12, outline=LINE)
    ty = ry0 + rh + 26
    d.text((rx0, ty), f"STAGE {stage_i + 1:02d} / {len(STAGES):02d}", font=fonts["mono_s"], fill=ACID)
    d.text((rx0, ty + 22), name.upper(), font=fonts["display"], fill=TEXT)
    d.text((rx0, ty + 72), desc, font=fonts["ui"], fill=MUTED)
    cx = rx0
    for chip in STAGE_CHIPS[stage_i]:
        tw = d.textlength(chip, font=fonts["mono_s"])
        d.rounded_rectangle((cx, ty + 110, cx + tw + 20, ty + 136), radius=13, outline=LINE, fill=INK)
        d.text((cx + 10, ty + 116), chip, font=fonts["mono_s"], fill=TEXT)
        cx += tw + 28
    seg_w, gap = (rw - 5 * 8) / 6, 8
    for i in range(6):
        sx = rx0 + i * (seg_w + gap)
        d.rounded_rectangle((sx, H - 40, sx + seg_w, H - 34), radius=3, fill=ACID if i <= stage_i else LINE)
    pct = typed / max(len(code), 1)
    d.text((rx0, H - 66), f"{'BUILDING' if pct < 1 else 'RENDERED'}  ·  {int(min(pct, 1) * 100):3d}%", font=fonts["mono_s"], fill=CYAN if pct < 1 else MINT)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", required=True)
    ap.add_argument("--final", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="DUO DISPLAY")
    ap.add_argument("--samples", type=int, default=32, help="samples the stage frames used")
    ap.add_argument("--times", default="", help="render seconds per stage, e.g. 12,13,15,33,74,71")
    ap.add_argument("--machine", default="", help="optional label, e.g. '4-CORE CPU'")
    ap.add_argument("--font", default=os.path.join(HERE, "fonts", "ChakraPetch-Bold.ttf"))
    ap.add_argument("--ui", default=next((f for f in UI_FONTS if os.path.isfile(f)), None))
    ap.add_argument("--mono", default=next((f for f in MONO_FONTS if os.path.isfile(f)), None))
    a = ap.parse_args()
    if not a.mono:
        ap.error("no monospace font found; pass --mono")
    fonts = {
        "display": ImageFont.truetype(a.font, 40),
        "ui": ImageFont.truetype(a.ui, 15),
        "mono": ImageFont.truetype(a.mono, 14),
        "mono_s": ImageFont.truetype(a.mono, 12),
    }
    global STAGES
    maxc = int((640 - 16 - (24 + 50)) // fonts["mono"].getlength("M"))
    STAGES = [(n, d, p, wrap_code(c, maxc)) for (n, d, p, c) in STAGES]
    longest = max(len(l) for st in STAGES for l in st[3].split("\n"))
    print(f"code panel fits {maxc} chars; longest line {longest}")

    renders = [Image.open(os.path.join(a.stages, f"stage{i}-hero.png")).convert("RGB") for i in range(1, 7)]
    times = [t for t in a.times.split(",") if t.strip()]
    for i in range(6):
        chips = [f"{renders[0].width}×{renders[0].height}", f"{a.samples} SPP"]
        if i < len(times):
            chips.append(f"{times[i].strip()} S RENDER")
        if a.machine:
            chips.append(a.machine.upper())
        STAGE_CHIPS[i] = chips
    blank = Image.new("RGB", renders[0].size, (8, 11, 16))
    ImageDraw.Draw(blank).text((40, 40), "EMPTY SCENE", font=fonts["mono_s"], fill=MUTED)

    tmp = a.out + "_frames"
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    n = 0

    def save(img):
        nonlocal n
        img.save(os.path.join(tmp, f"f{n:05d}.png"))
        n += 1

    type_frames, hold_frames = 62, 22
    lasts = []
    for s in range(6):
        code = STAGES[s][3]
        prev = renders[s - 1] if s else blank
        for f in range(type_frames):
            t = (f + 1) / type_frames
            typed = int(len(code) * t)
            save(frame(s, typed, Image.blend(prev, renders[s], min(1.0, t * 1.15)), fonts, a.title))
        last = frame(s, len(code), renders[s], fonts, a.title)
        lasts.append(last)
        for _ in range(hold_frames):
            save(last)

    src = Image.open(a.final).convert("RGB")
    final = src.resize((W, H), Image.LANCZOS)
    fd = ImageDraw.Draw(final)
    label = f"FINAL  ·  {src.width}×{src.height}  ·  CYCLES  ·  OIDN DENOISED  ·  AgX GRADED"
    lw = fd.textlength(label, font=fonts["mono_s"])
    fd.rounded_rectangle((24, H - 62, 24 + lw + 32, H - 24), radius=10, fill=INK, outline=LINE)
    fd.text((40, H - 51), label, font=fonts["mono_s"], fill=MINT)
    for f in range(75):
        t = min(1.0, f / 18)
        save(Image.blend(last, final, t))

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-movflags", "+faststart", a.out], check=True)
    shutil.rmtree(tmp)

    sheet = Image.new("RGB", (1920, 720), VOID)
    for i, img in enumerate(lasts):
        sheet.paste(img.resize((640, 360), Image.LANCZOS), ((i % 3) * 640, (i // 3) * 360))
    sheet_path = os.path.splitext(a.out)[0] + "-sheet.jpg"
    sheet.save(sheet_path, quality=88)
    print(f"wrote {sheet_path}")
    print(f"wrote {a.out}: {n} frames, {n / FPS:.1f} s, {os.path.getsize(a.out) // 1024} KB")


if __name__ == "__main__":
    main()
