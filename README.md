# TIMEŒ OS
Temporal Causality Engine + AI operating system.

## Current business units

### Airbnb Ops — Lekki Phase 1 2BR
The Airbnb unit is a first-class operational domain with:

- persistent booking and expense ledger
- occupancy and ADR calculations
- finance and debt controls
- turnover workflow primitives
- inventory and maintenance tracking
- occupancy forecasting
- advisory dynamic pricing
- escalation policies
- `/airbnb` dashboard
- `/airbnb/finance/snapshot` API

The system is provider-agnostic. It does not claim direct Airbnb API access and does not automatically change listing prices or send guest messages.

## Authentication and security

TIMEŒ API endpoints under `/timeoe/*` require a Supabase Auth access token in the request header:

```text
Authorization: Bearer <access-token>
```

The API verifies that token against Supabase Auth before reading or changing command/event data. It then authorizes the authenticated user against the requested business using either `businesses.owner_id` or a row in `memberships`.

The server uses `SUPABASE_SERVICE_ROLE_KEY` only for trusted server-side database access. It must never be exposed to browsers or committed to Git.

The public/publishable Supabase key used for token verification is configured as `SUPABASE_PUBLISHABLE_KEY`. Keep it separate from the service-role secret.

GitHub webhook requests to `/webhooks/github` are authenticated with `X-Hub-Signature-256` using `GITHUB_WEBHOOK_SECRET` and HMAC-SHA256. Invalid signatures are rejected.

Production secrets belong in the deployment platform's environment/secret store, not in source control.

## Local development

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open `/airbnb`.

## Architecture

```text
User / Client
      |
      | Supabase Auth JWT
      v
TIMEŒ Flask API
      |
      +--> authenticate JWT against Supabase Auth
      |
      +--> authorize business owner/member
      |
      +--> Supabase (service-role, server-side only)
      |
      +--> GitHub webhook (HMAC signature verification)
      |
      v
Commands / Tasks / Events

Chief of Staff
      |
   Lead Agent
      |
  Airbnb Ops Agent
  |   |   |   |   |
Booking Finance Turnover Inventory Maintenance
      |
 Risk / Escalation
      |
 Forecast + Pricing Intelligence
```
