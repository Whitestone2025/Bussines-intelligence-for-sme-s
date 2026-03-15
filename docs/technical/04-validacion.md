# Validation

## Minimum Validation By Change Type

### Docs only

- quick link review
- no broken references

### UI copy or view-model changes

```bash
python3 scripts/test_ui_workspace_flow.py
python3 scripts/test_business_os_e2e.py
```

### Discovery flow changes

```bash
python3 scripts/test_discovery_flow.py
python3 scripts/test_workspace_foundation.py
python3 scripts/test_intake_flow.py
```

### Strategy engine changes

```bash
python3 scripts/test_market_model.py
python3 scripts/test_pricing_financials.py
python3 scripts/test_decision_engine.py
python3 scripts/test_execution_planner.py
```

### Before showing the system

```bash
python3 scripts/release_check.py
```
