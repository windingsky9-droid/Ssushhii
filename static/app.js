const $ = (id) => document.getElementById(id);
const form = $("research-form");
const input = $("ticker-input");
const statusEl = $("form-status");
const errorEl = $("research-error");

const signalScene = (() => {
  const canvas = $("signal-canvas");
  if (!canvas) return null;
  const ctx = canvas.getContext("2d");
  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  const state = {ticker: "SPY", score: 0, momentum: 0, regime: "BALANCED", posture: "AWAITING SNAPSHOT", phase: 0};
  const stars = Array.from({length: 150}, (_, index) => {
    const seed = (index * 9301 + 49297) % 233280 / 233280;
    return {x: seed * 2 - 1, y: ((seed * 7.31) % 1) * 2 - 1, z: .15 + ((seed * 13.17) % 1) * .85, size: 0.45 + ((seed * 5.7) % 1) * 1.7, tint: index % 7 === 0 ? "#b6f36b" : index % 5 === 0 ? "#75d7ff" : "#c9d6e3"};
  });

  let width = 1;
  let height = 1;
  let dpr = 1;
  let animationQueued = false;

  function resize() {
    const box = canvas.getBoundingClientRect();
    width = Math.max(1, box.width);
    height = Math.max(1, box.height);
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw(performance.now());
  }

  function rotate(point, ry, rx) {
    const cy = Math.cos(ry), sy = Math.sin(ry);
    const x = point.x * cy - point.z * sy;
    const z = point.x * sy + point.z * cy;
    const cx = Math.cos(rx), sx = Math.sin(rx);
    return {x, y: point.y * cx - z * sx, z: point.y * sx + z * cx};
  }

  function project(point, cx, cy, scale) {
    const depth = 3.6 / (3.6 - point.z);
    return {x: cx + point.x * scale * depth, y: cy + point.y * scale * depth, depth};
  }

  function glowDot(x, y, radius, color, alpha = 1) {
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius * 4.2);
    gradient.addColorStop(0, color.replace(")", `, ${alpha})`).replace("rgb", "rgba"));
    gradient.addColorStop(.22, color);
    gradient.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius * 4.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawOrbitalPath(cx, cy, scale, ry, rx, radius, color, alpha, phase) {
    ctx.beginPath();
    for (let i = 0; i <= 120; i += 1) {
      const angle = (i / 120) * Math.PI * 2 + phase;
      const point = rotate({x: Math.cos(angle) * radius, y: Math.sin(angle) * radius * .26, z: Math.sin(angle) * radius * .74}, ry, rx);
      const projected = project(point, cx, cy, scale);
      if (i === 0) ctx.moveTo(projected.x, projected.y);
      else ctx.lineTo(projected.x, projected.y);
    }
    ctx.strokeStyle = color;
    ctx.globalAlpha = alpha;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  function drawGlobe(cx, cy, scale, ry, rx) {
    ctx.save();
    ctx.globalAlpha = .7;
    for (let latitude = -2; latitude <= 2; latitude += 1) {
      const lat = latitude * .24;
      ctx.beginPath();
      for (let i = 0; i <= 64; i += 1) {
        const angle = (i / 64) * Math.PI * 2;
        const r = Math.cos(lat);
        const point = rotate({x: Math.cos(angle) * r, y: Math.sin(lat), z: Math.sin(angle) * r}, ry, rx);
        const projected = project(point, cx, cy, scale * .96);
        if (i === 0) ctx.moveTo(projected.x, projected.y);
        else ctx.lineTo(projected.x, projected.y);
      }
      ctx.strokeStyle = latitude === 0 ? "rgba(117,215,255,.55)" : "rgba(117,215,255,.18)";
      ctx.lineWidth = latitude === 0 ? 1.3 : .7;
      ctx.stroke();
    }
    for (let longitude = 0; longitude < 8; longitude += 1) {
      const lon = (longitude / 8) * Math.PI * 2;
      ctx.beginPath();
      for (let i = 0; i <= 64; i += 1) {
        const angle = (i / 64) * Math.PI * 2;
        const point = rotate({x: Math.cos(angle) * Math.cos(lon), y: Math.sin(angle), z: Math.cos(angle) * Math.sin(lon)}, ry, rx);
        const projected = project(point, cx, cy, scale * .96);
        if (i === 0) ctx.moveTo(projected.x, projected.y);
        else ctx.lineTo(projected.x, projected.y);
      }
      ctx.strokeStyle = longitude % 2 ? "rgba(182,243,107,.15)" : "rgba(166,141,255,.13)";
      ctx.lineWidth = .7;
      ctx.stroke();
    }
    ctx.restore();
  }

  function draw(time) {
    if (!ctx) return;
    state.phase = time * .00016;
    ctx.clearRect(0, 0, width, height);
    const cx = width * .5;
    const cy = height * .52;
    const scale = Math.min(width, height) * .28;
    const ry = state.phase * .7 + .48;
    const rx = .34 + Math.sin(state.phase * .8) * .035;

    const vignette = ctx.createRadialGradient(cx, cy, 0, cx, cy, scale * 2.6);
    vignette.addColorStop(0, "rgba(117,215,255,.08)");
    vignette.addColorStop(.45, "rgba(117,215,255,.018)");
    vignette.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, width, height);

    stars.forEach((star, index) => {
      const point = rotate({x: star.x * 2.35, y: star.y * 1.35, z: star.z * 2.4 - 1.2}, ry * .18, rx * .25);
      const projected = project(point, cx, cy, scale * .9);
      const twinkle = .36 + .28 * Math.sin(state.phase * 4 + index);
      ctx.globalAlpha = Math.max(.08, twinkle * (1.1 - star.z * .45));
      ctx.fillStyle = star.tint;
      ctx.beginPath();
      ctx.arc(projected.x, projected.y, star.size * (projected.depth * .4), 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1;

    drawOrbitalPath(cx, cy, scale, ry, rx, 1.42, "rgba(182,243,107,.36)", .9, 0);
    drawOrbitalPath(cx, cy, scale, ry + .7, rx + .12, 1.72, "rgba(117,215,255,.36)", .82, .8);
    drawOrbitalPath(cx, cy, scale, ry - .5, rx - .08, 1.98, "rgba(166,141,255,.2)", .72, 2.1);
    drawGlobe(cx, cy, scale, ry, rx);

    const coreGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, scale * .8);
    coreGlow.addColorStop(0, "rgba(182,243,107,.34)");
    coreGlow.addColorStop(.18, "rgba(117,215,255,.18)");
    coreGlow.addColorStop(1, "rgba(117,215,255,0)");
    ctx.fillStyle = coreGlow;
    ctx.beginPath();
    ctx.arc(cx, cy, scale * .8, 0, Math.PI * 2);
    ctx.fill();

    const count = 7 + Math.round(Math.max(0, Math.min(100, state.score)) / 13);
    for (let index = 0; index < count; index += 1) {
      const angle = state.phase * (1.2 + (index % 3) * .25) + index * (Math.PI * 2 / count);
      const radius = 1.18 + (index % 3) * .25;
      const point = rotate({x: Math.cos(angle) * radius, y: Math.sin(angle * 1.5) * .2, z: Math.sin(angle) * radius * .72}, ry, rx);
      const projected = project(point, cx, cy, scale);
      const color = index % 3 === 0 ? "#b6f36b" : index % 3 === 1 ? "#75d7ff" : "#a68dff";
      glowDot(projected.x, projected.y, 1.7 + (index % 2), color, .78);
    }

    ctx.strokeStyle = "rgba(182,243,107,.34)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx - scale * 1.32, cy);
    ctx.lineTo(cx + scale * 1.32, cy);
    ctx.moveTo(cx, cy - scale * 1.1);
    ctx.lineTo(cx, cy + scale * 1.1);
    ctx.stroke();

    if (!reducedMotion && !animationQueued) {
      animationQueued = true;
      requestAnimationFrame((nextTime) => {
        animationQueued = false;
        draw(nextTime);
      });
    }
  }

  function update(data) {
    state.ticker = printable(data.ticker, "SPY");
    state.score = Number(data.composite_score) || 0;
    state.momentum = Number(data.metrics?.momentum) || 0;
    state.regime = printable(data.market?.regime, "BALANCED").replaceAll("_", " ").toUpperCase();
    state.posture = printable(data.posture, "AWAITING SNAPSHOT").toUpperCase();
    $("scene-ticker").textContent = state.ticker;
    $("scene-posture").textContent = state.posture;
    $("scene-score").textContent = Math.round(state.score);
    $("scene-momentum").textContent = Math.round(state.momentum);
    $("scene-regime").textContent = state.regime;
    $("scene-state").textContent = data.source === "factorweave" ? "LIVE TELEMETRY" : "DEMO TELEMETRY";
    draw(performance.now());
  }

  window.addEventListener("resize", resize);
  resize();
  return {update};
})();

function printable(value, fallback = "—") {
  return value === null || value === undefined || value === "" ? fallback : value;
}

function pct(value) {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  return Number.isFinite(n) ? `${(n * 100).toFixed(1)}%` : "—";
}

function decimal(value) {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(2) : "—";
}

function renderResearch(data) {
  const score = Math.max(0, Math.min(100, Number(data.composite_score) || 0));
  $("result-title").textContent = `${data.ticker} / Research snapshot`;
  $("source-badge").textContent = data.source === "factorweave" ? "LIVE FACTOR WEAVE" : "DEMO DATA";
  $("composite-score").textContent = Math.round(score);
  $("score-meter").style.width = `${score}%`;
  $("posture").textContent = printable(data.posture);
  $("summary").textContent = printable(data.summary);
  $("as-of").textContent = printable(data.as_of);
  const metrics = data.metrics || {};
  $("metric-momentum").textContent = printable(metrics.momentum);
  $("metric-rsi").textContent = printable(metrics.rsi);
  $("metric-vol").textContent = pct(metrics.realized_vol);
  $("metric-beta").textContent = decimal(metrics.beta);

  const market = data.market || {};
  $("market-regime").textContent = printable(market.regime, "Market context").replaceAll("_", " ");
  $("market-note").textContent = printable(market.note || (market.vix ? `VIX context: ${market.vix}` : null), "Provider context available in the raw research response.");
  const peers = Array.isArray(data.comparables) ? data.comparables : [];
  $("comparables").innerHTML = "";
  (peers.length ? peers : ["No comparable profiles returned"]).forEach((peer) => {
    const chip = document.createElement("span");
    chip.textContent = peer;
    $("comparables").appendChild(chip);
  });
  signalScene?.update(data);
}

async function runResearch(ticker) {
  statusEl.className = "form-status loading";
  statusEl.textContent = `Researching ${ticker.toUpperCase()}…`;
  errorEl.hidden = true;
  try {
    const response = await fetch(`/api/research?ticker=${encodeURIComponent(ticker)}`);
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || "Research request failed.");
    renderResearch(body);
    statusEl.className = "form-status";
    statusEl.textContent = body.source === "factorweave" ? "Live provider research loaded." : "Demo snapshot loaded — configure Factor Weave for live provider data.";
  } catch (error) {
    statusEl.className = "form-status error";
    statusEl.textContent = error.message;
    errorEl.textContent = error.message;
    errorEl.hidden = false;
  }
}
async function loadPricing() {
  try {
    const response = await fetch("/api/config");
    if (!response.ok) return;
    const {plans = []} = await response.json();
    const cards = $("pricing-grid").querySelectorAll(".price-card");
    plans.forEach((plan, index) => {
      const card = cards[index];
      if (!card) return;
      const control = card.querySelector("button, a");
      if (plan.checkout_enabled && plan.checkout_url && plan.id !== "free") {
        const link = document.createElement("a");
        link.href = plan.checkout_url;
        link.rel = "noopener";
        link.textContent = `Choose ${plan.name}`;
        control.replaceWith(link);
      }
    });
  } catch (_) {
    // Pricing remains safely disabled if config cannot load.
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  runResearch(input.value);
});

document.addEventListener("DOMContentLoaded", () => {
  loadPricing();
  runResearch(input.value);
});
