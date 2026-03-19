#!/usr/bin/env python3
"""Checks for the market discovery engine."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from market_model import build_market_models, persist_market_models


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "market" / "mexico-service.json").read_text(encoding="utf-8"))
    models = build_market_models(payload)
    assert len(models) == 4, "Expected TAM, SAM, SOM, and attractiveness outputs"

    tam = next(model for model in models if model["market_type"] == "tam")
    assert tam["top_down_value"] > 0
    assert tam["bottom_up_value"] > 0
    assert tam["blended_value"] > 0
    assert tam["fact_base"], "Expected explicit fact base"
    assert tam["key_assumptions"], "Expected explicit assumptions"
    assert tam["assumptions"] == tam["key_assumptions"], "Assumptions should remain traceable"
    assert tam["scenarios"], "Expected market scenarios"
    assert tam["recommended_entry_posture"], "Expected an entry posture recommendation"
    assert tam["implementation_risks"], "Expected implementation risks"
    assert tam["confidence"] > 0
    assert tam["fact_base"][0].startswith("Geografia analizada"), "Fact base should be in Spanish"
    assert tam["key_assumptions"][0].startswith("Se asume"), "Assumptions should be in Spanish"

    attractiveness = next(model for model in models if model["market_type"] == "attractiveness")
    assert attractiveness["blended_value"] <= 10
    assert "presion competitiva" in attractiveness["methodology_summary"].lower() or attractiveness["key_assumptions"]

    with TemporaryDirectory() as temp_dir:
        outputs = persist_market_models(Path(temp_dir), payload)
        assert len(outputs) == 4
        stored = json.loads(outputs[0].read_text(encoding="utf-8"))
        assert stored["market_model_id"]
        assert stored["company_id"] == payload["company_id"]

    print("Market model checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
