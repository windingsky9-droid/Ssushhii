"""Render one hero per product at a trial framing factor and tile them for review."""
import asyncio, base64, io, json, pathlib, sys
from playwright.async_api import async_playwright
from PIL import Image

SP = pathlib.Path(__file__).parent
FACTORS = json.loads(sys.argv[1])          # {"bottle":0.62,...}
SIDE = 900

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
            args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width":SIDE,"height":SIDE}, device_scale_factor=1)
        await pg.goto((pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else SP.parents[2]/"products/3d-configurator-template/index.html").as_uri())
        await pg.wait_for_function("!!window.__rig")
        await pg.evaluate("s => document.getElementById('c').style.cssText = s",
            f"position:fixed;left:0;top:0;z-index:99999;width:{SIDE}px;height:{SIDE}px;max-width:none;max-height:none")
        await pg.evaluate("__rig.setSpin(false)")
        await pg.wait_for_timeout(400)
        tiles = []
        for pid, f in FACTORS.items():
            await pg.evaluate("""([pid, f]) => {
              const R = window.__rig;
              R.cfg.product = pid; R.cfg.env = 0;
              R.loadCamera(pid); R.cam.dist *= f; R.sync();
            }""", [pid, f])
            await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>requestAnimationFrame(r))))")
            d = await pg.evaluate("document.getElementById('c').toDataURL('image/png')")
            im = Image.open(io.BytesIO(base64.b64decode(d.split(",",1)[1]))).convert("RGB")
            tiles.append((pid, im))
        await b.close()
    w = tiles[0][1].width
    sheet = Image.new("RGB", (w*len(tiles), w))
    for i,(pid,im) in enumerate(tiles): sheet.paste(im, (i*w, 0))
    sheet.save(SP/"probe.png")
    print("probe.png", sheet.size, [t[0] for t in tiles])

asyncio.run(main())
