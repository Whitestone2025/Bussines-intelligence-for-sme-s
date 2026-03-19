#!/usr/bin/env python3
"""Checks that the planner is driven by a real initiative roadmap, not just three linear tasks."""

from __future__ import annotations

import json
from pathlib import Path

from planner import build_execution_plan


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "plans" / "plan-input.json").read_text(encoding="utf-8"))
    plan = build_execution_plan(payload)
    roadmap = plan["initiative_roadmap"]

    assert len(roadmap) >= 4, "Expected a multi-initiative roadmap"
    assert plan["milestones"][0]["name"] != roadmap[0]["name"], "30/60/90 should summarize the roadmap, not duplicate it verbatim"
    assert any(item["workstream"] == "Gobierno de decision" for item in roadmap), "Expected a decision-governance workstream"
    assert any(item["stage_gate"] == "Gate 4" for item in roadmap), "Expected a final scale-or-pivot gate"
    assert any("sostener, ajustar o redirigir" in item["decision_trigger"].lower() or "reencuadr" in item["decision_trigger"].lower() for item in roadmap), "Expected explicit decision triggers"
    assert all(item["dependencies"] is not None for item in roadmap), "Roadmap initiatives should declare dependencies"

    print("Initiative roadmap quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
