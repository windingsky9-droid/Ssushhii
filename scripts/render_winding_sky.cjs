#!/usr/bin/env node
'use strict';
// Renders the Winding Sky stills and seamless loops from the real-time scene in
// showcase/SUSHIR_WINDING_SKY_3D_RENDER.html into showcase/media/.
//
// Setup (once):  npm install --no-save playwright && npx playwright install chromium
// Stills:        node scripts/render_winding_sky.cjs
// With loops:    node scripts/render_winding_sky.cjs --loops [--no-stills] [--workers=N]
//
// Requires ffmpeg on PATH and network access (three.js from jsDelivr, fonts from Google Fonts).
// Rendering uses SwiftShader, so no GPU is needed; it already uses every CPU core, so extra
// workers only help on machines with many cores. Every frame is a pure function of time, so
// repeated runs reproduce the same images.

const { chromium } = require('playwright');
const { spawnSync } = require('child_process');
const fs = require('fs');
const http = require('http');
const os = require('os');
const path = require('path');

const SHOWCASE = path.resolve(__dirname, '..', 'showcase');
const PAGE = 'SUSHIR_WINDING_SKY_3D_RENDER.html';
const MEDIA = path.join(SHOWCASE, 'media');
const STILL_TIME = 3;
const CHROME_ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];

// `scale` supersamples the page; ffmpeg downsizes to `out` with a Lanczos filter.
const STILLS = [
  { file: 'sushir-winding-sky-hero.jpg', variant: 'hero', size: [1200, 450], scale: 3, out: [2400, 900] },
  { file: 'sushir-winding-sky-social.jpg', variant: 'social', size: [1280, 640], scale: 2, out: [1280, 640] },
  { file: 'sushir-winding-sky-4k.jpg', variant: 'clean', size: [1920, 800], scale: 3, out: [3840, 1600] },
];
const LOOPS = [
  {
    file: 'sushir-winding-sky-loop.mp4', variant: 'loop', size: [1920, 1080], fps: 30, grain: 0.012,
    codec: ['-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'],
  },
  {
    file: 'sushir-winding-sky-hero.webp', variant: 'hero', size: [1200, 450], fps: 20, grain: 0,
    codec: ['-c:v', 'libwebp_anim', '-quality', '74', '-compression_level', '6', '-loop', '0'],
  },
];

const args = process.argv.slice(2);
const withLoops = args.includes('--loops');
const withStills = !args.includes('--no-stills');
const workers = Math.max(1, parseInt((args.find((a) => a.startsWith('--workers=')) || '--workers=1').split('=')[1], 10) || 1);

function ffmpeg(ffArgs, input) {
  const result = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...ffArgs], { input, maxBuffer: 1 << 30 });
  if (result.error) throw new Error(`ffmpeg is required on PATH (${result.error.message})`);
  if (result.status !== 0) throw new Error(`ffmpeg failed: ${result.stderr.toString()}`);
}

function serve(dir) {
  const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.png': 'image/png' };
  const server = http.createServer((req, res) => {
    const file = path.join(dir, decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
    if (!file.startsWith(dir)) { res.writeHead(403); res.end(); return; }
    fs.readFile(file, (err, data) => {
      if (err) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream' });
      res.end(data);
    });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

async function openScene(base, { variant, size, scale = 1, grain }) {
  const browser = await chromium.launch({ args: CHROME_ARGS });
  const page = await browser.newPage({ viewport: { width: size[0], height: size[1] }, deviceScaleFactor: scale });
  const errors = [];
  page.on('pageerror', (err) => errors.push(err.message));
  const query = new URLSearchParams({ capture: '1', variant });
  if (grain !== undefined) query.set('grain', String(grain));
  await page.goto(`${base}/${PAGE}?${query}`, { waitUntil: 'networkidle', timeout: 120000 });
  await page.evaluate(() => window.__sceneReady);
  if (errors.length) throw new Error(`Scene failed to load: ${errors.join('; ')}`);
  return { browser, page };
}

async function renderStill(base, spec) {
  const { browser, page } = await openScene(base, spec);
  await page.evaluate((t) => window.renderAt(t), STILL_TIME);
  // Software rendering of a supersampled frame can take a while, so no screenshot timeout.
  const png = await page.screenshot({ type: 'png', timeout: 0 });
  await browser.close();
  const out = path.join(MEDIA, spec.file);
  ffmpeg(['-f', 'image2pipe', '-i', '-', '-vf', `scale=${spec.out[0]}:${spec.out[1]}:flags=lanczos`, '-q:v', '2', '-pix_fmt', 'yuvj444p', out], png);
  console.log(`  ${spec.file}  ${spec.out.join('x')}  ${(fs.statSync(out).size / 1024).toFixed(0)} KB`);
}

async function renderLoop(base, spec) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'winding-sky-'));
  const scenes = await Promise.all(Array.from({ length: workers }, () => openScene(base, spec)));
  const seconds = await scenes[0].page.evaluate(() => window.LOOP_SECONDS);
  const frames = Math.round(seconds * spec.fps);
  let next = 0;
  let done = 0;
  await Promise.all(scenes.map(async ({ page }) => {
    while (next < frames) {
      const i = next++;
      await page.evaluate((t) => window.renderAt(t), i / spec.fps);
      await page.screenshot({ path: path.join(dir, `${String(i).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 95, timeout: 0 });
      done++;
      process.stdout.write(`\r  ${spec.file}: ${done}/${frames} frames`);
    }
  }));
  await Promise.all(scenes.map(({ browser }) => browser.close()));
  const out = path.join(MEDIA, spec.file);
  ffmpeg(['-framerate', String(spec.fps), '-i', path.join(dir, '%04d.jpg'), ...spec.codec, out]);
  fs.rmSync(dir, { recursive: true, force: true });
  console.log(`\r  ${spec.file}  ${spec.size.join('x')} @ ${spec.fps} fps, ${seconds}s loop  ${(fs.statSync(out).size / 1024 / 1024).toFixed(1)} MB`);
}

(async () => {
  fs.mkdirSync(MEDIA, { recursive: true });
  const server = await serve(SHOWCASE);
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    if (withStills) {
      console.log('Stills');
      for (const spec of STILLS) await renderStill(base, spec);
    }
    if (withLoops) {
      console.log(`Loops (${workers} workers)`);
      for (const spec of LOOPS) await renderLoop(base, spec);
    }
  } finally {
    server.close();
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
