#!/usr/bin/env python3
"""Decision engine and readiness gate for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def decision_question(payload: dict) -> str:
    business_goal = str(payload.get("business_goal", "")).strip()
    if business_goal:
        return f"What is the highest-confidence next move to {business_goal.lower()}?"
    return "What is the next best move that reduces uncertainty while improving business traction?"


def decision_criteria(payload: dict) -> list[str]:
    criteria = [str(item).strip() for item in payload.get("decision_criteria", []) if str(item).strip()]
    if criteria:
        return criteria
    return [
        "Speed to credible market learning.",
        "Fit with founder execution capacity.",
        "Confidence in channel and offer clarity.",
        "Economics strong enough to justify execution.",
    ]


def option_label(action: str, fallback: str) -> str:
    lowered = action.lower()
    if "price" in lowered:
        return "Pricing-first option"
    if "measure" in lowered or "conversion" in lowered:
        return "Measurement-first option"
    if "collect" in lowered or "evidence" in lowered or "validate" in lowered:
        return "Validation-first option"
    if "launch" in lowered or "channel" in lowered:
        return "Focused execution option"
    return fallback


def readiness_check(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    evidence_count = int(payload.get("evidence_count", 0) or 0)
    source_count = int(payload.get("source_count", 0) or 0)
    has_icp = bool(payload.get("has_icp", False))
    has_offer = bool(payload.get("has_offer", False))
    market_confidence = float(payload.get("market_confidence", 0) or 0)
    pricing_confidence = float(payload.get("pricing_confidence", 0) or 0)
    channel_confidence = float(payload.get("channel_confidence", 0) or 0)

    minimum_evidence_met = evidence_count >= 5
    source_diversity_met = source_count >= 2
    service_defined = has_offer
    icp_defined = has_icp
    channel_defined = channel_confidence >= 0.6
    insight_density = (market_confidence + pricing_confidence + channel_confidence) / 3 >= 0.6

    blockers = []
    if not minimum_evidence_met:
        blockers.append("Add at least 5 evidence entries before making a major decision.")
    if not source_diversity_met:
        blockers.append("Add at least 2 distinct sources for stronger confidence.")
    if not service_defined:
        blockers.append("Clarify the offer before recommending execution.")
    if not icp_defined:
        blockers.append("Define the ICP before selecting channels or pricing.")
    if not channel_defined:
        blockers.append("Strengthen channel confidence before execution.")
    if not insight_density:
        blockers.append("Market, pricing, and channel confidence are still too weak.")

    score = round(
        (
            (1 if minimum_evidence_met else 0)
            + (1 if source_diversity_met else 0)
            + (1 if service_defined else 0)
            + (1 if icp_defined else 0)
            + (1 if channel_defined else 0)
            + (1 if insight_density else 0)
        )
        / 6,
        2,
    )
    return {
        "company_id": company_id,
        "score": score,
        "status": "ready" if not blockers else "blocked",
        "minimum_evidence_met": minimum_evidence_met,
        "source_diversity_met": source_diversity_met,
        "service_defined": service_defined,
        "icp_defined": icp_defined,
        "channel_defined": channel_defined,
        "insight_density": insight_density,
        "fact_base": [
            f"Evidence entries available: {evidence_count}.",
            f"Distinct sources available: {source_count}.",
            f"ICP defined: {'yes' if has_icp else 'no'}.",
            f"Offer defined: {'yes' if has_offer else 'no'}.",
        ],
        "assumptions": [
            f"Market confidence assumed at {market_confidence:.0%}.",
            f"Pricing confidence assumed at {pricing_confidence:.0%}.",
            f"Channel confidence assumed at {channel_confidence:.0%}.",
        ],
        "blocking_reasons": blockers,
    }


def rank_next_actions(payload: dict, readiness: dict) -> list[str]:
    actions = []
    if readiness["blocking_reasons"]:
        if not readiness["minimum_evidence_met"]:
            actions.append("Collect more buyer evidence before making execution bets.")
        if not readiness["icp_defined"]:
            actions.append("Validate the primary ICP and how it buys.")
        if not readiness["service_defined"]:
            actions.append("Tighten the offer and explain the delivery mechanism clearly.")
        if not readiness["channel_defined"]:
            actions.append("Confirm the first acquisition channel with local evidence.")
        if not readiness["insight_density"]:
            actions.append("Strengthen market and pricing confidence before launch.")
        return actions

    actions.append("Launch the first Mexico-first acquisition experiment on the best-fit channel.")
    actions.append("Test the target pricing tier with explicit scope and proof.")
    actions.append("Measure conversion quality, not just lead volume, for 30 days.")
    return actions


def build_decision_memo(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    readiness = readiness_check(payload)
    actions = rank_next_actions(payload, readiness)
    confidence = round(
        min(
            0.95,
            0.35
            + float(payload.get("market_confidence", 0) or 0) * 0.2
            + float(payload.get("pricing_confidence", 0) or 0) * 0.2
            + float(payload.get("channel_confidence", 0) or 0) * 0.2,
        ),
        2,
    )
    timestamp = now_iso()
    business_goal = str(payload.get("business_goal", "")).strip() or "Reduce uncertainty and pick the next best move."
    criteria = decision_criteria(payload)
    question = decision_question(payload)
    fact_base = list(readiness["fact_base"])
    assumptions = list(readiness["assumptions"])

    if readiness["status"] == "blocked":
        decision_type = "viability"
        recommended_action = actions[0] if actions else "Resolve the highest-confidence blocker first."
        why_now = "The system does not yet have enough validated context to recommend execution safely."
        risks = readiness["blocking_reasons"]
        validation_gaps = list(readiness["blocking_reasons"])
    else:
        decision_type = "go_to_market"
        recommended_action = actions[0]
        why_now = "The system has enough evidence and confidence to recommend a focused next move."
        risks = [
            "Execution may still fail if the offer is not explained with enough specificity.",
            "Channel assumptions should be validated with early conversion data.",
        ]
        validation_gaps = list(risks)

    options = []
    for index, action in enumerate(actions, start=1):
        options.append(
            {
                "label": option_label(action, f"Option {index}"),
                "summary": action,
                "recommended": index == 1,
                "criteria_fit": criteria[0] if index == 1 else criteria[min(index - 1, len(criteria) - 1)],
            }
        )

    return {
        "decision_id": f"{company_id}-{slugify_id(decision_type)}-memo",
        "company_id": company_id,
        "decision_type": decision_type,
        "decision_question": question,
        "recommended_action": recommended_action,
        "decision_summary": business_goal,
        "why_now": why_now,
        "decision_criteria": criteria,
        "fact_base": fact_base,
        "assumptions": assumptions,
        "options": options,
        "alternative_actions": actions[1:] if len(actions) > 1 else [],
        "key_risks": risks,
        "implementation_risks": list(risks),
        "validation_gaps": validation_gaps,
        "next_steps": actions,
        "status": "inferred" if readiness["status"] == "ready" else "needs_validation",
        "confidence": confidence,
        "source_origin": "decision_engine",
        "evidence_refs": [str(item).strip() for item in payload.get("evidence_refs", []) if str(item).strip()],
        "source_refs": [str(item).strip() for item in payload.get("source_refs", []) if str(item).strip()],
        "assumption_refs": [f"{company_id}-decision-assumption-readiness"],
        "finding_refs": [],
        "validated_fact_refs": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def persist_decision_memo(root: Path, payload: dict) -> Path:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    memo = build_decision_memo(payload)
    path = layout.record_path("decisions", company_id, memo["decision_id"])
    layout.write_json_atomic(path, memo)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and persist a decision memo from JSON.")
    parser.add_argument("input", help="JSON fixture path")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()
    print(persist_decision_memo(Path(args.root).resolve(), json.loads(Path(args.input).read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
