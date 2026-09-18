# Revenue-ready setup

This project is prepared to test demand without pretending that synthetic research is live data or that any outcome is guaranteed.

## 1. Run the proof

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000`. Demo mode is intentionally useful with no account, payment method, or provider key.

## 2. Configure live research only when licensed

Copy `.env.example` to `.env` and set `FACTORWEAVE_API_KEY` only if the provider's current plan and commercial/data-redistribution terms cover the intended use. The key is loaded server-side and is never sent to browser JavaScript.

Keep demo mode available for sales calls. It makes the product easy to show and keeps a provider outage from breaking the first conversation.

## 3. Turn on paid checkout deliberately

Create hosted Stripe Payment Links in the owner's Stripe account. Test them in Stripe test mode first, then put only the public hosted URLs in:

```text
STRIPE_PRO_URL=https://buy.stripe.com/...
STRIPE_CREATOR_URL=https://buy.stripe.com/...
```

Do not put Stripe secret keys, card information, or customer data in `.env.example`, GitHub, issue forms, or browser code. The UI keeps paid controls disabled until a public link is present.

Before accepting money, publish plain-language scope, refund, and cancellation terms and confirm that the offer is a research tool—not personalized financial advice or an auto-trader.

## 4. Fastest first revenue loop

1. Use the observatory and the service cards as proof of capability.
2. Start with a tightly bounded API integration, dashboard, or 3D/AI prototype.
3. Send prospects to the GitHub service-request form with scope, stack, deadline, and documentation—not secrets.
4. Deliver a small result, collect a review, and raise price together with scope.
5. Track conversations, demos, trials, paid customers, and retained customers before adding accounts or infrastructure.

No code can guarantee profit. The setup is designed to shorten the distance between a credible demo and a paid, clearly scoped conversation.

## 5. Deployment handoff

The repository now includes `wsgi.py`, a Procfile, `requirements-production.txt`, and a Dockerfile. Deploy the demo first, set a health check to `/health`, and only then add live-provider or hosted-checkout environment variables. The `/health` endpoint should stay usable even if an upstream research provider is unavailable.
