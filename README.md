# Market Observatory

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
- Factor Weave MCP probe/template retained for future agent workflows.

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

## Test and verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app.py src scripts
.\.venv\Scripts\python.exe scripts\mcp_probe.py
```

The MCP probe performs public initialization/tool discovery only; authenticated Factor Weave MCP data calls depend on your provider plan and key.
