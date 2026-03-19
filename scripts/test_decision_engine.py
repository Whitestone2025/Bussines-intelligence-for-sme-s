#!/usr/bin/env python3
"""Checks for the decision engine and readiness gate."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from decision_engine import build_decision_memo, persist_decision_memo, readiness_check


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "decisions" / "readiness.json").read_text(encoding="utf-8"))

    readiness = readiness_check(payload)
    assert readiness["status"] == "ready"
    assert readiness["score"] > 0.8

    memo = build_decision_memo(payload)
    assert memo["recommended_action"]
    assert memo["decision_type"] == "go_to_market"
    assert memo["decision_question"], "Expected explicit decision question"
    assert memo["decision_criteria"], "Expected visible decision criteria"
    assert memo["fact_base"], "Expected visible fact base"
    assert memo["assumptions"], "Expected explicit assumptions"
    assert memo["strategic_stack"], "Expected strategic stack"
    assert memo["strategic_stack"]["problem_statement"]["headline"], "Expected structured problem statement"
    assert memo["strategic_stack"]["strategic_alternatives"], "Expected strategic alternatives"
    assert memo["strategic_stack"]["what_must_be_true"], "Expected what-must-be-true conditions"
    assert 2 <= len(memo["strategic_stack"]["strategic_alternatives"]) <= 4, "Expected a bounded strategic option set"
    assert memo["strategic_stack"]["recommended_route"]["why_this_route_wins"], "Expected explicit route rationale"
    assert memo["strategic_stack"]["recommended_route"]["invalidation_conditions"], "Expected explicit invalidation conditions"
    assert memo["options"], "Expected option set"
    assert memo["validation_gaps"], "Expected validation gaps"
    assert memo["next_steps"]
    assert memo["decision_question"].startswith("Cual es"), "Expected decision question in Spanish"
    assert "Launch the first" not in json.dumps(memo, ensure_ascii=False)
    assert "Ruta de" in memo["options"][0]["label"], "Options should reflect strategic routes, not generic numbered actions"
    assert "lanza una primera prueba comercial" not in memo["recommended_action"].lower(), "Recommendation should not collapse to a single imperative action"

    blocked_payload = payload | {"evidence_count": 2, "has_offer": False}
    blocked = readiness_check(blocked_payload)
    assert blocked["status"] == "blocked"
    blocked_memo = build_decision_memo(blocked_payload)
    assert blocked_memo["status"] == "needs_validation"
    assert blocked_memo["strategic_stack"]["case_for_change"]["cost_of_inaction"], "Blocked decisions should still explain cost of inaction"
    assert blocked_memo["validation_gaps"], "Blocked decisions should surface validation gaps"
    assert blocked["blocking_reasons"][0].startswith("Agrega") or blocked["blocking_reasons"][0].startswith("Aclara"), "Blocking reasons should be in Spanish"

    with TemporaryDirectory() as temp_dir:
        path = persist_decision_memo(Path(temp_dir), payload)
        assert path.exists()

    print("Decision engine checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
