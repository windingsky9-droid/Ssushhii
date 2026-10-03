# Market Observatory

[![Market Observatory CI](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/ci.yml/badge.svg)](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/ci.yml)
[![Publisher Site CI](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/publisher-site-ci.yml/badge.svg)](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/publisher-site-ci.yml)
[![Repository Health](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/repo-health.yml/badge.svg)](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/repo-health.yml)
[![CodeQL](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/codeql.yml/badge.svg)](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/codeql.yml)
[![Live Site Smoke](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/live-site-smoke.yml/badge.svg)](https://github.com/windingsky9-droid/Ssushhii/actions/workflows/live-site-smoke.yml)

A zero-required-cost market research MVP built around a clean provider boundary. It runs immediately with deterministic demo data and switches to server-side Factor Weave research when `FACTORWEAVE_API_KEY` is configured.

## Why this exists

The goal is to validate whether people will use and pay for a clearer research workflow before spending money on infrastructure. It is a research product, not an auto-trader and not a promise of investment returns.

## Current MVP

- Premium responsive ticker-research dashboard.
- Deterministic demo mode with no account or API key required.
- Optional Factor Weave REST provider on the server.
- Composite profile, factor lens, market context, and comparable symbols.
- Free / Pro / Creator pricing presentation.
- Paid CTAs remain disabled until Stripe Payment Links are deliberately configured.
- Health and JSON research endpoints for deployment checks.

## Run locally — $0 path

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000`. The app automatically loads a SPY demo snapshot.

## Optional live Factor Weave mode

1. Copy `.env.example` to `.env`.
2. Put a Factor Weave API key in `FACTORWEAVE_API_KEY`.
3. Load that environment before starting the app.
4. Keep `.env` local; it is ignored by Git.

The browser never receives the Factor Weave credential. Provider requests are made by Flask on the server.

## Optional payments

Create hosted Stripe Payment Links only when you intentionally want to accept payments, then set `STRIPE_PRO_URL` and/or `STRIPE_CREATOR_URL`. Until those variables are present, the paid buttons remain disabled. This MVP does not collect card data or require a Stripe secret key.

See [`docs/REVENUE_SETUP.md`](docs/REVENUE_SETUP.md) for the end-to-end proof, live-provider, checkout, and first-revenue flow. `.env.example` documents the supported local variables; real credentials stay in `.env` or the deployment host's secret manager.

## Test and verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app.py src
```

## Hosted deployment

The repository includes a generic production entry point (`wsgi.py`), a `Procfile`, and a Dockerfile. Hosts that support Procfiles can use:

```text
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60 wsgi:app
```

For Docker-based hosting:

```powershell
docker build -t market-observatory .
docker run --rm -p 5000:5000 --env-file .env market-observatory
```

Keep `FACTORWEAVE_API_KEY`, `STRIPE_PRO_URL`, and `STRIPE_CREATOR_URL` in the host's secret/environment settings. Never bake `.env` into an image or commit it.

## Visual portfolio

The privacy-safe Sushir 3D Studio showcase is included under [`portfolio/`](portfolio/). Open `portfolio/index.html` locally or serve the folder from any static host. It includes a cinematic still, a synthetic public observatory demo, service positioning, and buyer-facing contact links. Private/name-specific source files are intentionally not included.


## Sushir Systems Lab

The repository also contains a separate static technical publisher under [`publisher-site/`](publisher-site/) with original engineering notes on APIs, demo architecture, WebGL performance, and remote AI workflows.

**Live:** https://sushir-systems-lab.netlify.app/

The publisher build includes:

- canonical URLs and per-page descriptions
- sitemap, robots.txt, manifest, favicon, and security contact
- CSP, clickjacking protection, permissions policy, and cache rules
- a dedicated Python validator
- GitHub Actions validation and a scheduled public smoke test

## Repository quality gates

Changes on the active development branch are checked through multiple independent workflows:

1. **Market Observatory CI** — installs the application, runs pytest, and compiles Python.
2. **Publisher Site CI** — validates static pages, links, metadata, assets, and secret-like patterns.
3. **Repository Health** — compile, tests, publisher validation, Ruff, and dependency audit.
4. **CodeQL** — Python and JavaScript/TypeScript security analysis.
5. **Live Site Smoke** — scheduled checks against the public publisher deployment and security headers.

See [`docs/WORKFLOW_MAP.md`](docs/WORKFLOW_MAP.md) for the full build-to-deploy path.
