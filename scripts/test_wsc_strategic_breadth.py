#!/usr/bin/env python3
"""Checks that the WSC web-only case produces real strategic breadth."""

from __future__ import annotations

from decision_engine import build_decision_memo


def payload() -> dict:
    return {
        "company_id": "wsc-lat",
        "company_name": "WS Capital",
        "website": "https://wsc.lat/",
        "available_sources": ["website"],
        "web_only_case": True,
        "business_goal": "aclarar que negocio visible existe hoy y que deberia validarse primero",
        "decision_question": "Que ruta estrategica deberia liderar primero WS Capital con la informacion publica disponible?",
        "evidence_count": 6,
        "source_count": 1,
        "has_icp": False,
        "has_offer": False,
        "market_confidence": 0.41,
        "pricing_confidence": 0.46,
        "channel_confidence": 0.22,
        "country_name": "Latinoamerica",
        "identity_tensions": [
            "La web mezcla AI Lab operativo, plataforma abierta de inteligencia y vehiculo de venture capital sin dejar claro cual es la cuña comercial dominante."
        ],
        "proof_gaps": [
            "La promesa 80/20 y la narrativa de infraestructura todavia no se apoyan en prueba publica suficiente de implementacion."
        ],
        "offer_anchor": "La unica monetizacion publica concreta hoy es el AI Lab de 1,500 USD al mes por 6 meses.",
        "known_unknowns": [
            "Todavia no sabemos con suficiente certeza si el comprador real es un fundador, una empresa cliente o un actor del ecosistema.",
        ],
        "public_claims": [
            "AI Lab & Venture Capital Hybrid",
            "80% Agentic | 20% Human",
            "McKinsey-Level Data for All",
        ],
    }


def main() -> int:
    memo = build_decision_memo(payload())
    stack = memo["strategic_stack"]
    options = stack["strategic_alternatives"]

    assert memo["decision_type"] == "viability"
    assert len(options) == 4, "Expected four real routes for the WSC web-only case."
    assert stack["recommended_route"]["alternative_id"] == "ai-lab-wedge"
    assert "ai lab" in stack["recommended_route"]["thesis"].lower()
    assert "1,500 usd" in stack["recommended_route"]["why_this_route_wins"].lower()
    assert any("plataforma" in item["label"].lower() for item in options)
    assert any("venture" in item["label"].lower() for item in options)
    assert any("prueba" in item["label"].lower() for item in options)
    assert any("ai lab" in item["thesis"].lower() for item in options)
    assert any("inteligencia abierta" in item["thesis"].lower() for item in options)
    assert any("venture builder" in item["thesis"].lower() or "holdco" in item["thesis"].lower() for item in options)
    assert all("{" not in item["thesis"] for item in options), "Unexpected template placeholder in route thesis."
    assert len(memo["alternative_actions"]) == 3
    assert all(not action.lower().startswith("lanza ") for action in memo["alternative_actions"])
    assert stack["recommended_route"]["invalidation_conditions"], "Expected explicit invalidation conditions."

    print("WSC strategic breadth checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
