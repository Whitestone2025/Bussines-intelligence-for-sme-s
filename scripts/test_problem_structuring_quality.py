#!/usr/bin/env python3
"""Checks that reports expose problem structuring before recommendation."""

from __future__ import annotations

import json
from pathlib import Path

from decision_engine import build_decision_memo
from render_report import render_bundle


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    bundle = json.loads((ROOT / "data" / "tests" / "fixtures" / "deliverables" / "report-input.json").read_text(encoding="utf-8"))
    rendered = render_bundle(bundle)

    executive = rendered["executive-memo"]
    diagnosis = rendered["business-diagnosis"]

    assert executive.index("## Problema estructurado") < executive.index("## Ruta provisional recomendada")
    assert executive.index("## Hechos validados") < executive.index("## Ruta provisional recomendada")
    assert executive.index("## Inferencias principales") < executive.index("## Ruta provisional recomendada")
    assert executive.index("## Supuestos de trabajo") < executive.index("## Ruta provisional recomendada")
    assert "## Lo que tendria que ser cierto" in executive

    assert diagnosis.index("## Problema central") < diagnosis.index("## Recomendacion actual")
    assert diagnosis.index("## Lo que sabemos") < diagnosis.index("## Recomendacion actual")
    assert diagnosis.index("## Lo que inferimos") < diagnosis.index("## Recomendacion actual")
    assert diagnosis.index("## Supuestos de trabajo") < diagnosis.index("## Recomendacion actual")

    wsc_memo = build_decision_memo(
        {
            "company_id": "wsc-lat",
            "company_name": "WS Capital",
            "website": "https://wsc.lat/",
            "available_sources": ["website"],
            "web_only_case": True,
            "business_goal": "aclarar que negocio visible existe hoy y que deberia validarse primero",
            "decision_question": "Que problema estrategico real tiene hoy WS Capital con la informacion publica disponible?",
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
    )

    wsc_bundle = {
        "company": {
            "company_id": "wsc-lat",
            "name": "WS Capital",
            "seed_summary": "Firma que se presenta como AI Lab y un hibrido de venture capital para Latinoamerica, con foco en infraestructura agentic e inteligencia abierta.",
        },
        "decision_question": wsc_memo["decision_question"],
        "current_thesis": "La tesis actual sigue siendo provisional porque la web mezcla varias identidades y todavia no resuelve cual lidera la venta.",
        "validated_facts": [
            "La web publica se presenta como AI Lab y Venture Capital Hybrid.",
            "Existe una oferta visible de AI Lab con precio publico de 1,500 USD al mes por 6 meses.",
            "Tambien existe una promesa abierta de inteligencia y varias unidades activas visibles.",
        ],
        "inferences": [
            "La friccion principal hoy parece ser de claridad estrategica y no solo de ejecucion comercial.",
            "La oferta visible todavia no ordena por si sola toda la narrativa del negocio.",
        ],
        "validation_gaps": [
            "Falta confirmar quien compra realmente y que oferta deberia liderar.",
            "Falta evidencia publica suficiente de implementacion o resultados.",
        ],
        "contrary_evidence": [
            "La misma amplitud narrativa puede hacer que el mercado no entienda que se vende primero.",
        ],
        "decision_criteria": [
            "Reducir ambiguedad estrategica antes de escalar una ruta comercial.",
            "Preservar cautela epistemica cuando la evidencia publica es limitada.",
        ],
        "assumptions": [
            "La web actual refleja una mezcla real de identidades y no solo un problema de copy.",
        ],
        "execution_realities": [
            "Con solo la web publica, la primera decision correcta es estructurar el problema antes de elegir canal.",
        ],
        "options": [],
        "icp": {
            "label": "Comprador todavia no confirmado",
            "pains": [],
            "desired_outcomes": [],
        },
        "offer": {
            "name": "Oferta dominante todavia no confirmada",
            "core_promise": "La oferta visible actual no alcanza todavia para fijar una tesis comercial unica.",
            "mechanism": "Primero hay que ordenar identidad, prueba y cuña comercial.",
            "proof_points": ["AI Lab con precio visible", "Portafolio de unidades activas"],
        },
        "market_model": {
            "segment_name": "Mercado latinoamericano aun por estructurar",
            "blended_value": 0,
            "currency_code": "USD",
            "key_assumptions": ["La web por si sola no basta para estimar mercado defendible."],
        },
        "pricing_model": {
            "price_floor": 1500,
            "price_target": 1500,
            "price_ceiling": 1500,
            "currency_code": "USD",
        },
        "decision_memo": wsc_memo,
        "execution_plan": {
            "milestones": [],
            "decision_checkpoints": [
                "Confirmar si el AI Lab es la cuña comercial dominante o solo una expresion parcial del negocio.",
            ],
            "initiative_roadmap": [],
        },
    }

    wsc_rendered = render_bundle(wsc_bundle)
    wsc_exec = wsc_rendered["executive-memo"]
    wsc_problem = wsc_rendered["problem-structuring-memo"]
    assert "AI Lab operativo, plataforma abierta de inteligencia y vehiculo de venture capital" in wsc_exec
    assert "La unica monetizacion publica concreta hoy es el AI Lab de 1,500 USD al mes por 6 meses." in wsc_problem
    assert "La promesa 80/20 y la narrativa de infraestructura todavia no se apoyan en prueba publica suficiente de implementacion." in wsc_problem
    assert "Todavia no sabemos con suficiente certeza si el comprador real es un fundador, una empresa cliente o un actor del ecosistema." in wsc_exec

    print("Problem structuring quality checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
