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
    assert plan["initiative_roadmap"], "Plan should expose an initiative roadmap"
    assert len(plan["initiative_roadmap"]) >= 4, "Roadmap should contain multiple initiatives"
    assert plan["decision_checkpoints"], "Plan should expose decision checkpoints"
    assert plan["no_regret_moves"] is not None, "Plan should expose no-regret moves even if empty"
    assert plan["validation_agenda"], "Plan should expose the validation agenda"
    assert plan["sequence_rationale"], "Plan should explain sequencing"
    assert any(item["timeframe"] == "Dias 1-30" for item in plan["initiative_roadmap"]), "Roadmap should cover the first 30 days"
    assert all(item["lagging_indicator"] for item in plan["initiative_roadmap"]), "Each initiative should expose lagging indicators"
    assert all(item["key_risks"] for item in plan["initiative_roadmap"]), "Each initiative should expose initiative risks"
    assert all(item["risk_mitigation"] for item in plan["initiative_roadmap"]), "Each initiative should expose mitigation actions"
    assert all(item["decision_trigger"] for item in plan["initiative_roadmap"]), "Each initiative should expose a decision trigger"
    assert all(item["exit_criteria"] for item in plan["initiative_roadmap"]), "Each initiative should expose exit criteria"

    with TemporaryDirectory() as temp_dir:
        path = persist_execution_plan(Path(temp_dir), payload)
        assert path.exists()

    print("Execution planner checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
