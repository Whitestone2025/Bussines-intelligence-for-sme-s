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
        f"Ancla de costo mensual de entrega: {currency_code} {monthly_cost:,.2f}.",
        f"Ancla de precio de competidores: {currency_code} {competitor_anchor:,.2f}.",
        f"Ancla de valor percibido: {currency_code} {value_anchor:,.2f}.",
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
    target_segment = str(payload.get("target_segment", "")).strip() or "Negocios de servicios liderados por el fundador"
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
            "name": "Inicial",
            "price": round_money(target * 0.75),
            "fit": "Validacion rapida con menor alcance y menor carga de confianza.",
            "tradeoff": "Menor ingreso por cliente y menos margen para acompanamiento cercano.",
            "recommended": False,
        },
        {
            "name": "Base",
            "price": round_money(target),
            "fit": "Mejor balance de confianza, margen y claridad para la primera oferta en Mexico.",
            "tradeoff": "Todavia necesita un alcance explicito para no sentirse abstracta.",
            "recommended": True,
        },
        {
            "name": "Expandido",
            "price": round_money(ceiling),
            "fit": "Util cuando ya existen pruebas y demanda suficiente por una implementacion mas amplia.",
            "tradeoff": "Exige mas confianza y mas complejidad operativa.",
            "recommended": False,
        },
    ]
    implementation_risks = [
        "El nivel objetivo puede fallar si el alcance no se vuelve concreto durante la venta.",
        "Un precio por encima de la prueba visible puede generar friccion de confianza aunque la economia se vea fuerte.",
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
                "name": "Inicial",
                "price": round_money(target * 0.75),
                "value_summary": "Diagnostico enfocado y guia rapida de implementacion."
            },
            {
                "name": "Base",
                "price": round_money(target),
                "value_summary": "Oferta central completa con claridad de proceso y apoyo en mensaje comercial."
            },
            {
                "name": "Expandido",
                "price": round_money(ceiling),
                "value_summary": "Acompanamiento mas cercano con implementacion y optimizacion."
            }
        ],
        "pricing_options": pricing_options,
        "recommended_tier": "Base",
        "recommendation_logic": "Se recomienda empezar por Base porque balancea mejor confianza, alcance de entrega y proteccion de margen que Inicial o Expandido.",
        "margin_assumptions": [
            f"Se asume un costo mensual de entrega de {currency_code} {monthly_cost:,.2f}.",
            f"Se asume un margen bruto deseado de {desired_margin:.0%}.",
            f"Se asume un precio ancla de competidores de {currency_code} {competitor_anchor:,.2f}.",
            f"Se asume un ancla de valor de {currency_code} {value_anchor:,.2f}."
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
