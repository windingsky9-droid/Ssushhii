# Market Observatory MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a zero-cost local market-research MVP that works in demo mode, can switch to Factor Weave server-side, and exposes safe subscription links only when configured.

**Architecture:** Flask serves a single responsive dashboard plus JSON research/config endpoints. A provider boundary isolates deterministic demo data from authenticated Factor Weave data, with checkout URLs read only from environment variables.

**Tech Stack:** Python 3.13, Flask, requests, python-dotenv, pytest, vanilla HTML/CSS/JavaScript.

**Spec:** `docs/superpowers/specs/2026-08-31-market-observatory-mvp-design.md`

## Global Constraints
- Local development must require $0 paid services.
- API keys stay server-side and out of source control.
- Missing Factor Weave credentials selects demo mode.
- Missing checkout URLs disables purchase CTAs safely.
- No automated trading or guaranteed-return claims.

---

### Task 1: Research domain and provider selection

**Files:**
- Create: `tests/test_research.py`
- Create: `src/research.py`
- Modify: `requirements.txt`

**Interfaces:**
- Produces: `normalize_ticker(value: str) -> str`, `DemoResearchProvider.research(ticker: str) -> dict`, `get_research_provider() -> ResearchProvider`.
- [ ] **Step 1: Write failing tests** for uppercase normalization, rejected ticker characters, deterministic demo output, and demo provider selection without a key.
- [ ] **Step 2: Run tests and verify RED** with `py -m pytest tests/test_research.py -q`.
- [ ] **Step 3: Implement minimal provider/domain code** in `src/research.py`; wrap `FactorWeaveClient` only when `FACTORWEAVE_API_KEY` exists.
- [ ] **Step 4: Run tests and verify GREEN**.
- [ ] **Step 5: Commit** `feat: add research provider domain`.

### Task 2: Flask API and safe monetization config

**Files:**
- Create: `tests/test_app.py`
- Create: `app.py`
- Create: `src/pricing.py`

**Interfaces:**
- Consumes: `get_research_provider`, `normalize_ticker`.
- Produces: Flask `create_app()`; `GET /api/research?ticker=...`; `GET /api/config`; `GET /health`.

- [ ] **Step 1: Write failing endpoint tests** for success, invalid ticker, provider failure, health, and disabled checkout URLs.
- [ ] **Step 2: Run tests and verify RED** with `py -m pytest tests/test_app.py -q`.
- [ ] **Step 3: Implement minimal Flask app and pricing config** with no secret data in JSON responses.
- [ ] **Step 4: Run endpoint tests and full suite GREEN**.
- [ ] **Step 5: Commit** `feat: add market observatory api`.

### Task 3: Conversion-oriented dashboard

**Files:**
- Create: `templates/index.html`
- Create: `static/app.js`
- Create: `static/styles.css`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: `/api/research`, `/api/config`.
- Produces: responsive search/results/pricing page with explicit Demo/Live source label.
- [ ] **Step 1: Extend failing render test** to require the product headline, search control, source badge hook, pricing section, and risk disclaimer.
- [ ] **Step 2: Run render test and verify RED**.
- [ ] **Step 3: Implement HTML/CSS/JS** with no client-side API keys, credible empty/loading/error states, and disabled CTAs unless configured.
- [ ] **Step 4: Run full test suite GREEN** and request the local page with Flask test client.
- [ ] **Step 5: Commit** `feat: add conversion dashboard`.

### Task 4: Operator docs and zero-cost verification

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Create: `docs/LAUNCH_CHECKLIST.md`

**Interfaces:**
- Documents: local demo launch, optional Factor Weave key, optional Stripe links, free deployment path, and outreach prerequisites.

- [ ] **Step 1: Update environment template** without real credentials.
- [ ] **Step 2: Document one-command local run and verification commands**.
- [ ] **Step 3: Add launch checklist** covering payments, provider licensing, privacy/terms, deployment, and first-customer outreach.
- [ ] **Step 4: Run `py -m pytest -q` and Python compile checks**.
- [ ] **Step 5: Confirm `git status` contains no `.env`, credential, bank, or payment data**.
- [ ] **Step 6: Commit** `docs: add market observatory launch guide`.
