# Architecture

Ws B-I is a local, repo-backed business intelligence system.

## Main Layers

### Workspace layer

- repo-backed storage under `data/`
- workspace helpers in `scripts/workspace.py`
- local UI serving in `scripts/serve_ui.py`

### Research layer

- intake in `scripts/intake.py`
- evidence ingestion in `scripts/evidence_ingest.py`
- raw-to-normalized material in `data/sources`, `data/evidence`, and `data/corpus`

### Intelligence layer

- market in `scripts/market_model.py`
- competitors in `scripts/competitors.py`
- customer and offer in `scripts/customer_model.py`
- pricing and financials in `scripts/pricing.py` and `scripts/financials.py`
- decision and planning in `scripts/decision_engine.py` and `scripts/planner.py`

### Delivery layer

- deliverables in `scripts/render_report.py`
- tabular outputs in `scripts/render_tables.py`
- frontend rendering in `ui/`

## Core Runtime Flow

1. seed a business,
2. add sources,
3. add evidence,
4. infer findings and validation needs,
5. build market, pricing, decision, and plan outputs,
6. generate deliverables,
7. review in frontend.

## Main Data Areas

- `data/reference/`: static references
- `data/tests/fixtures/`: deterministic test fixtures
- generated runtime state under the rest of `data/`
