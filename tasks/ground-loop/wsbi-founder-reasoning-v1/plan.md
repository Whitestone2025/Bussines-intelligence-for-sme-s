---
project: Ws B-I
runId: wsbi-founder-reasoning-v1
commitPolicy: "no-commit"
qualityChecks:
  - python3 -m compileall scripts
  - python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/wsbi-founder-reasoning-v1/plan.md tasks/ground-loop/wsbi-founder-reasoning-v1/prd.json
  - python3 scripts/test_founder_bootstrap_flow.py
  - python3 scripts/test_discovery_flow.py
---

# Goal

Audit and upgrade the founder bootstrap flow and the agent reasoning logic so Ws B-I can start from either a clean repo bootstrap or a business folder that already contains company files, analyze available material before asking questions, preserve uncertainty, and avoid collapsing distinct companies into generic formulas.

## Story: S1 | Founder Prompt Surfaces

### Goal

Align every founder-facing prompt surface so the product clearly supports both clean-folder bootstrap and in-place business-folder bootstrap, while preserving the promise that Codex handles commands and opens the frontend when the case is ready.

### Deliverables

- README.md
- docs/founder/README.md
- docs/founder/02-trabajar-con-codex.md
- docs/founder/05-instalacion-limpia.md
- program.md
- scripts/serve_ui.py

### Acceptance

- Founder-facing docs describe both startup modes clearly.
- The recommended prompt explicitly supports "en esta carpeta esta toda la informacion de mi negocio".
- Empty-workspace onboarding copy no longer assumes only a clean-folder flow.
- The operator promise stays nontechnical and end-to-end.

### Checks

- python3 scripts/test_founder_bootstrap_flow.py

## Story: S2 | Analysis-First Founder Protocol

### Goal

Codify the rule that when business files already exist, Codex must inspect them first, summarize what it understood, and only then ask the minimum necessary questions.

### Deliverables

- program.md
- scripts/serve_ui.py
- scripts/intake.py

### Acceptance

- The operating program distinguishes clean bootstrap from in-place business-folder bootstrap.
- Onboarding copy and seed language emphasize file analysis before questions.
- Intake records can preserve the fact that existing business material was already present.

### Checks

- python3 scripts/test_founder_bootstrap_flow.py

## Story: S3 | Anti-Generic Reasoning Core

### Goal

Improve the inference layer so business-specific evidence drives findings, uncertainty is preserved, and sparse or contradictory inputs do not collapse into generic ICP, service, or channel formulas.

### Deliverables

- scripts/serve_ui.py
- scripts/customer_model.py

### Acceptance

- Findings carry clearer traceability to sources and evidence.
- Sparse inputs produce lower confidence and more validation pressure instead of generic defaults.
- Divergent business inputs can generate materially different findings.
- Reasoning distinguishes observation, inference, and validation state more cleanly.

### Checks

- python3 scripts/test_discovery_flow.py

## Story: S4 | Validation And Knowledge Assembly

### Goal

Tighten validation and knowledge assembly so the system asks fewer but better questions, preserves unresolved uncertainty, and promotes only sufficiently grounded knowledge into company, service, ICP, and channel records.

### Deliverables

- scripts/serve_ui.py

### Acceptance

- Validation questions are driven by blockers and confidence gaps, not by a fixed template alone.
- Knowledge records preserve unresolved questions where confidence is still thin.
- Readiness remains blocked when the system still lacks grounded context, even if guesses exist.

### Checks

- python3 scripts/test_discovery_flow.py

## Story: S5 | Founder And Reasoning Test Suite

### Goal

Expand the automated checks to cover both founder bootstrap modes and anti-generic reasoning behavior, including sparse-input caution and cross-company divergence.

### Deliverables

- scripts/test_founder_bootstrap_flow.py
- scripts/test_discovery_flow.py
- scripts/test_reasoning_quality.py

### Acceptance

- Tests cover clean-folder onboarding and in-place business-folder onboarding.
- Tests verify that generic defaults are not over-asserted under sparse evidence.
- Tests verify that distinct companies do not collapse into the same interpretation without support.

### Checks

- python3 scripts/test_founder_bootstrap_flow.py
- python3 scripts/test_discovery_flow.py
- python3 scripts/test_reasoning_quality.py

## Story: S6 | Final Verification Pass

### Goal

Run the full verification pass, review the modified surfaces, and leave the loop in a complete persisted state with no missing story.

### Deliverables

- tasks/ground-loop/wsbi-founder-reasoning-v1/progress.txt
- tasks/ground-loop/wsbi-founder-reasoning-v1/prd.json

### Acceptance

- All quality checks pass.
- Ground loop state reflects every completed story.
- The repo is ready for a founder to use the revised prompt and for future Codex iterations to continue from persisted state.

### Checks

- python3 -m compileall scripts
- python3 scripts/codex-ground-loop/build_prd.py tasks/ground-loop/wsbi-founder-reasoning-v1/plan.md tasks/ground-loop/wsbi-founder-reasoning-v1/prd.json
- python3 scripts/test_founder_bootstrap_flow.py
- python3 scripts/test_discovery_flow.py
- python3 scripts/test_reasoning_quality.py
- scripts/codex-ground-loop/ground-loop.sh tasks/ground-loop/wsbi-founder-reasoning-v1
