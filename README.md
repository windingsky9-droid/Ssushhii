# Ssushhii + Factor Weave Research Hub

This branch adds a safe Factor Weave integration scaffold without storing secrets in Git.

## What it does

- Reads Factor Weave market-factor data through the REST API.
- Provides a smoke test for ticker data and market context.
- Includes an MCP configuration template for MCP-aware clients.
- Keeps `fw_live_...` credentials outside the repository.
- Leaves room for dashboards, alerts, research reports, and paid products.

## Cost-aware starting point

- Factor Weave Free: $0, 250 API calls/day, REST access.
- Factor Weave Hobby: $19/month, 2,500 calls/day and MCP server access.
- Start on Free for development; upgrade only when MCP or higher limits are actually needed.

## Local setup

1. Create a Factor Weave dev key in Profile -> API Access.
2. Copy `.env.example` to `.env`.
3. Put the key in `.env`; never commit that file.
4. Install Python dependencies with `py -m pip install -r requirements.txt`.
5. Run `py scripts/smoke_test.py`.

## MCP setup

The Factor Weave MCP endpoint is:

`https://factorweave.com/api/mcp`

Factor Weave documents streamable HTTP transport and `Authorization: Bearer fw_live_...` authentication. The template is in `mcp/factorweave.template.json`.

MCP data tools require the Factor Weave Hobby tier or above. Public MCP initialization/tool discovery can still be probed without exposing a key.

## Revenue-oriented uses

Good product directions include a research dashboard, watchlist/report-card service, alert digest, educational market screener, or paid research newsletter. Treat Factor Weave as research infrastructure, not as a guaranteed return or auto-trading signal.

Before reselling or redistributing Factor Weave data, verify the provider's commercial/licensing terms.

See `docs/MONEY_STACK.md` for a low-cost build-and-sell plan.
