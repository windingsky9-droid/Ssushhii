const $ = (id) => document.getElementById(id);
const form = $("research-form");
const input = $("ticker-input");
const statusEl = $("form-status");
const errorEl = $("research-error");

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
