---
project: Ws B-I
runId: ws-bi-v1
commitPolicy: "no-commit"
qualityChecks:
  - python3 -m compileall scripts
  - python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/ws-bi-v1/plan.md tasks/ground-loop/ws-bi-v1/prd.json
---

# Goal

Describe the business outcome this run is supposed to achieve.

## Story: S1 | Repo Foundation

### Goal

Set up the project foundation, repo structure, and core operating docs.

### Deliverables

- README.md
- program.md
- project directories

### Acceptance

- Repository structure exists.
- Ground loop artifacts exist.
- Project docs explain the system clearly.

### Checks

- python3 -m compileall scripts

## Story: S2 | Core Research Utilities

### Goal

Create lightweight utilities for corpus normalization, indexing, scoring, and reporting.

### Deliverables

- scripts/normalize.py
- scripts/build_index.py
- scripts/evaluate.py
- scripts/summarize_results.py

### Acceptance

- Scripts run with the standard library only.
- Scripts accept helpful CLI arguments.
- Outputs match the repo contracts.

### Checks

- python3 -m compileall scripts

## Story: S3 | Schemas And Templates

### Goal

Define stable formats for companies, ICPs, corpus entries, and evaluations.

### Deliverables

- schemas/
- templates/
- rubrics/

### Acceptance

- Key record shapes are documented.
- Templates are usable without extra explanation.

### Checks

- python3 -m compileall scripts

## Story: S4 | Pilot Workflow

### Goal

Prepare the repo so a first real company can be onboarded and an experiment can be run end-to-end.

### Deliverables

- example folders for data domains
- a repeatable operator workflow in README
- progress notes for next onboarding

### Acceptance

- A future run can add one company with minimal friction.
- The ground loop can continue from persisted state.

### Checks

  - scripts/codex-ground-loop/ground-loop.sh tasks/ground-loop/ws-bi-v1
