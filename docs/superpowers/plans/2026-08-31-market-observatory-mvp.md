# Market Observatory MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a polished zero-cost-to-run market-research MVP with demo data, optional live Factor Weave data, and payment-link-ready pricing.

**Architecture:** Flask serves a single responsive dashboard and JSON research endpoint. Provider classes isolate demo/live data, and all external credentials stay server-side in environment variables.

**Tech Stack:** Python 3.13, Flask, pytest, requests, HTML/CSS/vanilla JavaScript.

**Spec:** `docs/superpowers/specs/2026-08-31-market-observatory-mvp-design.md`

## Global Constraints
- Local development must work with no paid accounts or API keys.
- Demo and live data must always be visibly distinguished.
- No secrets in Git or browser JavaScript.
- No automatic trading or guaranteed-return language.
- Payment CTAs stay inert until explicit Stripe URLs are configured.

---

### Task 1: Research provider and service
**Files:** Create `src/research.py`; Test `tests/test_research.py`; Modify `requirements.txt`.
**Interfaces:** Produces `normalize_ticker()`, `DemoResearchProvider`, `FactorWeaveResearchProvider`, and `build_provider()`.
- [ ] Write tests for ticker validation, deterministic demo results, and provider selection.
- [ ] Run tests and verify RED because `src.research` does not exist.
- [ ] Implement the minimum provider/service behavior.
- [ ] Run the focused tests and verify GREEN.
- [ ] Commit the task.

### Task 2: Flask API and pricing safety
**Files:** Create `app.py`; Test `tests/test_app.py`; Modify `.env.example`, `requirements.txt`.
**Interfaces:** `create_app(provider=None)` returns the Flask app; `/api/research?ticker=...` returns normalized research JSON.
- [ ] Write failing tests for health, research success, invalid ticker, and disabled checkout links.
- [ ] Run the focused test and verify RED.
- [ ] Implement the application factory and routes.
- [ ] Run focused and full tests and verify GREEN.
- [ ] Commit the task.

### Task 3: Premium dashboard UI
**Files:** Create `templates/index.html`, `static/app.css`, `static/app.js`; Test `tests/test_ui.py`.
**Interfaces:** Browser calls `/api/research` and renders returned cards; upgrade anchors use server-provided payment URLs only.
- [ ] Write a failing rendering test for required product copy and source labeling hooks.
- [ ] Run test and verify RED.
- [ ] Implement responsive dashboard, search flow, pricing, trust copy, and error states.
- [ ] Run full tests and verify GREEN.
- [ ] Commit the task.

### Task 4: Demo readiness and documentation
**Files:** Modify `README.md`; Create `docs/LAUNCH_CHECKLIST.md`; Modify `.github/workflows/factorweave-smoke.yml`.
**Interfaces:** One documented local command starts the app; CI runs tests without secrets.
- [ ] Add a failing smoke assertion that `/` returns 200 and contains Market Observatory.
- [ ] Update dependencies, docs, and CI commands.
- [ ] Run all tests and compile checks.
- [ ] Run the app locally and request `/health` and `/api/research?ticker=SPY`.
- [ ] Commit the task.

### Task 5: Release verification
**Files:** No new production files unless verification finds a defect.
- [ ] Run `pytest -q`.
- [ ] Run `py -m compileall src app.py -q`.
- [ ] Verify `git status` contains no secrets or `.env` file.
- [ ] Review the diff for investment-return claims and payment links.
- [ ] Record blockers that require user login rather than bypassing them.
