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
    assert memo["options"], "Expected option set"
    assert memo["validation_gaps"], "Expected validation gaps"
    assert memo["next_steps"]

    blocked_payload = payload | {"evidence_count": 2, "has_offer": False}
    blocked = readiness_check(blocked_payload)
    assert blocked["status"] == "blocked"
    blocked_memo = build_decision_memo(blocked_payload)
    assert blocked_memo["status"] == "needs_validation"
    assert blocked_memo["validation_gaps"], "Blocked decisions should surface validation gaps"

    with TemporaryDirectory() as temp_dir:
        path = persist_decision_memo(Path(temp_dir), payload)
        assert path.exists()

    print("Decision engine checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
