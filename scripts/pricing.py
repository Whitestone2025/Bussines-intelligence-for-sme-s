#!/usr/bin/env python3
"""Pricing model builder for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def round_money(value: float) -> float:
    return round(float(value), 2)


def pricing_fact_base(currency_code: str, monthly_cost: float, competitor_anchor: float, value_anchor: float) -> list[str]:
    return [
        f"Monthly delivery cost anchor: {currency_code} {monthly_cost:,.2f}.",
        f"Competitor price anchor: {currency_code} {competitor_anchor:,.2f}.",
        f"Value anchor: {currency_code} {value_anchor:,.2f}.",
    ]


def build_pricing_model(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    currency_code = str(payload.get("currency_code", "")).strip() or "MXN"
    monthly_cost = float(payload.get("monthly_delivery_cost", 0) or 0)
    desired_margin = float(payload.get("desired_margin_ratio", 0.6) or 0.6)
    competitor_anchor = float(payload.get("competitor_anchor_price", 0) or 0)
    value_anchor = float(payload.get("value_anchor_price", 0) or 0)
    target_segment = str(payload.get("target_segment", "")).strip() or "Founder-led service businesses"
    evidence_refs = [str(item).strip() for item in payload.get("evidence_refs", []) if str(item).strip()]
    source_refs = [str(item).strip() for item in payload.get("source_refs", []) if str(item).strip()]

    floor = monthly_cost / max(0.01, 1 - desired_margin)
    target_candidates = [value for value in [value_anchor, competitor_anchor, floor * 1.2] if value > 0]
    target = sum(target_candidates) / len(target_candidates) if target_candidates else floor * 1.25
    target = max(target, floor)
    ceiling = max(target * 1.35, competitor_anchor * 1.15 if competitor_anchor else 0, value_anchor, target)
    timestamp = now_iso()
    confidence = round(min(0.9, 0.4 + 0.06 * len(evidence_refs) + 0.04 * len(source_refs)), 2)
    fact_base = pricing_fact_base(currency_code, monthly_cost, competitor_anchor, value_anchor)
    pricing_options = [
        {
            "name": "Starter",
            "price": round_money(target * 0.75),
            "fit": "Fast validation with lower scope and lower trust burden.",
            "tradeoff": "Lower revenue per win and less room for hands-on support.",
            "recommended": False,
        },
        {
            "name": "Core",
            "price": round_money(target),
            "fit": "Best balance of trust, margin, and clarity for the first Mexico-first offer.",
            "tradeoff": "Still needs explicit scope so it does not feel abstract.",
            "recommended": True,
        },
        {
            "name": "Growth",
            "price": round_money(ceiling),
            "fit": "Useful once proof and implementation demand are both strong.",
            "tradeoff": "Higher trust requirement and more delivery complexity.",
            "recommended": False,
        },
    ]
    implementation_risks = [
        "The target tier can fail if scope is not made concrete during the sales conversation.",
        "A price anchored above visible proof can create trust friction even if the economics look strong.",
    ]

    return {
        "pricing_model_id": f"{company_id}-{slugify_id(target_segment)}-pricing",
        "company_id": company_id,
        "currency_code": currency_code,
        "pricing_strategy": "hybrid",
        "target_segment": target_segment,
        "fact_base": fact_base,
        "price_floor": round_money(floor),
        "price_target": round_money(target),
        "price_ceiling": round_money(ceiling),
        "tier_summaries": [
            {
                "name": "Starter",
                "price": round_money(target * 0.75),
                "value_summary": "Focused diagnostics and fast implementation guidance."
            },
            {
                "name": "Core",
                "price": round_money(target),
                "value_summary": "Full core offer with process clarity and buyer messaging support."
            },
            {
                "name": "Growth",
                "price": round_money(ceiling),
                "value_summary": "Higher-touch support with implementation and optimization."
            }
        ],
        "pricing_options": pricing_options,
        "recommended_tier": "Core",
        "recommendation_logic": "Recommend the Core tier first because it balances trust, delivery scope, and margin protection better than the lower-risk Starter tier or the heavier Growth tier.",
        "margin_assumptions": [
            f"Monthly delivery cost assumed at {currency_code} {monthly_cost:,.2f}.",
            f"Desired gross margin ratio assumed at {desired_margin:.0%}.",
            f"Competitor anchor price assumed at {currency_code} {competitor_anchor:,.2f}.",
            f"Value anchor assumed at {currency_code} {value_anchor:,.2f}."
        ],
        "implementation_risks": implementation_risks,
        "status": "inferred",
        "confidence": confidence,
        "source_origin": "pricing_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "assumption_refs": [f"{company_id}-pricing-assumption-{index + 1}" for index in range(4)],
        "finding_refs": [],
        "validated_fact_refs": [],
        "created_at": timestamp,
        "updated_at": timestamp
    }


def persist_pricing_model(root: Path, payload: dict) -> Path:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    model = build_pricing_model(payload)
    path = layout.record_path("pricing", company_id, model["pricing_model_id"])
    layout.write_json_atomic(path, model)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and persist a pricing model from JSON.")
    parser.add_argument("input", help="JSON fixture path")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    print(persist_pricing_model(Path(args.root).resolve(), payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
