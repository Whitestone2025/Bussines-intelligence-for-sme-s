#!/usr/bin/env python3
"""Checks that WSC web-only deliverables are useful and explicit about limits."""

from __future__ import annotations

from render_report import render_bundle


def bundle() -> dict:
    return {
        "company": {
            "company_id": "wsc-lat",
            "name": "WS Capital",
            "seed_summary": "Firma que se presenta como AI Lab y Venture Capital Hybrid para Latinoamerica, con foco en infraestructura agentic e inteligencia abierta.",
            "primary_country": "MX",
            "known_constraints": [
                "Solo se usa la web publica como fuente inicial.",
                "No hay entrevistas, pricing interno ni evidencia operativa privada.",
            ],
        },
        "decision_question": "Que ruta estrategica deberia liderar primero WS Capital con la informacion publica disponible?",
        "current_thesis": "La tesis actual no es una recomendacion de ejecucion, sino una lectura provisional para decidir que identidad comercial merece validarse primero.",
        "validated_facts": [
            "La web publica presenta a WS Capital como AI Lab y Venture Capital Hybrid.",
            "La unica oferta con precio visible es el AI Lab de 1,500 USD al mes por 6 meses.",
            "La homepage tambien muestra una Open Intel Platform y varias unidades activas mas alla del AI Lab.",
        ],
        "inferences": [
            "La friccion principal hoy parece ser de claridad estrategica y no de ejecucion de canal.",
            "La mezcla entre AI Lab, plataforma abierta y venture hybrid exige elegir una cuña antes de ampliar la narrativa.",
        ],
        "validation_gaps": [
            "Agrega al menos 2 fuentes distintas para subir la confianza de lectura.",
            "Aclara mejor la oferta antes de recomendar ejecucion.",
            "Define mejor a quien compras antes de elegir canal o precio.",
        ],
        "contrary_evidence": [
            "La promesa 80/20 y la narrativa de infraestructura todavia no se apoyan en prueba publica suficiente de implementacion.",
        ],
        "decision_criteria": [
            "Velocidad para obtener aprendizaje creible de mercado.",
            "Ajuste con la capacidad real de ejecucion del fundador.",
            "Confianza suficiente en canal y claridad de oferta.",
            "Economia suficientemente sana para justificar la prueba.",
        ],
        "assumptions": [
            "La web actual probablemente mezcla una cuña comercial real con una narrativa mas amplia de portafolio e infraestructura.",
            "Todavia no sabemos con suficiente certeza si el comprador real es un fundador, una empresa cliente o un actor del ecosistema.",
        ],
        "execution_realities": [
            "Con solo una web publica, la primera utilidad del sistema es ordenar la decision y mostrar vacios, no prometer salida al mercado inmediata.",
        ],
        "options": [],
        "icp": {
            "label": "Comprador aun no confirmado desde la web publica",
            "pains": [],
            "desired_outcomes": [],
        },
        "offer": {
            "name": "AI Lab como cuña comercial provisional",
            "core_promise": "Usar la unica oferta con monetizacion visible como punto de entrada mientras se valida si esa identidad merece liderar el negocio.",
            "mechanism": "Primero ordenar identidad, prueba y cuña comercial antes de escalar una ruta de mercado.",
            "proof_points": [
                "Precio visible de 1,500 USD al mes por 6 meses",
                "Capacidad publica limitada en el AI Lab",
            ],
        },
        "market_model": {
            "segment_name": "Mercado latinoamericano aun por estructurar",
            "blended_value": 0,
            "currency_code": "USD",
            "key_assumptions": [
                "Con solo la web publica no se puede estimar un mercado defendible con confianza suficiente.",
            ],
            "assumption_refs": ["wsc-lat-market-assumption-web-only"],
        },
        "pricing_model": {
            "price_floor": 1500,
            "price_target": 1500,
            "price_ceiling": 1500,
            "currency_code": "USD",
            "margin_assumptions": [
                "El precio visible del AI Lab todavia no confirma economics ni disposicion real a pagar.",
            ],
            "assumption_refs": ["wsc-lat-pricing-assumption-web-only"],
        },
        "decision_memo": {
            "recommended_action": "Usar el AI Lab como cuña comercial dominante de WS Capital mientras se valida si esa identidad merece liderar la narrativa publica.",
            "why_now": "Hoy esta ruta gana porque es la unica con monetizacion publica concreta y reduce mejor la ambiguedad del caso.",
            "decision_summary": "aclarar que negocio visible existe hoy y que deberia validarse primero",
            "decision_question": "Que ruta estrategica deberia liderar primero WS Capital con la informacion publica disponible?",
            "decision_criteria": [
                "Velocidad para obtener aprendizaje creible de mercado.",
                "Ajuste con la capacidad real de ejecucion del fundador.",
                "Confianza suficiente en canal y claridad de oferta.",
                "Economia suficientemente sana para justificar la prueba.",
            ],
            "fact_base": [
                "Evidencias disponibles: 6.",
                "Fuentes distintas disponibles: 1.",
                "La unica monetizacion publica concreta hoy es el AI Lab de 1,500 USD al mes por 6 meses.",
            ],
            "assumptions": [
                "Todavia no sabemos con suficiente certeza si el comprador real es un fundador, una empresa cliente o un actor del ecosistema.",
            ],
            "key_risks": [
                "La promesa 80/20 y la narrativa de infraestructura todavia no se apoyan en prueba publica suficiente de implementacion.",
                "La cuña AI Lab puede encoger demasiado la lectura del negocio si la identidad venture hybrid era la puerta correcta.",
            ],
            "validation_gaps": [
                "Agrega al menos 2 fuentes distintas para subir la confianza de lectura.",
                "Aclara mejor la oferta antes de recomendar ejecucion.",
                "Define mejor a quien compras antes de elegir canal o precio.",
            ],
            "next_steps": [
                "Valida mejor quien compra, como compra y que objecion aparece primero.",
                "Aterriza mejor la oferta y explica con claridad como se entrega el servicio.",
            ],
            "evidence_refs": [
                "2026-03-18-wsc-positioning-hybrid",
                "2026-03-18-wsc-ai-lab-offer",
            ],
            "assumption_refs": ["wsc-lat-decision-assumption-readiness"],
            "strategic_stack": {
                "problem_statement": {
                    "headline": "WS Capital todavia no resuelve que identidad comercial debe liderar la narrativa publica.",
                    "situation": "La lectura actual parte solo de la web publica y mezcla AI Lab, plataforma abierta e identidad venture hybrid.",
                    "complication": "La unica oferta con precio visible convive con una narrativa mucho mas amplia que no esta ordenada comercialmente.",
                    "decision_tension": "La ambiguedad actual impide recomendar ejecucion con seguridad.",
                    "key_question": "Que ruta estrategica deberia liderar primero WS Capital con la informacion publica disponible?",
                },
                "case_for_change": {
                    "why_change": "Mientras la identidad dominante no se aclare, cualquier esfuerzo comercial arranca con friccion de entendimiento.",
                    "cost_of_inaction": "La amplitud narrativa puede seguir pareciendo vision sin prueba suficiente.",
                    "transformation_story": "El cambio inmediato no es de canal, sino de claridad estrategica y prueba visible.",
                },
                "where_to_play": {
                    "primary_segment": "segmento comprador aun no confirmado desde la web publica",
                    "primary_channel": "canal aun no confirmado",
                    "geographic_focus": "Latinoamerica",
                },
                "how_to_win": {
                    "value_thesis": "Ganar aclarando primero cual es la cuña comercial dominante.",
                    "differentiation": "La ventaja no viene del manifiesto solo; tiene que venir de una promesa mas concreta y verificable.",
                    "proof": "Hoy la prueba publica sigue siendo insuficiente para sostener toda la amplitud de la narrativa visible.",
                },
                "right_to_win": [
                    "La empresa necesita explicar con claridad como se entrega la oferta.",
                    "La evidencia todavia no es suficientemente fuerte para reclamar una ventaja defensible permanente.",
                ],
                "strategic_alternatives": [
                    {
                        "alternative_id": "ai-lab-wedge",
                        "label": "Ruta de cuña comercial AI Lab",
                        "thesis": "Usar el AI Lab como cuña comercial dominante de WS Capital, tratando la narrativa venture hybrid y la plataforma abierta como apuestas de segundo plano hasta que exista una prueba publica mas fuerte.",
                        "route_type": "where_to_play",
                        "why_this_route": "Es la unica ruta con monetizacion publica concreta hoy y por eso reduce mejor la ambiguedad del caso.",
                        "criteria_fit": "Velocidad para obtener aprendizaje creible de mercado.",
                        "key_bets": [
                            "El mercado puede entender primero una oferta concreta antes que una arquitectura completa de identidades.",
                        ],
                        "key_risks": [
                            "La cuña AI Lab puede encoger demasiado la lectura del negocio si la identidad venture hybrid era la puerta correcta.",
                        ],
                        "what_must_be_true": [
                            "El AI Lab debe ser suficientemente comprable y explicable como oferta inicial.",
                        ],
                        "recommended": True,
                    },
                    {
                        "alternative_id": "open-intel-platform",
                        "label": "Ruta de plataforma de inteligencia abierta",
                        "thesis": "Tomar la promesa de inteligencia abierta como producto lider, tratando el AI Lab como servicio de acompañamiento y dejando la narrativa venture como capa posterior.",
                        "route_type": "where_to_play",
                        "why_this_route": "Podria escalar mejor si la promesa abierta de inteligencia de verdad funciona como producto.",
                        "criteria_fit": "Confianza suficiente en canal y claridad de oferta.",
                        "key_bets": [
                            "La promesa abierta de inteligencia puede atraer un mercado mas amplio.",
                        ],
                        "key_risks": [
                            "La plataforma todavia parece mas manifiesto que producto listo.",
                        ],
                        "what_must_be_true": [
                            "La plataforma debe resolver un trabajo concreto y repetible.",
                        ],
                        "recommended": False,
                    },
                ],
                "what_must_be_true": [
                    "El AI Lab debe ser suficientemente comprable y explicable como oferta inicial.",
                ],
                "no_regret_moves": [
                    "Separar hechos, inferencias y supuestos antes de escalar la recomendacion.",
                ],
                "recommended_route": {
                    "alternative_id": "ai-lab-wedge",
                    "label": "Ruta de cuña comercial AI Lab",
                    "thesis": "Usar el AI Lab como cuña comercial dominante de WS Capital, tratando la narrativa venture hybrid y la plataforma abierta como apuestas de segundo plano hasta que exista una prueba publica mas fuerte.",
                    "why_this_route_wins": "Hoy esta ruta gana porque es la unica con monetizacion publica concreta y reduce mejor la ambiguedad del caso.",
                    "invalidation_conditions": [
                        "La cuña AI Lab puede encoger demasiado la lectura del negocio si la identidad venture hybrid era la puerta correcta.",
                    ],
                },
            },
        },
        "execution_plan": {
            "objective": "Decidir si el AI Lab merece liderar la lectura comercial del negocio antes de ampliar la narrativa.",
            "decision_checkpoints": [
                "Confirmar si el AI Lab es la cuña comercial dominante o solo una expresion parcial del negocio.",
                "Decidir si la falta de prueba publica obliga a priorizar casos y evidencia antes de cualquier expansion narrativa.",
            ],
            "initiative_roadmap": [
                {
                    "stage_gate": "Gate 1",
                    "name": "Alinear cuña comercial y narrativa publica",
                    "objective": "Traducir la recomendacion a una tesis operativa entendible por el fundador y por el mercado.",
                    "workstream": "Alineacion estrategica",
                    "owner": "Fundador",
                    "timeframe": "Dias 1-30",
                    "dependencies": ["wsc-lat-viability-memo"],
                    "leading_indicator": "La tesis puede explicarse sin mezclar AI Lab, plataforma y venture hybrid en la misma frase.",
                    "lagging_indicator": "La lectura del negocio deja de sentirse como manifiesto mezclado.",
                    "stage_gate_question": "La cuña comercial ya quedo lo bastante clara como para probarse?",
                    "decision_trigger": "Si la tesis sigue cambiando en cada explicacion, el caso aun no esta listo para ir al mercado.",
                    "exit_criteria": "Existe una lectura unica del problema, de la oferta de entrada y de la senal que confirmaria o invalidaria la ruta.",
                    "key_risks": [
                        "La falta de prueba visible puede seguir bloqueando confianza aunque la narrativa mejore.",
                    ],
                    "risk_mitigation": [
                        "Separar hechos, inferencias y supuestos antes de mover recursos.",
                    ],
                }
            ],
            "milestones": [
                {
                    "name": "Alinear cuña comercial y narrativa publica",
                    "timeframe": "Dias 1-30",
                    "success_metric": "Tesis, problema del comprador y cuña inicial alineados en un solo memo ejecutivo.",
                }
            ],
        },
    }


def main() -> int:
    deliverables = render_bundle(bundle())

    executive = deliverables["executive-memo"]
    diagnosis = deliverables["business-diagnosis"]
    options = deliverables["strategic-options-memo"]
    decision = deliverables["decision-document"]
    roadmap = deliverables["initiative-roadmap"]

    assert "Te sirve para" in executive
    assert "Te sirve para" in diagnosis
    assert "Te sirve para" in options
    assert "Te sirve para" in decision
    assert "Te sirve para" in roadmap
    assert "## Limites de evidencia hoy" in executive
    assert "Solo se usa la web publica como fuente inicial." in executive
    assert "No hay entrevistas, pricing interno ni evidencia operativa privada." in decision
    assert "Que ruta estrategica deberia liderar primero WS Capital" in executive
    assert "Ruta de cuña comercial AI Lab" in options
    assert "Ruta de plataforma de inteligencia abierta" in options
    assert "no es una recomendacion de ejecucion" in diagnosis.lower()
    assert "economics" not in (executive + diagnosis + options + decision + roadmap).lower()
    assert "open source" not in (executive + diagnosis + options + decision + roadmap).lower()
    assert "right to win" not in (executive + diagnosis + options + decision + roadmap).lower()
    assert " founder" not in (executive + diagnosis + options + decision + roadmap).lower()

    print("WSC case usefulness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
