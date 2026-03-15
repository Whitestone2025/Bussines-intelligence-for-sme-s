# Codex UI War Room V1

## Vision

Codex Business OS needs a new interface that feels like an executive war room, not a repo browser. The user should be able to open one business case, understand the thesis, inspect the evidence, challenge the recommendation, and review deliverables without touching raw JSON unless they intentionally switch to audit mode.

## Product Outcome

Replace the current interface with a single-company, Spanish-first review experience built around two modes:

- `War Room`: understand and decide
- `Auditoria`: inspect all underlying evidence and artifacts

The Preview is the flagship case and must read like a premium strategy engagement from first load.

## User Experience Principles

- One active company at a time.
- Executive reading first, artifact inspection second.
- Curated synthesis must outrank automatic extraction noise.
- Visual hierarchy should make the core recommendation obvious in seconds.
- Every conclusion should remain traceable to evidence.
- Deliverables should feel like premium working documents inside the app.

## Information Architecture

### Executive mode

- War Room
- Tesis
- Mercado
- Cliente y oferta
- Competencia
- Pricing y viabilidad
- Decision
- Plan
- Entregables

### Audit mode

- Auditoria

## Interface Requirements

### War Room

Must show:

- company identity and website
- executive recommendation
- decision rationale
- readiness
- top pains, objections, trust signals
- principal risks
- immediate next steps
- featured deliverables

### Tesis

Must show:

- service statement
- offer statement
- ICP
- buying triggers
- messaging
- proof points

### Mercado

Must show:

- TAM, SAM, SOM
- attractiveness score
- sizing methodology summary
- explicit assumptions

### Cliente y oferta

Must show:

- pains
- desired outcomes
- objections
- trust signals
- mechanism
- proof points
- objection handling

### Competencia

Must show:

- direct competitors
- substitutes
- incumbent risk
- whitespace
- why we win / why we lose

### Pricing y viabilidad

Must show:

- floor, target, ceiling
- tier summaries
- LTV, CAC, payback, break-even
- viability flags

### Decision

Must show:

- decision memo
- alternatives
- risks
- next steps

### Plan

Must show:

- 30/60/90 execution milestones
- metrics or outcomes per milestone

### Entregables

Must show:

- premium in-app reader
- clear document navigation
- summaries and full content

### Auditoria

Must show:

- source list
- evidence list
- findings list
- validation queue
- paths and counts
- traceability hints by section

## Backend Contract

`/api/case` must become a UI-first view-model endpoint. It must continue returning raw sections for compatibility, but it also needs the following top-level blocks:

- `hero`
- `war_room`
- `thesis`
- `market_summary`
- `competition_summary`
- `viability_summary`
- `decision_summary`
- `deliverable_index`
- `audit_index`

Each executive block should expose:

- `status`
- `confidence`
- `headline`
- `summary`
- `highlights`

## Quality Bar

The redesign is complete only when:

- The Preview opens in War Room by default.
- A human can understand what The Preview sells in under 10 minutes.
- Deliverables can be read in-app without friction.
- Audit mode exposes the full traceability path.
- No `undefined`, raw ids, or technical labels leak into executive mode.
- Desktop and mobile layouts both work.

## Validation

### Automated

- `python3 -m compileall scripts`
- `python3 scripts/test_ui_workspace_flow.py`
- `python3 scripts/test_business_os_e2e.py`
- `python3 scripts/test_case_view_model.py`

### Manual

- Browser walkthrough of War Room, Cliente y oferta, Decision, Entregables, and Auditoria
- Desktop and mobile snapshots for The Preview
- Review of labels, hierarchy, spacing, and traceability

## Non-goals

- Multi-company dashboard as primary experience
- Editing workflows in v1
- High-density BI dashboards
- Framework migration in this iteration

