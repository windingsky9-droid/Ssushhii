"""Render the configurator offscreen at high resolution, one PNG per configuration.

The page is driven through its own top-level bindings (cfg, cam, ENVS, PRODUCTS,
sync, loadCamera, setSpin) rather than through the UI, because clicking swatches
would be both slower and less precise — we want an exact, reproducible state per
frame.

Usage:  render_farm.py [limit] [css_side] [source.html]
        render_farm.py 0 1000        all configurations at 2000x2000
        render_farm.py 8 700         a quick eight-frame sample

Needs Playwright with Chromium. Set CHROME to override the browser binary.
"""
import asyncio, base64, json, pathlib, sys, tempfile, time
from playwright.async_api import async_playwright

SRC   = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (
    pathlib.Path(__file__).parents[2] / "products/3d-configurator-template/index.html")
OUT   = pathlib.Path(__file__).parent / "renders"
import os
# Software GL is fine here: the scene is a few thousand triangles, and a
# deterministic rasteriser beats a driver-dependent one for a reproducible set.
CHROME = os.environ.get("CHROME") or None

# Viewport CSS px; deviceScaleFactor doubles it. 1000 -> 2000x2000 canvas.
SIDE  = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 0   # 0 = no limit

# toDataURL reads the canvas backing store, not the screen, so the surrounding UI
# is irrelevant — only the canvas's own CSS box matters, because resize() derives
# the drawing-buffer size from clientWidth/clientHeight * dpr. Pinning the element
# to an exact square is both simpler and more reliable than fighting the grid.
def canvas_css(side):
    return (f"position:fixed;left:0;top:0;z-index:99999;"
            f"width:{side}px;height:{side}px;max-width:none;max-height:none")

# yaw/pitch/dist are DELTAS applied to each product's own default camera, so a
# product framed for a close hero shot stays framed at every angle.
# Each product's default camera was framed for a wide stage. On a square canvas
# the page's own `fit` factor pushes the camera back further still, so every
# product needs its own pull-in. Tuned by eye against a contact sheet: too tight
# clips the lamp's base and the headphone band, too loose wastes half the frame.
FRAME = {"headphones": 0.92, "bottle": 0.72, "lamp": 0.55,
         "table": 0.62, "speaker": 0.60}

ANGLES = [
    ("hero",    0.00,  0.00, 1.00),
    ("front",   0.62, -0.04, 1.02),
    ("high",   -0.28,  0.30, 1.06),
    ("profile", 1.15,  0.02, 1.05),
]


def rig(src: pathlib.Path) -> pathlib.Path:
    """Write a temporary copy of the configurator that exposes its internals.

    Everything the renderer owns - camera, current selection, lighting index -
    lives inside start(), so none of it is reachable from page.evaluate. Rather
    than put a debug hook in the file people buy, inject one into a throwaway
    copy at the single point where start() hands control to the draw loop.
    """
    html = src.read_text()
    # Leading newline disambiguates start()'s kick-off from the recursive call
    # inside frame(), which is indented four spaces.
    anchor = "\n  requestAnimationFrame(frame);\n"
    if html.count(anchor) != 1:
        raise SystemExit(f"{src}: expected exactly one render-loop kick-off, "
                         f"found {html.count(anchor)} - has start() been refactored?")
    hook = ("\n  window.__rig = { cfg, cam, ENVS, PRODUCTS, canvas,\n"
            "                   sync, loadCamera, setSpin };\n")
    out = pathlib.Path(tempfile.gettempdir()) / "render-rig.html"
    out.write_text(html.replace(anchor, hook + anchor))
    return out

async def main():
    OUT.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            **({"executable_path": CHROME} if CHROME else {}),
            args=["--use-gl=angle", "--use-angle=swiftshader",
                  "--enable-unsafe-swiftshader", "--disable-lcd-text"])
        page = await browser.new_page(
            viewport={"width": SIDE, "height": SIDE}, device_scale_factor=2)
        await page.goto(rig(SRC).as_uri())
        await page.wait_for_function("!!window.__rig")
        await page.evaluate("s => document.getElementById('c').style.cssText = s", canvas_css(SIDE))
        await page.evaluate("__rig.setSpin(false)")
        await page.wait_for_timeout(400)

        dims = await page.evaluate("[document.getElementById('c').width, document.getElementById('c').height]")
        print(f"canvas {dims[0]}x{dims[1]}", flush=True)

        # Build the shot list in the page, where PRODUCTS actually lives.
        shots = await page.evaluate("""() => {
          const out = [];
          for (const [pid, prod] of Object.entries(__rig.PRODUCTS)) {
            const groups = prod.groups;
            const lead   = groups[0];               // the primary colour group
            lead.items.forEach((item, li) => {
              // Vary the secondary groups deterministically as the lead colour
              // advances, so the set reads as a range rather than one product
              // recoloured N times.
              const sel = {};
              groups.forEach((g, gi) => {
                sel[g.key] = gi === 0 ? li : (li + gi) % g.items.length;
              });
              out.push({ pid, sel, name: prod.name, colour: item.name });
            });
          }
          return out;
        }""")

        combos = []
        for env_i, env in enumerate(await page.evaluate("__rig.ENVS.map(e => e.id)")):
            for s in shots:
                for a in ANGLES:
                    combos.append((s, env_i, env, a))
        # Interleave so a truncated run still covers every product and preset.
        combos.sort(key=lambda c: (ANGLES.index(c[3]), c[1], c[0]["pid"]))
        if LIMIT:
            combos = combos[:LIMIT]
        print(f"{len(combos)} renders queued", flush=True)

        t0 = time.time()
        manifest = []
        for n, (s, env_i, env_id, (aname, dy, dp, ds)) in enumerate(combos, 1):
            code = await page.evaluate("""([pid, sel, envi, dy, dp, ds, fr]) => {
              const R = window.__rig;
              R.cfg.product = pid;
              Object.assign(R.cfg.sel[pid], sel);
              R.cfg.env = envi;
              R.loadCamera(pid);
              R.cam.yaw += dy; R.cam.pitch += dp; R.cam.dist *= ds * fr;
              R.sync();
              return document.getElementById('sCode').textContent;
            }""", [s["pid"], s["sel"], env_i, dy, dp, ds, FRAME.get(s["pid"], 1.0)])
            # Three frames: the loop must run at least once after the state change,
            # and preserveDrawingBuffer keeps the last one readable.
            await page.evaluate("""() => new Promise(r => requestAnimationFrame(
                () => requestAnimationFrame(() => requestAnimationFrame(r))))""")
            data = await page.evaluate("document.getElementById('c').toDataURL('image/png')")
            fn = f"{s['pid']}_{code}_{env_id}_{aname}.png"
            (OUT / fn).write_bytes(base64.b64decode(data.split(",", 1)[1]))
            manifest.append({"file": fn, "product": s["pid"], "model": s["name"],
                             "colour": s["colour"], "code": code,
                             "lighting": env_id, "angle": aname})
            if n % 20 == 0 or n == len(combos):
                el = time.time() - t0
                print(f"  {n}/{len(combos)}  {el:.0f}s  ({el/n:.2f}s each)", flush=True)

        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
        await browser.close()
        print(f"done: {len(manifest)} files in {OUT}", flush=True)

asyncio.run(main())
