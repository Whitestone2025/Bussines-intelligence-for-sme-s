#!/usr/bin/env python3
"""Financial snapshot builder for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def round_number(value: float) -> float:
    return round(float(value), 2)


def build_financial_snapshot(payload: dict, pricing_model: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    currency_code = pricing_model["currency_code"]
    lifetime_months = float(payload.get("customer_lifetime_months", 6) or 6)
    monthly_revenue = float(payload.get("average_monthly_revenue_per_customer", pricing_model["price_target"]) or pricing_model["price_target"])
    monthly_delivery_cost = float(payload.get("monthly_delivery_cost", 0) or 0)
    fixed_monthly_cost = float(payload.get("fixed_monthly_cost", 0) or 0)
    estimated_cac = float(payload.get("estimated_cac", 0) or 0)
    evidence_refs = [str(item).strip() for item in payload.get("evidence_refs", []) if str(item).strip()]
    source_refs = [str(item).strip() for item in payload.get("source_refs", []) if str(item).strip()]

    gross_margin_ratio = max(0.0, min(1.0, (monthly_revenue - monthly_delivery_cost) / monthly_revenue if monthly_revenue else 0.0))
    estimated_ltv = monthly_revenue * lifetime_months * gross_margin_ratio
    ltv_cac_ratio = estimated_ltv / estimated_cac if estimated_cac else 0.0
    payback_months = estimated_cac / max(1, (monthly_revenue - monthly_delivery_cost)) if estimated_cac else 0.0
    contribution_margin = max(1, (monthly_revenue - monthly_delivery_cost))
    break_even_customers = fixed_monthly_cost / contribution_margin if contribution_margin else 0.0

    warning = ""
    if len(evidence_refs) < 2:
        warning = "Low evidence depth: viability estimate is highly assumption-driven."
    elif ltv_cac_ratio and ltv_cac_ratio < 3:
        warning = "LTV:CAC appears weak and may require pricing or channel changes."
    elif gross_margin_ratio < 0.45:
        warning = "Gross margin looks thin for a founder-led service business."

    timestamp = now_iso()
    confidence = round(min(0.9, 0.35 + 0.06 * len(evidence_refs) + 0.04 * len(source_refs)), 2)

    return {
        "snapshot_id": f"{company_id}-{slugify_id(pricing_model['target_segment'])}-financials",
        "company_id": company_id,
        "currency_code": currency_code,
        "customer_lifetime_months": round_number(lifetime_months),
        "average_monthly_revenue_per_customer": round_number(monthly_revenue),
        "gross_margin_ratio": round_number(gross_margin_ratio),
        "estimated_cac": round_number(estimated_cac),
        "estimated_ltv": round_number(estimated_ltv),
        "ltv_cac_ratio": round_number(ltv_cac_ratio),
        "payback_months": round_number(payback_months),
        "break_even_customers": round_number(break_even_customers),
        "viability_warning": warning,
        "status": "inferred",
        "confidence": confidence,
        "source_origin": "financials_engine",
        "evidence_refs": evidence_refs,
        "source_refs": source_refs,
        "assumption_refs": [
            f"{company_id}-financial-assumption-lifetime",
            f"{company_id}-financial-assumption-cac",
            f"{company_id}-financial-assumption-costs"
        ],
        "finding_refs": [],
        "validated_fact_refs": [],
        "created_at": timestamp,
        "updated_at": timestamp
    }


def persist_financial_snapshot(root: Path, payload: dict, pricing_model: dict) -> Path:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    snapshot = build_financial_snapshot(payload, pricing_model)
    path = layout.record_path("financials", company_id, snapshot["snapshot_id"])
    layout.write_json_atomic(path, snapshot)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and persist a financial snapshot from JSON.")
    parser.add_argument("input", help="JSON fixture path")
    parser.add_argument("--pricing", required=True, help="Pricing model JSON path")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    pricing_model = json.loads(Path(args.pricing).read_text(encoding="utf-8"))
    print(persist_financial_snapshot(Path(args.root).resolve(), payload, pricing_model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
