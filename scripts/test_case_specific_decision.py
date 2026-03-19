#!/usr/bin/env python3
"""Checks that decision recommendations adapt to the case instead of reusing one generic playbook."""

from __future__ import annotations

from decision_engine import build_decision_memo


def founder_payload() -> dict:
    return {
        "company_id": "decision-founder",
        "evidence_count": 6,
        "source_count": 3,
        "has_icp": True,
        "has_offer": True,
        "market_confidence": 0.74,
        "pricing_confidence": 0.66,
        "channel_confidence": 0.79,
        "business_goal": "mejorar la calidad de conversion en ventas de servicios",
        "primary_channel": "WhatsApp",
        "service_name": "Sprint de claridad comercial",
        "dominant_objection": "suena como cualquier agencia",
    }


def ops_payload() -> dict:
    return {
        "company_id": "decision-ops",
        "evidence_count": 7,
        "source_count": 4,
        "has_icp": True,
        "has_offer": True,
        "market_confidence": 0.7,
        "pricing_confidence": 0.61,
        "channel_confidence": 0.71,
        "business_goal": "reducir riesgo operativo antes del evento",
        "primary_channel": "Referidos",
        "service_name": "Validacion operativa de eventos",
        "dominant_objection": "temen agregar complejidad al proceso",
    }


def main() -> int:
    founder = build_decision_memo(founder_payload())
    ops = build_decision_memo(ops_payload())

    assert founder["recommended_action"] != ops["recommended_action"], "Decision recommendations should differ by case."
    assert "whatsapp" in founder["recommended_action"].lower()
    assert "referidos" in ops["recommended_action"].lower()
    assert "sprint de claridad comercial" in founder["recommended_action"].lower()
    assert "validacion operativa de eventos" in ops["recommended_action"].lower()
    assert founder["strategic_stack"]["recommended_route"]["why_this_route_wins"] != ops["strategic_stack"]["recommended_route"]["why_this_route_wins"]
    assert founder["alternative_actions"] != ops["alternative_actions"]
    assert "lanza una primera prueba comercial" not in founder["recommended_action"].lower()

    print("Case-specific decision checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
