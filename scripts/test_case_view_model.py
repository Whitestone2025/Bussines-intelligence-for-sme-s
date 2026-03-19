#!/usr/bin/env python3
"""Contract checks for the executive /api/case view model."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from competitors import persist_competitor_records
from decision_engine import persist_decision_memo
from financials import build_financial_snapshot, persist_financial_snapshot
from market_model import persist_market_models
from planner import persist_execution_plan
from pricing import build_pricing_model, persist_pricing_model
from render_report import persist_bundle
from serve_ui import build_case_payload, create_research_profile


ROOT = Path(__file__).resolve().parent.parent
COMPANY_ID = "case-view-model-lab"
REQUIRED_BLOCKS = (
    "hero",
    "war_room",
    "thesis",
    "market_summary",
    "competition_summary",
    "viability_summary",
    "decision_summary",
    "deliverable_index",
    "audit_index",
)


def cleanup() -> None:
    targets = [
        ROOT / "data" / "companies" / COMPANY_ID,
        ROOT / "data" / "research" / COMPANY_ID,
        ROOT / "data" / "sources" / COMPANY_ID,
        ROOT / "data" / "evidence" / COMPANY_ID,
        ROOT / "data" / "findings" / COMPANY_ID,
        ROOT / "data" / "market" / COMPANY_ID,
        ROOT / "data" / "competitors" / COMPANY_ID,
        ROOT / "data" / "pricing" / COMPANY_ID,
        ROOT / "data" / "financials" / COMPANY_ID,
        ROOT / "data" / "decisions" / COMPANY_ID,
        ROOT / "data" / "plans" / COMPANY_ID,
        ROOT / "data" / "deliverables" / COMPANY_ID,
        ROOT / "data" / "validation" / COMPANY_ID,
        ROOT / "data" / "reports" / COMPANY_ID,
        ROOT / "data" / "corpus" / "raw" / COMPANY_ID,
        ROOT / "data" / "corpus" / "clean" / COMPANY_ID,
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)


def seed_records() -> None:
    create_research_profile(
        {
            "company_name": "Case View Model Lab",
            "company_id": COMPANY_ID,
            "website": "https://example.test",
            "industry": "service clarity",
            "intake_mode": "existing",
            "seed_summary": "A founder-led service business focused on sales clarity in Mexico.",
            "primary_goal": "Improve conversion quality.",
            "available_sources": ["notes"],
        }
    )

    market_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "market" / "mexico-service.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_market_models(ROOT, market_payload)

    competitor_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "competitors" / "mexico-smb-services.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_competitor_records(ROOT, competitor_payload)

    pricing_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "pricing-financials" / "founder-service.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    pricing_model = build_pricing_model(pricing_payload)
    persist_pricing_model(ROOT, pricing_payload)
    persist_financial_snapshot(ROOT, pricing_payload, pricing_model)
    financials = build_financial_snapshot(pricing_payload, pricing_model)

    decision_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "decisions" / "readiness.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_decision_memo(ROOT, decision_payload)

    plan_payload = json.loads((ROOT / "data" / "tests" / "fixtures" / "plans" / "plan-input.json").read_text(encoding="utf-8")) | {"company_id": COMPANY_ID}
    persist_execution_plan(ROOT, plan_payload)

    bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))
    bundle["company"]["company_id"] = COMPANY_ID
    bundle["company"]["name"] = "Case View Model Lab"
    bundle["company"]["seed_summary"] = "A founder-led service business focused on sales clarity in Mexico."
    bundle["pricing_model"] = pricing_model
    bundle["financial_snapshot"] = financials
    persist_bundle(ROOT, COMPANY_ID, bundle)


def assert_block_shape(payload: dict, block_name: str) -> None:
    block = payload.get(block_name)
    assert isinstance(block, dict), f"{block_name} should be an object"
    for field in ("status", "confidence", "headline", "summary", "highlights"):
        assert field in block, f"{block_name} is missing {field}"


def main() -> int:
    cleanup()
    try:
        seed_records()
        payload = build_case_payload(COMPANY_ID)
        assert payload["company"]["company_id"] == COMPANY_ID, "Expected seeded case payload"

        for block_name in REQUIRED_BLOCKS:
            if block_name == "deliverable_index":
                assert isinstance(payload.get(block_name), list), "deliverable_index should be a list"
                assert payload[block_name], "Expected deliverables in deliverable_index"
                continue
            assert_block_shape(payload, block_name)

        hero = payload["hero"]
        assert hero["title"] == "Case View Model Lab", "Expected hero title to match active company"
        assert hero["website"], "Expected hero website"
        assert "te ayuda" in hero["narrative"].lower() or "te sirve" in hero["narrative"].lower()

        war_room = payload["war_room"]
        assert war_room["recommendation"], "Expected a war room recommendation"
        assert war_room["recommendation_label"], "Expected route label in war room"
        assert war_room["next_validation_step"], "Expected next validation step in war room"
        assert war_room["evidence_limits"], "Expected visible evidence limits in war room"
        assert war_room["featured_deliverables"], "Expected featured deliverables"
        assert "te ayuda" in war_room["summary"].lower() or "sirve" in war_room["summary"].lower()

        thesis = payload["thesis"]
        assert thesis["service_statement"], "Expected service statement"
        assert thesis["headline"], "Expected thesis headline"
        assert "buyer_truths" in thesis and "objections" in thesis["buyer_truths"], "Expected buyer truths structure"
        assert "te" in thesis["summary"].lower(), "Thesis summary should explain utility"

        market = payload["market_summary"]
        assert len(market["records"]) == 4, "Expected TAM, SAM, SOM, and attractiveness"
        assert "sirve" in market["summary"].lower() or "te ayuda" in market["summary"].lower()

        competition = payload["competition_summary"]
        assert competition["competitors"], "Expected competitor records"
        assert competition["whitespace"], "Expected whitespace analysis"

        viability = payload["viability_summary"]
        assert viability["pricing"]["price_target"], "Expected target price"
        assert "sirve" in viability["summary"].lower() or "te ayuda" in viability["summary"].lower()

        decision = payload["decision_summary"]
        assert decision["memo"]["recommended_action"], "Expected decision memo recommendation"
        assert decision["milestones"], "Expected execution milestones"
        assert decision["problem_structuring"]["headline"], "Expected structured problem headline"
        assert decision["evidence_limits"], "Expected visible evidence limits in decision summary"
        assert decision["confidence_note"], "Expected confidence note in decision summary"
        assert decision["decision_readout"]["criteria"], "Expected explicit decision criteria"
        assert decision["decision_readout"]["alternatives"], "Expected visible strategic alternatives"
        assert decision["decision_readout"]["recommended_route"]["why_this_route_wins"], "Expected explicit route rationale"
        assert decision["roadmap_readout"]["initiatives"], "Expected initiative roadmap preview"
        assert "te dice" in decision["summary"].lower() or "te" in decision["summary"].lower()

        audit = payload["audit_index"]
        assert audit["counts"]["sources"] >= 0, "Expected source count field"
        assert audit["counts"]["evidence"] >= 0, "Expected evidence count field"
        assert "te permite" in audit["summary"].lower() or "te" in audit["summary"].lower()

        print("Case view-model contract checks passed.")
        return 0
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
