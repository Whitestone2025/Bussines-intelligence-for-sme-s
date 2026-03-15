#!/usr/bin/env python3
"""Checks for deterministic deliverable generation."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from render_report import persist_bundle, render_bundle
from render_tables import render_tables


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))

    first = render_bundle(bundle)
    second = render_bundle(bundle)
    assert first == second, "Render output must be deterministic"
    assert "## Decision Question" in first["executive-memo"], "Executive memo should frame the decision explicitly"
    assert "## Current Thesis" in first["executive-memo"], "Executive memo should surface the current thesis"
    assert "## Key Assumptions" in first["executive-memo"], "Executive memo should expose assumptions"
    assert "## Options Considered" in first["executive-memo"], "Executive memo should compare options"
    assert "2026-03-14-founder-clarity" in first["executive-memo"], "Traceability should include evidence refs"
    assert "## What We Know" in first["business-diagnosis"], "Diagnosis should separate fact base"
    assert "## What We Infer" in first["business-diagnosis"], "Diagnosis should separate inference"
    assert "## What Still Needs Validation" in first["business-diagnosis"], "Diagnosis should show validation gaps"
    assert "## Execution Realities" in first["business-diagnosis"], "Diagnosis should stay implementation-aware"
    assert "Options Considered" in first["deck-outline"], "Deck should include strategic options"
    assert "## Contrary Evidence And Watchouts" in first["risk-memo"], "Risk memo should include contrary evidence"
    assert "## Risk Register" in first["risk-memo"], "Risk memo should include a risk register"

    tables = render_tables(bundle)
    assert "price_target" in tables["pricing-options.tsv"]
    assert "Sales clarity sprint first" in tables["decision-options.tsv"]
    assert "Annual price per customer assumed" in tables["assumption-register.tsv"]
    assert "Days 1-30" in tables["plan-milestones.tsv"]
    assert "Founder" in tables["plan-milestones.tsv"]

    with TemporaryDirectory() as temp_dir:
        outputs = persist_bundle(Path(temp_dir), bundle["company"]["company_id"], bundle)
        assert all(path.exists() for path in outputs.values())

    print("Deliverable generator checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
