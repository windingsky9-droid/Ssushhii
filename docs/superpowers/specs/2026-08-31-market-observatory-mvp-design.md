# Market Observatory MVP Design

## Goal
Build a polished, zero-required-cost market research web app that can run in demo mode immediately and switch to live Factor Weave data when a key is configured.

## Product
The working name is **Market Observatory**. A visitor enters a ticker and receives a compact research snapshot: factor metrics, risk/volatility context, market context, and comparable symbols when the provider exposes them.

The app must clearly label demo data versus live data and must never imply guaranteed returns or personalized investment advice.

## Revenue model
The first release is a lead-and-conversion MVP, not an automated trading product. It presents Free, Pro, and Creator/Research tiers; checkout buttons only become active when Stripe payment-link environment variables are configured.

This keeps development free while preserving a direct path to subscriptions once payments are intentionally activated.

## Architecture
A small Flask application serves one responsive dashboard and JSON endpoints. Business logic is isolated from HTTP rendering so it can be tested without network access.

A provider interface supplies research data. `DemoResearchProvider` returns deterministic, visibly labeled sample data; `FactorWeaveResearchProvider` wraps the existing Factor Weave client for authenticated live requests.

## User flow
1. Land on a premium-looking research dashboard.
2. Search a supported ticker.
3. See a summary card, factor/risk metrics, market context, and comparable symbols.
4. See clear source labeling: Demo or Live Factor Weave.
5. See a pricing section with disabled-safe upgrade links until payment URLs are configured.

## Error handling
Invalid tickers produce a friendly validation error. Provider/network failures return a research-unavailable state without exposing secrets or stack traces. Missing credentials automatically selects demo mode instead of breaking the site.

## Security and cost controls
- No API keys in source control or browser JavaScript.
- Live Factor Weave calls happen server-side only.
- Stripe is link-only at MVP stage; no custom card handling.
- No paid API or plugin action is required for local development.
- No automatic trading, order placement, or claims of guaranteed returns.

## Testing
Pytest covers ticker normalization, deterministic demo research, provider selection, research endpoint success, invalid input, and pricing/checkout safety. A local smoke test confirms the HTML dashboard renders.

## Success criteria
The app starts locally with one command, works without paid accounts, passes automated tests, looks credible enough to demo to prospects, and has a clear upgrade path to Factor Weave live data, Stripe, Supabase, Resend, deployment, and outreach.
