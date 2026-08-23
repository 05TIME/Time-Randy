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

## Local development

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open `/airbnb`.

## Architecture

```text
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

Production deployment should move persistence from SQLite to PostgreSQL and place real provider credentials in environment/secret storage, never in Git.
