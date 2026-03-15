# How To Modify

## If You Change Business Logic

Touch the relevant engine:

- market: `scripts/market_model.py`
- pricing: `scripts/pricing.py`
- decision: `scripts/decision_engine.py`
- plan: `scripts/planner.py`
- deliverables: `scripts/render_report.py`

Then update the matching tests.

## If You Change UX Or Frontend Copy

Touch:

- `ui/index.html`
- `ui/app.js`
- `ui/styles.css`
- `scripts/serve_ui.py` if the view-model changes

## If You Change Contracts

Review:

- `schemas/`
- `data/tests/fixtures/`
- `scripts/test_schema_contracts.py`
- any e2e tests that depend on the changed shape

## If You Improve Founder Guidance

Update:

- [program.md](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/program.md)
- [docs/founder/README.md](/Users/pablomeneses/Documents/codex/Gta/InvestigaTRON%20copy/docs/founder/README.md)
- onboarding copy in the frontend if needed
