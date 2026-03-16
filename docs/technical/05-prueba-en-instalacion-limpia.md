# Clean Install Readiness

This document defines when Ws B-I is ready to test on another computer from a clean folder.

## Required Product Conditions

- empty-workspace onboarding must explain how a founder should start,
- the onboarding payload must include the GitHub repository URL,
- the founder prompt must explicitly support a clean-folder bootstrap,
- founder docs must explain the no-technical-install path,
- and Codex operating instructions must treat this as an end-to-end founder bootstrap request.

## Required Verification

Run:

```bash
python3 scripts/test_founder_bootstrap_flow.py
python3 scripts/test_ui_workspace_flow.py
python3 scripts/test_discovery_flow.py
python3 scripts/test_business_os_e2e.py
```

## Ready For Cross-Machine Trial

Ws B-I is ready for a clean-install trial on another computer when:

- the tests above pass,
- the repo has no leftover runtime research data,
- the published GitHub repository contains the founder and technical guides,
- and the startup prompt in the empty frontend points to the correct repository.
