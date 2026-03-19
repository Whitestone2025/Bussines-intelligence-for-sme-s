#!/usr/bin/env python3
"""Checks that the decision memo does not collapse into one tactical imperative."""

from __future__ import annotations

from decision_engine import build_decision_memo


def payload() -> dict:
    return {
        "company_id": "decision-collapse-check",
        "evidence_count": 8,
        "source_count": 4,
        "has_icp": True,
        "has_offer": True,
        "market_confidence": 0.76,
        "pricing_confidence": 0.69,
        "channel_confidence": 0.74,
        "business_goal": "mejorar la conversion de desarrolladoras boutique",
        "primary_channel": "Alianzas con brokers",
        "service_name": "Preventa visual para desarrolladoras boutique",
        "dominant_objection": "temen pagar produccion sin ver impacto comercial claro",
    }


def main() -> int:
    memo = build_decision_memo(payload())

    assert memo["decision_type"] == "go_to_market"
    assert 2 <= len(memo["options"]) <= 4, "Expected a small set of strategic routes"
    assert len(memo["alternative_actions"]) >= 2, "Expected real alternatives besides the recommended route"
    assert memo["recommended_action"] == memo["strategic_stack"]["recommended_route"]["thesis"]
    assert memo["why_now"] == memo["strategic_stack"]["recommended_route"]["why_this_route_wins"]
    assert memo["strategic_stack"]["recommended_route"]["invalidation_conditions"], "Expected explicit invalidation conditions"
    assert not memo["recommended_action"].lower().startswith("lanza "), "Recommendation should be a thesis, not a tactical command"
    assert any("ruta" in option["label"].lower() for option in memo["options"]), "Options should be strategic routes"

    print("No single-action collapse checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
