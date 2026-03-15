#!/usr/bin/env python3
"""Contract checks for the executive /api/case view model."""

from __future__ import annotations

from serve_ui import build_case_payload


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


def assert_block_shape(payload: dict, block_name: str) -> None:
    block = payload.get(block_name)
    assert isinstance(block, dict), f"{block_name} should be an object"
    for field in ("status", "confidence", "headline", "summary", "highlights"):
        assert field in block, f"{block_name} is missing {field}"


def main() -> int:
    payload = build_case_payload("the-preview")
    assert payload["company"]["company_id"] == "the-preview", "Expected The Preview case payload"

    for block_name in REQUIRED_BLOCKS:
        if block_name == "deliverable_index":
            assert isinstance(payload.get(block_name), list), "deliverable_index should be a list"
            assert payload[block_name], "Expected deliverables in deliverable_index"
            continue
        assert_block_shape(payload, block_name)

    hero = payload["hero"]
    assert hero["title"] == "The Preview", "Expected hero title to match active company"
    assert hero["website"], "Expected hero website"

    war_room = payload["war_room"]
    assert war_room["recommendation"], "Expected a war room recommendation"
    assert war_room["featured_deliverables"], "Expected featured deliverables"

    thesis = payload["thesis"]
    assert thesis["service_statement"], "Expected service statement"
    assert thesis["offer"]["name"], "Expected curated offer name"
    assert thesis["buyer_truths"]["objections"], "Expected buyer objections"

    market = payload["market_summary"]
    assert len(market["records"]) == 4, "Expected TAM, SAM, SOM, and attractiveness"

    competition = payload["competition_summary"]
    assert competition["competitors"], "Expected competitor records"
    assert competition["whitespace"], "Expected whitespace analysis"

    viability = payload["viability_summary"]
    assert viability["pricing"]["price_target"], "Expected target price"

    decision = payload["decision_summary"]
    assert decision["memo"]["recommended_action"], "Expected decision memo recommendation"
    assert decision["milestones"], "Expected execution milestones"

    audit = payload["audit_index"]
    assert audit["counts"]["sources"] >= 1, "Expected source count"
    assert audit["counts"]["evidence"] >= 1, "Expected evidence count"
    assert audit["traceability"]["decision"], "Expected decision traceability"

    print("Case view-model contract checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
