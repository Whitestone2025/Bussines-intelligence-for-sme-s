#!/usr/bin/env python3
"""Checks for pricing and financial viability."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from financials import build_financial_snapshot, persist_financial_snapshot
from pricing import build_pricing_model, persist_pricing_model


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "pricing-financials" / "founder-service.json").read_text(encoding="utf-8"))

    pricing_model = build_pricing_model(payload)
    assert pricing_model["price_floor"] > 0
    assert pricing_model["price_target"] >= pricing_model["price_floor"]
    assert pricing_model["price_ceiling"] >= pricing_model["price_target"]
    assert len(pricing_model["tier_summaries"]) == 3
    assert pricing_model["fact_base"], "Expected explicit pricing fact base"
    assert pricing_model["pricing_options"], "Expected pricing options"
    assert pricing_model["recommended_tier"] == "Base"
    assert pricing_model["recommendation_logic"], "Expected recommendation logic"
    assert pricing_model["implementation_risks"], "Expected implementation risks"
    assert pricing_model["fact_base"][0].startswith("Ancla de costo mensual"), "Pricing fact base should be in Spanish"

    snapshot = build_financial_snapshot(payload, pricing_model)
    assert snapshot["estimated_ltv"] > 0
    assert snapshot["gross_margin_ratio"] > 0
    assert snapshot["ltv_cac_ratio"] > 0
    if snapshot["viability_warning"]:
        assert "Low evidence" not in snapshot["viability_warning"]

    with TemporaryDirectory() as temp_dir:
        pricing_path = persist_pricing_model(Path(temp_dir), payload)
        assert pricing_path.exists()
        financial_path = persist_financial_snapshot(Path(temp_dir), payload, pricing_model)
        assert financial_path.exists()

    print("Pricing financial checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
