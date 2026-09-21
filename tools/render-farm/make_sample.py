"""Build the free ten-render sample: files, manifest, and its download page.

Run after render_farm.py. Writes into <portfolio>/renders/sample/ so the page
and its images sit together, exactly as they are served.
"""
import csv, json, pathlib, shutil, sys

REN  = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "renders"
OUT  = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else (
    pathlib.Path(__file__).parents[2] / "portfolio/renders/sample")

# Ten frames chosen to DESCRIBE the set, not flatter it: every product, every
# lighting preset, four different angles. The speaker appears twice on purpose,
# once with the grille off and once fitted — letting the picker take whichever
# matched first gave two grille-fitted frames, so the one genuinely new product
# showed up in the free sample as a featureless black box, twice.
WANT = [("headphones", "studio",   "hero",    None),
        ("bottle",     "sunset",   "hero",    None),
        ("lamp",       "showroom", "hero",    None),
        ("table",      "neon",     "hero",    None),
        ("speaker",    "studio",   "hero",    "-OFF"),
        ("speaker",    "showroom", "front",   "-ON"),
        ("headphones", "neon",     "profile", None),
        ("bottle",     "studio",   "high",    None),
        ("lamp",       "sunset",   "front",   None),
        ("table",      "showroom", "profile", None)]

LABEL = {"headphones": "Headphones", "bottle": "Cosmetic bottle",
         "lamp": "Table lamp", "table": "Side table", "speaker": "Bookshelf speaker"}

def main():
    man = json.loads((REN / "manifest.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    picked = []
    for pid, light, angle, code_contains in WANT:
        hit = next((r for r in man
                    if r["product"] == pid and r["lighting"] == light and r["angle"] == angle
                    and (code_contains is None or code_contains in r["code"])), None)
        if hit is None:
            raise SystemExit(f"make_sample: no render matches {pid} {light} {angle} {code_contains}")
        shutil.copy2(REN / hit["file"], OUT / hit["file"])
        picked.append(hit)

    cols = ["file", "product", "model", "colour", "code", "lighting", "angle"]
    with (OUT / "manifest-sample.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows([{k: r[k] for k in cols} for r in picked])

    (OUT / "index.html").write_text(page(picked))

    # Every image the page names must exist, or the sample ships broken links.
    named = {r["file"] for r in picked}
    on_disk = {p.name for p in OUT.glob("*.png")}
    assert named == on_disk, f"page/disk mismatch: {named ^ on_disk}"
    total = sum((OUT / r["file"]).stat().st_size for r in picked)
    print(f"{len(picked)} renders, {total/1e6:.1f} MB -> {OUT}")

def page(rows):
    cards = "\n".join(
        f'''    <figure>
      <a href="{r['file']}" download><img src="{r['file']}" alt="{LABEL[r['product']]} — {r['colour']}, {r['lighting']} lighting, {r['angle']} angle" loading="lazy" width="2000" height="2000"></a>
      <figcaption><b>{r['model']}</b><span>{r['colour']} · {r['lighting']} · {r['angle']}</span>
      <a class="dl" href="{r['file']}" download>Download PNG ↓</a></figcaption>
    </figure>''' for r in rows)
    return TEMPLATE.replace("{{CARDS}}", cards)

TEMPLATE = '''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Free sample — Studio Product Renders</title>
<meta name="description" content="Ten free full-resolution 2000x2000 product renders. All five products, all four lighting presets, four camera angles. Commercial use, no attribution.">
<link rel="canonical" href="https://sushir-saxon.upfling.site/renders/sample/index.html">
<style>
:root{--bg:#05070b;--fg:#e8eef7;--dim:#8b97a8;--line:#1a2331;--acc:#6fe9ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
header{padding:66px 0 34px;border-bottom:1px solid var(--line)}
h1{font-size:clamp(28px,4.6vw,44px);line-height:1.1;margin:0 0 14px;letter-spacing:-.02em}
p{color:var(--dim);max-width:65ch}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:18px;padding:34px 0}
figure{margin:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#070b11}
figure img{display:block;width:100%;height:auto;aspect-ratio:1}
figcaption{padding:12px 14px;border-top:1px solid var(--line);display:grid;gap:4px;font-size:13px}
figcaption span{color:var(--dim)}
.dl{color:var(--acc);text-decoration:none;font-weight:600;margin-top:4px}
section{padding:38px 0;border-top:1px solid var(--line)}
h2{font-size:22px;margin:0 0 12px}
ul{color:var(--dim);max-width:65ch;padding-left:20px}
ul b{color:var(--fg)}
a{color:var(--acc)}
footer{padding:34px 0 66px;color:var(--dim);font-size:14px;border-top:1px solid var(--line)}
</style>
<div class="wrap">
<header>
  <h1>Ten renders, free</h1>
  <p>Full resolution, 2000&thinsp;×&thinsp;2000 PNG. Chosen to describe the set
  rather than flatter it: all five products, all four lighting presets, four
  different camera angles. Click any image to download it.</p>
  <p>Commercial use, unlimited projects, no attribution. Don&rsquo;t resell them
  as a stock pack.</p>
</header>

<div class="grid">
{{CARDS}}
</div>

<section>
  <h2>Read this before you use them</h2>
  <ul>
    <li><b>No alpha channel.</b> Each one is a finished studio scene — backdrop,
      ground plane and contact shadow baked in. Not cut-outs.</li>
    <li><b>Not editable mockups.</b> No PSD, no smart object.</li>
    <li><b>Not real products.</b> ORBIT ONE, SERUM 30ML, ARC TABLE LAMP, FORM 62
      and MONITOR 5 are invented for this set.</li>
    <li><b>Not photorealistic.</b> Analytic lighting, not a captured HDR
      environment. It reads as a clean product render — which is the point.</li>
  </ul>
</section>

<section>
  <h2>The full set</h2>
  <p>480 renders: five products × six colourways × four lighting presets × four
  camera angles, all at this resolution. Every frame out of the same
  hand-written WebGL2 renderer, so the whole set matches.
  <a href="../index.html">Browse all thirty configurations →</a></p>
</section>

<footer>
  Sushir Saxon · <a href="../index.html">Render gallery</a> ·
  <a href="../../3d/index.html">Live configurator</a> ·
  <a href="../../index.html">Portfolio</a>
</footer>
</div>
</html>
'''

if __name__ == "__main__":
    main()
