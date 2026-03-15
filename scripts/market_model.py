#!/usr/bin/env python3
"""Market discovery engine for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def round_money(value: float) -> float:
    return round(float(value), 2)


def market_fact_base(geography: list[str], total_customers: float, reachable_customers: float, annual_price: float, currency_code: str) -> list[str]:
    return [
        f"Geography under analysis: {', '.join(geography)}.",
        f"Total addressable customers currently modeled: {int(total_customers)}.",
        f"Known reachable customers currently modeled: {int(reachable_customers)}.",
        f"Annual revenue per customer anchor: {currency_code} {annual_price:,.2f}.",
    ]


def market_scenarios(annual_price: float, serviceable_customers: float, obtainable_customers: float, reachable_customers: float, close_rate: float) -> list[dict]:
    conservative_customers = max(reachable_customers * close_rate * 0.7, obtainable_customers * 0.7)
    base_customers = max(reachable_customers * close_rate, obtainable_customers)
    upside_customers = max(base_customers * 1.4, serviceable_customers * 0.18)
    return [
        {"label": "conservative", "customer_count": round_money(conservative_customers), "value": round_money(conservative_customers * annual_price)},
        {"label": "base", "customer_count": round_money(base_customers), "value": round_money(base_customers * annual_price)},
        {"label": "upside", "customer_count": round_money(upside_customers), "value": round_money(upside_customers * annual_price)},
    ]


def build_market_models(payload: dict) -> list[dict]:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    segment_name = str(payload.get("segment_name", "")).strip() or "core-market"
    geography = [str(item).strip() for item in payload.get("geography", []) if str(item).strip()] or ["Mexico"]
    currency_code = str(payload.get("currency_code", "")).strip() or "MXN"
    annual_price = float(payload.get("annual_price_per_customer", 0) or 0)
    total_customers = float(payload.get("total_addressable_customers", 0) or 0)
    target_ratio = clamp_ratio(float(payload.get("target_customer_ratio", 0) or 0))
    serviceable_ratio = clamp_ratio(float(payload.get("serviceable_customer_ratio", 0) or 0))
    obtainable_ratio = clamp_ratio(float(payload.get("obtainable_customer_ratio", 0) or 0))
    reachable_customers = float(payload.get("known_reachable_customers", 0) or 0)
    close_rate = clamp_ratio(float(payload.get("expected_close_rate", 0) or 0))

    target_customers = total_customers * target_ratio
    serviceable_customers = target_customers * serviceable_ratio
    obtainable_customers = serviceable_customers * obtainable_ratio
    bottom_up_tam = reachable_customers * annual_price
    top_down_tam = target_customers * annual_price
    blended_tam = (top_down_tam + bottom_up_tam) / 2 if top_down_tam and bottom_up_tam else max(top_down_tam, bottom_up_tam)
    sam_value = serviceable_customers * annual_price
    som_value = obtainable_customers * annual_price if obtainable_customers else reachable_customers * close_rate * annual_price

    competition_intensity = float(payload.get("competition_intensity", 5) or 5)
    urgency_score = float(payload.get("urgency_score", 5) or 5)
    budget_fit_score = float(payload.get("budget_fit_score", 5) or 5)
    channel_access_score = float(payload.get("channel_access_score", 5) or 5)
    attractiveness_score = round(((11 - competition_intensity) + urgency_score + budget_fit_score + channel_access_score) / 4, 2)
    assumptions = [
        f"Annual price per customer assumed at {currency_code} {annual_price:,.2f}.",
        f"Target customer ratio set at {target_ratio:.0%} of the total addressable customer base.",
        f"Serviceable customer ratio set at {serviceable_ratio:.0%} of target customers.",
        f"Obtainable customer ratio set at {obtainable_ratio:.0%} of serviceable customers.",
        f"Bottom-up model uses {int(reachable_customers)} reachable customers and {close_rate:.0%} expected close rate.",
    ]
    facts = market_fact_base(geography, total_customers, reachable_customers, annual_price, currency_code)
    scenarios = market_scenarios(annual_price, serviceable_customers, obtainable_customers, reachable_customers, close_rate)
    entry_posture = "focused pilot" if attractiveness_score >= 7 else "validation-first niche test" if attractiveness_score >= 5 else "defer and gather stronger evidence"
    implementation_risks = unique_risks = [
        "Top-down demand may look larger than what a founder can actually reach in the first 90 days.",
        "Market attractiveness can degrade quickly if trust-building channels underperform.",
    ]
    timestamp = now_iso()
    common = {
        "company_id": company_id,
        "geography": geography,
        "currency_code": currency_code,
        "segment_name": segment_name,
        "fact_base": facts,
        "growth_rate_assumption": float(payload.get("growth_rate_assumption", 0.12) or 0.12),
        "methodology_summary": "Blended market model using top-down demand assumptions and bottom-up reachable-customer heuristics.",
        "key_assumptions": assumptions,
        "assumptions": assumptions,
        "scenarios": scenarios,
        "recommended_entry_posture": entry_posture,
        "implementation_risks": unique_risks,
        "status": "inferred",
        "confidence": round(min(0.9, 0.45 + 0.08 * len(payload.get("evidence_refs", [])) + 0.04 * len(payload.get("source_refs", []))), 2),
        "source_origin": "market_model_engine",
        "evidence_refs": [str(item).strip() for item in payload.get("evidence_refs", []) if str(item).strip()],
        "source_refs": [str(item).strip() for item in payload.get("source_refs", []) if str(item).strip()],
        "assumption_refs": [f"{segment_name}-assumption-{index + 1}" for index in range(len(assumptions))],
        "finding_refs": [],
        "validated_fact_refs": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    models = [
        common
        | {
            "market_model_id": f"{company_id}-{slugify_id(segment_name)}-tam",
            "market_type": "tam",
            "top_down_value": round_money(top_down_tam),
            "bottom_up_value": round_money(bottom_up_tam),
            "blended_value": round_money(blended_tam),
        },
        common
        | {
            "market_model_id": f"{company_id}-{slugify_id(segment_name)}-sam",
            "market_type": "sam",
            "top_down_value": round_money(sam_value),
            "bottom_up_value": round_money(reachable_customers * annual_price),
            "blended_value": round_money(sam_value),
        },
        common
        | {
            "market_model_id": f"{company_id}-{slugify_id(segment_name)}-som",
            "market_type": "som",
            "top_down_value": round_money(som_value),
            "bottom_up_value": round_money(reachable_customers * close_rate * annual_price),
            "blended_value": round_money(som_value),
        },
        common
        | {
            "market_model_id": f"{company_id}-{slugify_id(segment_name)}-attractiveness",
            "market_type": "attractiveness",
            "top_down_value": attractiveness_score,
            "bottom_up_value": attractiveness_score,
            "blended_value": attractiveness_score,
            "methodology_summary": (
                "Attractiveness score balances competitive pressure, urgency of the problem, budget fit, and channel accessibility."
            ),
            "key_assumptions": assumptions
            + [
                f"Competition intensity scored at {competition_intensity}/10.",
                f"Urgency scored at {urgency_score}/10, budget fit at {budget_fit_score}/10, and channel access at {channel_access_score}/10.",
            ],
        },
    ]
    return models


def persist_market_models(root: Path, payload: dict) -> list[Path]:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    outputs = []
    for model in build_market_models(payload):
        path = layout.record_path("market", company_id, model["market_model_id"])
        layout.write_json_atomic(path, model)
        outputs.append(path)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build market model records from a fixture or JSON payload.")
    parser.add_argument("input", help="JSON file with market assumptions")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    paths = persist_market_models(Path(args.root).resolve(), payload)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
