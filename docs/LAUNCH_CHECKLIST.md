# Market Observatory Launch Checklist

Use this checklist in order. The principle is **prove demand before paying for scale**.

## 1. Product proof - free

- [ ] Run the full test suite locally and in CI.
- [ ] Open the dashboard at desktop and mobile widths.
- [ ] Search at least five tickers in demo mode.
- [ ] Confirm every demo result visibly says Demo data.
- [ ] Confirm invalid input produces a friendly error.
- [ ] Confirm no `.env`, API key, banking data, Cash App data, or browser credentials are tracked.

## 2. Live data - optional

- [ ] Review Factor Weave's current plan limits and commercial/data-redistribution terms.
- [ ] Create a dedicated development API key.
- [ ] Put the key only in local/deployment environment variables.
- [ ] Test live mode on a small ticker set and verify provider errors degrade safely.
- [ ] Keep demo mode available for sales demos and development.

## 3. First offer

- [ ] Pick one audience: active retail researchers, finance creators, or small research teams.
- [ ] Describe one paid outcome, not a giant feature list.
- [ ] Start with a simple monthly price test and change it based on conversations.
- [ ] Recruit 5-10 design partners before building accounts, databases, or automation.
- [ ] Record objections and requested workflows in GitHub issues.

## 4. Payments - only when ready to sell

- [ ] Create hosted checkout/payment links in the payment provider dashboard.
- [ ] Test sandbox/test mode before accepting live payments.
- [ ] Add only public hosted checkout URLs to `STRIPE_PRO_URL` / `STRIPE_CREATOR_URL`.
- [ ] Do not add raw card handling to this MVP.
- [ ] Publish refund/cancellation terms and a plain-language product description before charging.

## 5. Deployment - free tier first

- [ ] Choose a host that supports Python/Flask and environment variables.
- [ ] Add a health check pointing at `/health`.
- [ ] Deploy demo mode first and validate the public URL before adding provider credentials.
- [ ] Add a custom domain only after the product message is stable.
- [ ] Upgrade hosting only when actual traffic or revenue requires it.

## 6. Customer acquisition

- [ ] Build a 25-prospect list from public research before using paid enrichment credits.
- [ ] Send highly targeted, low-volume outreach instead of mass spam.
- [ ] Offer a short live demo and ask what would make the tool worth paying for.
- [ ] Publish useful ticker walkthroughs without making return promises.
- [ ] Track: conversations -> demos -> trials -> paid customers -> retained customers.

## Do not launch yet if

- Provider licensing for the intended commercial use is unclear.
- Checkout or cancellation terms are unclear.
- The site implies guaranteed returns, personalized advice, or auto-trading that it does not provide.
- A credential or personal financial detail appears anywhere in source control.
