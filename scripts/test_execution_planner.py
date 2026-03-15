#!/usr/bin/env python3
"""Checks for the 30/60/90 execution planner."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from planner import build_execution_plan, persist_execution_plan


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "plans" / "plan-input.json").read_text(encoding="utf-8"))
    plan = build_execution_plan(payload)

    assert plan["plan_horizon"] == "30-60-90"
    assert len(plan["milestones"]) == 3
    assert all(item["dependencies"] is not None for item in plan["milestones"])
    assert all(item["learning_goal"] for item in plan["milestones"]), "Milestones should explain learning goals"
    assert any(item["risk_watchouts"] for item in plan["milestones"]), "Milestones should include watchouts"
    assert plan["decision_refs"], "Plan should reference the decision memo"
    assert plan["workstreams"], "Plan should expose workstreams"
    assert plan["validation_agenda"], "Plan should expose the validation agenda"
    assert plan["sequence_rationale"], "Plan should explain sequencing"

    with TemporaryDirectory() as temp_dir:
        path = persist_execution_plan(Path(temp_dir), payload)
        assert path.exists()

    print("Execution planner checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
