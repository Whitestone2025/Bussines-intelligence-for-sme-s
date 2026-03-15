#!/usr/bin/env python3
"""Render consulting-grade markdown deliverables from canonical objects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def unique_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = str(item).strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)
    return ordered


def money(currency_code: str, value: float) -> str:
    return f"{currency_code} {value:,.2f}"


def first_non_empty(*values: str) -> str:
    for value in values:
        normalized = str(value or "").strip()
        if normalized:
            return normalized
    return ""


def decision_question(bundle: dict) -> str:
    company = bundle["company"]
    offer = bundle["offer"]
    decision = bundle["decision_memo"]
    return first_non_empty(
        bundle.get("decision_question", ""),
        decision.get("decision_summary", ""),
        f"What is the highest-confidence next move for {company['name']} to validate and grow the {offer['name']} offer in Mexico?",
    )


def current_thesis(bundle: dict) -> str:
    company = bundle["company"]
    icp = bundle["icp"]
    offer = bundle["offer"]
    decision = bundle["decision_memo"]
    return first_non_empty(
        bundle.get("current_thesis", ""),
        (
            f"{company['name']} should lead with {offer['name']} for {icp['label']} because buyers respond to "
            "clarity, transparent delivery, and a focused first acquisition experiment."
        ),
        decision.get("recommended_action", ""),
    )


def fact_base(bundle: dict) -> list[str]:
    company = bundle["company"]
    icp = bundle["icp"]
    offer = bundle["offer"]
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    decision = bundle["decision_memo"]
    facts = [str(item).strip() for item in bundle.get("validated_facts", []) if str(item).strip()]
    if facts:
        return unique_preserve(facts)
    facts.extend(
        [
            company.get("seed_summary", ""),
            f"Primary ICP: {icp['label']}.",
            f"Offer in focus: {offer['name']} with promise '{offer['core_promise']}'.",
            f"Blended market estimate for {market['segment_name']}: {money(market['currency_code'], market['blended_value'])}.",
            f"Target price currently points to {money(pricing['currency_code'], pricing['price_target'])}.",
        ]
    )
    for proof_point in offer.get("proof_points", []):
        facts.append(f"Visible proof point: {proof_point}.")
    for evidence_ref in decision.get("evidence_refs", []):
        facts.append(f"Evidence reference available: {evidence_ref}.")
    return unique_preserve(facts)


def assumptions(bundle: dict) -> list[str]:
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    assumption_lines = [str(item).strip() for item in bundle.get("assumptions", []) if str(item).strip()]
    assumption_lines.extend(str(item).strip() for item in market.get("key_assumptions", []) if str(item).strip())
    assumption_lines.extend(str(item).strip() for item in pricing.get("margin_assumptions", []) if str(item).strip())
    if not assumption_lines:
        assumption_lines.append("The current recommendation assumes the first chosen channel can be validated quickly with founder-led execution.")
    return unique_preserve(assumption_lines)


def decision_criteria(bundle: dict) -> list[str]:
    criteria = [str(item).strip() for item in bundle.get("decision_criteria", []) if str(item).strip()]
    if criteria:
        return unique_preserve(criteria)
    return [
        "Speed to real market signal in Mexico.",
        "Trust fit for founder-led service buyers.",
        "Economics that protect margin while keeping the offer credible.",
        "Execution simplicity for a founder with limited bandwidth.",
    ]


def contrary_evidence(bundle: dict) -> list[str]:
    decision = bundle["decision_memo"]
    items = [str(item).strip() for item in bundle.get("contrary_evidence", []) if str(item).strip()]
    items.extend(str(item).strip() for item in decision.get("key_risks", []) if str(item).strip())
    return unique_preserve(items)


def validation_gaps(bundle: dict) -> list[str]:
    items = [str(item).strip() for item in bundle.get("validation_gaps", []) if str(item).strip()]
    items.extend(contrary_evidence(bundle))
    if not items:
        items.append("Validate early conversion quality before scaling channel spend or delivery scope.")
    return unique_preserve(items)


def inferred_points(bundle: dict) -> list[str]:
    decision = bundle["decision_memo"]
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    inferences = [str(item).strip() for item in bundle.get("inferences", []) if str(item).strip()]
    if inferences:
        return unique_preserve(inferences)
    inferences.extend(
        [
            f"The market appears attractive enough to test because the current model estimates {money(market['currency_code'], market['blended_value'])} in blended value.",
            f"The viable price corridor likely sits between {money(pricing['currency_code'], pricing['price_floor'])} and {money(pricing['currency_code'], pricing['price_ceiling'])}.",
            f"The current recommendation remains a live hypothesis with {decision.get('confidence', 0):.0%} confidence.",
        ]
    )
    return unique_preserve(inferences)


def execution_realities(bundle: dict) -> list[str]:
    plan = bundle["execution_plan"]
    realities = [str(item).strip() for item in bundle.get("execution_realities", []) if str(item).strip()]
    if realities:
        return unique_preserve(realities)
    realities.extend(
        [
            "The founder is the default owner for the first 90 days, so the plan must stay lightweight and sequential.",
            "Each milestone depends on learning from the previous step before scaling scope or spend.",
        ]
    )
    for milestone in plan.get("milestones", []):
        realities.append(
            f"{milestone['timeframe']}: owner {milestone.get('owner', 'Founder')} must hit '{milestone['success_metric']}'."
        )
    return unique_preserve(realities)


def build_options(bundle: dict) -> list[dict]:
    provided = bundle.get("options", [])
    if provided:
        normalized = []
        for index, option in enumerate(provided, start=1):
            normalized.append(
                {
                    "label": first_non_empty(option.get("label", ""), f"Option {index}"),
                    "summary": first_non_empty(option.get("summary", ""), option.get("action", "")),
                    "pros": [str(item).strip() for item in option.get("pros", []) if str(item).strip()],
                    "cons": [str(item).strip() for item in option.get("cons", []) if str(item).strip()],
                    "recommended": bool(option.get("recommended", False)),
                }
            )
        if normalized and not any(item["recommended"] for item in normalized):
            normalized[0]["recommended"] = True
        return normalized

    decision = bundle["decision_memo"]
    criteria = decision_criteria(bundle)
    options = [
        {
            "label": "Recommended path",
            "summary": decision["recommended_action"],
            "pros": [
                f"Best fit against the current criteria: {criteria[0]}",
                f"Supported by current why-now logic: {decision['why_now']}",
            ],
            "cons": contrary_evidence(bundle)[:2],
            "recommended": True,
        }
    ]
    for index, action in enumerate(decision.get("alternative_actions", []), start=1):
        options.append(
            {
                "label": f"Alternative {index}",
                "summary": action,
                "pros": [
                    "Creates a credible fallback path if the main experiment underperforms.",
                ],
                "cons": [
                    "Slower path to signal than the recommended move.",
                ],
                "recommended": False,
            }
        )
    return options


def option_lines(bundle: dict) -> list[str]:
    lines: list[str] = []
    for option in build_options(bundle):
        prefix = "Recommended" if option["recommended"] else "Alternative"
        lines.append(f"{prefix}: {option['label']} -> {option['summary']}")
        for item in option.get("pros", []):
            lines.append(f"  Pros: {item}")
        for item in option.get("cons", []):
            lines.append(f"  Tradeoff: {item}")
    return lines


def traceability_lines(bundle: dict) -> list[str]:
    decision = bundle["decision_memo"]
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    refs = []
    refs.extend(f"Evidence: {item}" for item in decision.get("evidence_refs", []))
    refs.extend(f"Assumption: {item}" for item in market.get("assumption_refs", []))
    refs.extend(f"Assumption: {item}" for item in pricing.get("assumption_refs", []))
    refs.extend(f"Decision assumption: {item}" for item in decision.get("assumption_refs", []))
    return unique_preserve(refs)


def executive_memo(bundle: dict) -> str:
    company = bundle["company"]
    decision = bundle["decision_memo"]
    return "\n".join(
        [
            "# Executive Memo",
            "",
            f"## Company",
            "",
            company["name"],
            "",
            "## Decision Question",
            "",
            decision_question(bundle),
            "",
            "## Current Thesis",
            "",
            current_thesis(bundle),
            "",
            "## Fact Base",
            "",
            bullet_lines(fact_base(bundle)),
            "",
            "## Key Assumptions",
            "",
            bullet_lines(assumptions(bundle)),
            "",
            "## Options Considered",
            "",
            bullet_lines(option_lines(bundle)),
            "",
            "## Recommendation Criteria",
            "",
            bullet_lines(decision_criteria(bundle)),
            "",
            "## Recommendation",
            "",
            decision["recommended_action"],
            "",
            "## Why This Matters",
            "",
            decision["why_now"],
            "",
            "## Risks And Contrary Evidence",
            "",
            bullet_lines(contrary_evidence(bundle)),
            "",
            "## Traceability",
            "",
            bullet_lines(traceability_lines(bundle)),
            "",
            "## Immediate Next Actions",
            "",
            bullet_lines(decision.get("next_steps", [])),
            "",
        ]
    )


def business_diagnosis(bundle: dict) -> str:
    company = bundle["company"]
    icp = bundle["icp"]
    offer = bundle["offer"]
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    decision = bundle["decision_memo"]
    return "\n".join(
        [
            "# Business Diagnosis",
            "",
            "## Core Problem",
            "",
            company["seed_summary"],
            "",
            "## Current Thesis",
            "",
            current_thesis(bundle),
            "",
            "## What We Know",
            "",
            bullet_lines(fact_base(bundle)),
            "",
            "## What We Infer",
            "",
            bullet_lines(inferred_points(bundle)),
            "",
            "## What Still Needs Validation",
            "",
            bullet_lines(validation_gaps(bundle)),
            "",
            "## ICP",
            "",
            icp["label"],
            "",
            "## Offer",
            "",
            f"{offer['name']}: {offer['core_promise']}",
            "",
            "## Market",
            "",
            f"{market['segment_name']} estimated blended size: {market['currency_code']} {market['blended_value']:,.2f}",
            "",
            "## Pricing",
            "",
            f"Target price: {pricing['currency_code']} {pricing['price_target']:,.2f}",
            "",
            "## Strategic Options",
            "",
            bullet_lines(option_lines(bundle)),
            "",
            "## Execution Realities",
            "",
            bullet_lines(execution_realities(bundle)),
            "",
            "## Risks",
            "",
            bullet_lines(decision.get("key_risks", [])),
            "",
        ]
    )


def deck_outline(bundle: dict) -> str:
    plan = bundle["execution_plan"]
    lines = [
        "# Deck Outline",
        "",
        "1. Thesis And Decision Question",
        "2. Core Problem And Constraints",
        "3. Fact Base",
        "4. Market Size And Attractiveness",
        "5. Pricing Logic And Economics",
        "6. Options Considered",
        "7. Recommendation Criteria",
        "8. Recommendation And Risks",
        "9. 30/60/90 Plan",
        "10. Validation Agenda",
        "",
        "## 30/60/90 Milestones",
        "",
    ]
    for milestone in plan.get("milestones", []):
        lines.append(f"- {milestone['timeframe']}: {milestone['name']} ({milestone['success_metric']})")
    lines.append("")
    return "\n".join(lines)


def risk_memo(bundle: dict) -> str:
    decision = bundle["decision_memo"]
    risk_lines = []
    for risk in decision.get("key_risks", []):
        risk_lines.append(f"Risk: {risk}")
        risk_lines.append("  Owner: Founder")
        risk_lines.append("  Early signal: Watch objections, low conversion quality, or inability to explain scope quickly.")
    mitigations = unique_preserve(
        [
            "Use evidence-backed language and visible proof.",
            "Validate channels with low-cost experiments before scaling.",
            "Review pricing and objections every 30 days.",
            *validation_gaps(bundle),
        ]
    )
    return "\n".join(
        [
            "# Risk Memo",
            "",
            "## Contrary Evidence And Watchouts",
            "",
            bullet_lines(contrary_evidence(bundle)),
            "",
            "## Risk Register",
            "",
            bullet_lines(risk_lines),
            "",
            "## Mitigation Plan",
            "",
            bullet_lines(mitigations),
            "",
        ]
    )


def render_bundle(bundle: dict) -> dict[str, str]:
    return {
        "executive-memo": executive_memo(bundle),
        "business-diagnosis": business_diagnosis(bundle),
        "deck-outline": deck_outline(bundle),
        "risk-memo": risk_memo(bundle),
    }


def persist_bundle(root: Path, company_id: str, bundle: dict) -> dict[str, Path]:
    layout = WorkspaceLayout(root=root)
    layout.ensure_company_workspace(company_id)
    outputs = {}
    for key, content in render_bundle(bundle).items():
        path = layout.record_path("deliverables", company_id, key, extension=".md")
        path.write_text(content, encoding="utf-8")
        outputs[key] = path
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Render markdown deliverables from a JSON bundle.")
    parser.add_argument("input", help="JSON bundle fixture")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()
    bundle = json.loads(Path(args.input).read_text(encoding="utf-8"))
    outputs = persist_bundle(Path(args.root).resolve(), bundle["company"]["company_id"], bundle)
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
