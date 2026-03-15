# Setup And Commands

## Core Commands

Run the frontend:

```bash
python3 scripts/serve_ui.py
```

Run the release gate:

```bash
python3 scripts/release_check.py
```

Run the key product tests:

```bash
python3 scripts/test_discovery_flow.py
python3 scripts/test_ui_workspace_flow.py
python3 scripts/test_business_os_e2e.py
```

## Ground Loop

Build a PRD from a plan:

```bash
python3 scripts/codex-ground-loop/build_prd.py <plan.md> <prd.json>
```

Run the local loop:

```bash
scripts/codex-ground-loop/ground-loop.sh <run-dir>
```

## Autoresearch Loop

Initialize:

```bash
python3 scripts/codex-ground-loop/autoresearch_loop.py init <run-dir> --goal "Improve Ws B-I one bounded experiment at a time."
```

Generate the next brief:

```bash
python3 scripts/codex-ground-loop/autoresearch_loop.py next <run-dir>
```
