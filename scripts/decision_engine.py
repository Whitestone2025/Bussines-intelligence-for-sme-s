#!/usr/bin/env python3
"""Decision engine and readiness gate for Codex Business OS MX."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def unique_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        normalized = str(item).strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)
    return ordered


def web_only_payload(payload: dict) -> bool:
    if bool(payload.get("web_only_case")):
        return True
    available_sources = [str(item).strip().lower() for item in payload.get("available_sources", []) if str(item).strip()]
    return bool(payload.get("website")) and bool(available_sources) and set(available_sources) <= {"website"}


def first_non_empty(*values: object) -> str:
    for value in values:
        normalized = str(value or "").strip()
        if normalized:
            return normalized
    return ""


def decision_question(payload: dict) -> str:
    business_goal = str(payload.get("business_goal", "")).strip()
    if business_goal:
        return f"Cual es el siguiente movimiento de mayor confianza para {business_goal.lower()}?"
    return "Cual es el siguiente movimiento que mas reduce incertidumbre sin perder traccion comercial?"


def decision_criteria(payload: dict) -> list[str]:
    criteria = [str(item).strip() for item in payload.get("decision_criteria", []) if str(item).strip()]
    if criteria:
        return criteria
    return [
        "Velocidad para obtener aprendizaje creible de mercado.",
        "Ajuste con la capacidad real de ejecucion del fundador.",
        "Confianza suficiente en canal y claridad de oferta.",
        "Economia suficientemente sana para justificar la prueba.",
    ]


def strategic_problem_statement(payload: dict, readiness: dict) -> dict:
    if web_only_payload(payload):
        company_name = str(payload.get("company_name", "")).strip() or str(payload.get("company_id", "")).strip() or "La empresa"
        identity_tensions = [str(item).strip() for item in payload.get("identity_tensions", []) if str(item).strip()]
        proof_gaps = [str(item).strip() for item in payload.get("proof_gaps", []) if str(item).strip()]
        offer_anchor = first_non_empty(payload.get("offer_anchor", ""))
        public_claims = [str(item).strip() for item in payload.get("public_claims", []) if str(item).strip()]
        return {
            "headline": first_non_empty(
                payload.get("problem_headline", ""),
                f"{company_name} todavia no resuelve que identidad comercial debe liderar la narrativa publica.",
            ),
            "situation": first_non_empty(
                payload.get("current_state", ""),
                "La lectura actual parte solo de la web publica y mezcla una narrativa de AI Lab, plataforma abierta e identidad hibrida de venture capital.",
            ),
            "complication": first_non_empty(
                identity_tensions[0] if identity_tensions else "",
                offer_anchor,
                "La oferta visible y la identidad del negocio todavia no quedan alineadas.",
            ),
            "decision_tension": first_non_empty(
                proof_gaps[0] if proof_gaps else "",
                "La web promete mas de una cosa al mismo tiempo, pero aun no muestra suficiente prueba publica para cerrar una tesis unica.",
            ),
            "key_question": first_non_empty(
                payload.get("decision_question", ""),
                f"Que identidad deberia liderar primero {company_name} para que el mercado entienda que vende hoy y por que debe creerle?",
            ),
            "public_claims": public_claims,
        }

    business_goal = str(payload.get("business_goal", "")).strip() or "mejorar la calidad de conversion"
    dominant_objection = str(payload.get("dominant_objection", "")).strip()
    service_name = str(payload.get("offer_name", "") or payload.get("service_name", "")).strip() or "la oferta principal"
    complication = (
        f"La objecion dominante hoy es '{dominant_objection}'."
        if dominant_objection
        else "Todavia no existe una objecion dominante suficientemente clara."
    )
    readiness_state = (
        "La base minima para decidir ya existe."
        if readiness["status"] == "ready"
        else "La base para decidir sigue incompleta y obliga a validar antes de ejecutar."
    )
    return {
        "headline": f"El sistema debe decidir como {business_goal.lower()} sin diluir {service_name.lower()}.",
        "situation": f"El caso busca {business_goal.lower()} con una oferta que hoy gira alrededor de {service_name.lower()}.",
        "complication": complication,
        "decision_tension": readiness_state,
        "key_question": decision_question(payload),
    }


def strategic_case_for_change(payload: dict, readiness: dict) -> dict:
    if web_only_payload(payload):
        proof_gaps = [str(item).strip() for item in payload.get("proof_gaps", []) if str(item).strip()]
        known_unknowns = [str(item).strip() for item in payload.get("known_unknowns", []) if str(item).strip()]
        return {
            "why_change": first_non_empty(
                payload.get("why_change", ""),
                "Mientras la web siga mezclando identidades sin una cuña comercial dominante, cada nueva accion comercial arranca con friccion de entendimiento.",
            ),
            "cost_of_inaction": first_non_empty(
                payload.get("cost_of_inaction", ""),
                proof_gaps[0] if proof_gaps else "",
                "Si no se aclara la identidad comercial dominante, el mercado seguira leyendo varias promesas sin saber cual comprar primero.",
            ),
            "transformation_story": first_non_empty(
                payload.get("transformation_story", ""),
                known_unknowns[0] if known_unknowns else "",
                "La primera transformacion no es de canal sino de claridad estrategica: pasar de manifiesto mixto a tesis comercial comprobable.",
            ),
        }

    blockers = list(readiness.get("blocking_reasons", []))
    urgency = (
        "La empresa ya tiene suficiente estructura para tomar una postura y mover el caso."
        if readiness["status"] == "ready"
        else "El sistema todavia esta demasiado cerca de la especulacion y necesita reducir vacios de validacion."
    )
    inaction_risk = (
        blockers[0]
        if blockers
        else "Si no se define una tesis clara, el caso seguira pareciendo una serie de acciones sueltas en lugar de una ruta estrategica."
    )
    return {
        "why_change": urgency,
        "cost_of_inaction": inaction_risk,
        "transformation_story": "La recomendacion debe conectar problema, comprador, economia y secuencia de ejecucion; no solo proponer una tarea.",
    }


def strategic_where_to_play(payload: dict) -> dict:
    if web_only_payload(payload):
        return {
            "primary_segment": first_non_empty(payload.get("target_segment", ""), "segmento comprador aun no confirmado desde la web publica"),
            "primary_channel": first_non_empty(payload.get("primary_channel", ""), "canal aun no confirmado"),
            "geographic_focus": str(payload.get("country_name", "")).strip() or "Latinoamerica",
        }
    return {
        "primary_segment": str(payload.get("target_segment", "")).strip() or str(payload.get("business_goal", "")).strip() or "segmento principal por validar",
        "primary_channel": str(payload.get("primary_channel", "")).strip() or "canal principal por definir",
        "geographic_focus": str(payload.get("country_name", "")).strip() or "Mexico",
    }


def strategic_how_to_win(payload: dict) -> dict:
    if web_only_payload(payload):
        return {
            "value_thesis": first_non_empty(
                payload.get("value_thesis", ""),
                "Ganar aclarando primero cual es la oferta comercial dominante y mostrando prueba visible antes de ampliar la narrativa.",
            ),
            "differentiation": first_non_empty(
                payload.get("differentiation", ""),
                "La ventaja no viene solo del manifiesto; tiene que venir de una promesa mas concreta y verificable que la mezcla actual de identidades.",
            ),
            "proof": first_non_empty(
                payload.get("proof_statement", ""),
                "Hoy la prueba publica sigue siendo insuficiente para sostener toda la amplitud de la narrativa visible.",
            ),
        }
    service_name = str(payload.get("offer_name", "") or payload.get("service_name", "")).strip() or "la oferta principal"
    dominant_objection = str(payload.get("dominant_objection", "")).strip()
    value_thesis = (
        f"Ganar demostrando por que {service_name.lower()} resuelve mejor el problema que las alternativas actuales."
    )
    differentiation = (
        f"Bajar la objecion '{dominant_objection}' con una propuesta mas especifica y defendible."
        if dominant_objection
        else "Volver la propuesta mas especifica, trazable y facil de creer."
    )
    return {
        "value_thesis": value_thesis,
        "differentiation": differentiation,
        "proof": "La recomendacion debe apoyarse en evidencia, economics, capacidad real de ejecucion y una ruta clara hacia aprendizaje.",
    }


def strategic_right_to_win(payload: dict, readiness: dict) -> list[str]:
    service_name = str(payload.get("offer_name", "") or payload.get("service_name", "")).strip() or "la oferta"
    channel_name = str(payload.get("primary_channel", "")).strip() or "el canal principal"
    foundations = [
        f"La empresa necesita explicar con claridad como se entrega {service_name.lower()}.",
        f"El primer canal debe ser compatible con la capacidad operativa real del fundador: {channel_name}.",
    ]
    if readiness["status"] != "ready":
        foundations.append("La evidencia todavia no es suficientemente fuerte para reclamar una ventaja defensible permanente.")
    else:
        foundations.append("La empresa ya tiene minima base de evidencia para sostener una primera tesis competitiva.")
    return foundations


def strategic_alternatives(payload: dict, readiness: dict, actions: list[str], criteria: list[str]) -> list[dict]:
    if web_only_payload(payload):
        company_name = str(payload.get("company_name", "")).strip() or str(payload.get("company_id", "")).strip() or "La empresa"
        geographic_focus = str(payload.get("country_name", "")).strip() or "Latinoamerica"
        offer_anchor = first_non_empty(
            payload.get("offer_anchor", ""),
            "La unica monetizacion publica concreta hoy es el AI Lab visible en la web.",
        )
        public_claims = [str(item).strip() for item in payload.get("public_claims", []) if str(item).strip()]
        identity_tensions = [str(item).strip() for item in payload.get("identity_tensions", []) if str(item).strip()]
        proof_gaps = [str(item).strip() for item in payload.get("proof_gaps", []) if str(item).strip()]
        known_unknowns = [str(item).strip() for item in payload.get("known_unknowns", []) if str(item).strip()]
        primary_tension = first_non_empty(
            identity_tensions[0] if identity_tensions else "",
            "La identidad comercial dominante sigue sin resolverse publicamente.",
        )
        primary_gap = first_non_empty(
            proof_gaps[0] if proof_gaps else "",
            "La promesa publica todavia no tiene suficiente prueba visible.",
        )
        unknown_buyer = first_non_empty(
            known_unknowns[0] if known_unknowns else "",
            "Todavia no sabemos con suficiente certeza quien compra realmente primero.",
        )
        alternatives: list[dict] = [
            {
                "alternative_id": "ai-lab-wedge",
                "label": "Ruta de cuña comercial AI Lab",
                "thesis": (
                    f"Usar el AI Lab como cuña comercial dominante de {company_name}, "
                    "tratando la narrativa hibrida de venture capital y la plataforma abierta como apuestas de segundo plano "
                    "hasta que exista una prueba publica mas fuerte."
                ),
                "route_type": "where_to_play",
                "why_this_route": (
                    f"Es la unica ruta con monetizacion publica concreta hoy ({offer_anchor}) "
                    "y por eso reduce mas rapido la ambiguedad entre lo que el sitio inspira y lo que realmente puede venderse primero."
                ),
                "criteria_fit": criteria[0] if criteria else "",
                "key_bets": [
                    "El mercado puede entender primero una oferta concreta antes que una arquitectura completa de identidades.",
                    "La cuña AI Lab puede producir aprendizaje comercial sin negar la ambicion mas amplia del negocio.",
                ],
                "key_risks": [
                    primary_gap,
                    "La cuña AI Lab puede encoger demasiado la lectura del negocio si la identidad hibrida de venture capital era la puerta correcta.",
                ],
                "what_must_be_true": [
                    "El AI Lab debe ser suficientemente comprable y explicable como oferta inicial.",
                    "La narrativa abierta y venture puede quedar subordinada sin romper la credibilidad general del caso.",
                ],
                "recommended": True,
            },
            {
                "alternative_id": "proof-before-scale",
                "label": "Ruta de prueba antes de expansion",
                "thesis": (
                    "Congelar temporalmente la amplitud narrativa y usar el sitio solo para demostrar como opera el modelo 80/20, "
                    "que resultados produce y en que tipo de cliente ya funciona."
                ),
                "route_type": "how_to_win",
                "why_this_route": (
                    "Sirve cuando la mayor friccion no es la falta de vision sino la falta de prueba visible para creer la vision."
                ),
                "criteria_fit": criteria[min(1, len(criteria) - 1)] if criteria else "",
                "key_bets": [
                    "Una prueba publica clara puede ordenar despues cualquiera de las identidades visibles.",
                    "La credibilidad perdida por ambiguedad se recupera mejor con evidencia que con mas manifiesto.",
                ],
                "key_risks": [
                    "Puede retrasar demasiado la venta si se convierte en una espera indefinida de prueba perfecta.",
                    unknown_buyer,
                ],
                "what_must_be_true": [
                    "Existe una forma realista de mostrar implementacion sin revelar informacion sensible.",
                    "La ausencia de prueba es hoy un freno mayor que la ausencia de awareness.",
                ],
                "recommended": False,
            },
            {
                "alternative_id": "open-intel-platform",
                "label": "Ruta de plataforma de inteligencia abierta",
                "thesis": (
                    "Tomar la promesa de inteligencia abierta como producto lider, tratando el AI Lab como servicio de acompañamiento "
                    "y dejando la narrativa venture como capa posterior."
                ),
                "route_type": "where_to_play",
                "why_this_route": (
                    "Aprovecha una tesis visible de democratizacion de inteligencia que podria escalar mejor que una oferta de servicio artesanal."
                ),
                "criteria_fit": criteria[min(2, len(criteria) - 1)] if criteria else "",
                "key_bets": [
                    "La promesa publica 'McKinsey-Level Data for All' puede atraer un mercado mas amplio que el AI Lab.",
                    "El ecosistema de codigo abierto puede servir como motor de distribucion y credibilidad.",
                ],
                "key_risks": [
                    "La plataforma todavia parece mas manifiesto que producto listo para liderar una venta.",
                    "Puede abrir un frente demasiado grande sin comprador ni economia visible.",
                ],
                "what_must_be_true": [
                    "La plataforma abierta debe resolver un trabajo concreto y repetible para un comprador real.",
                    "El negocio debe poder explicar como conviven codigo abierto, servicio y captura de valor.",
                ],
                "recommended": False,
            },
            {
                "alternative_id": "venture-hybrid-holdco",
                "label": "Ruta hibrida de venture capital como tesis principal",
                "thesis": (
                    f"Ordenar a {company_name} primero como venture builder o holdco regional, "
                    f"tratando el AI Lab y la plataforma abierta como capacidades internas para originar, operar e invertir en {geographic_focus}."
                ),
                "route_type": "right_to_win",
                "why_this_route": (
                    "Convierte la mezcla actual de unidades, infraestructura y capital en una historia mas coherente si el negocio de verdad quiere jugar como plataforma de construccion e inversion."
                ),
                "criteria_fit": criteria[min(3, len(criteria) - 1)] if criteria else "",
                "key_bets": [
                    "La mezcla de unidades activas y narrativa de infraestructura realmente responde a una tesis de portafolio y no solo a un problema de copy.",
                    "El mercado correcto valora mas el acceso a capacidades y capital que una oferta puntual de servicio.",
                ],
                "key_risks": [
                    primary_tension,
                    "Es la ruta mas dificil de creer hoy porque la prueba publica de derecho a ganar sigue siendo limitada.",
                ],
                "what_must_be_true": [
                    "Debe existir evidencia suficiente de capacidad para operar, seleccionar e invertir mejor que alternativas mas simples.",
                    "La audiencia prioritaria debe entender y comprar una tesis hibrida de venture capital desde la web publica.",
                ],
                "recommended": False,
            },
        ]
        if public_claims:
            alternatives[2]["key_bets"].append(
                f"La promesa publica '{public_claims[-1]}' puede funcionar como cuña de distribucion si se vuelve mas concreta."
            )
        return alternatives[:4]

    service_name = str(payload.get("offer_name", "") or payload.get("service_name", "")).strip() or "la oferta principal"
    channel_name = str(payload.get("primary_channel", "")).strip() or "el canal con mejor senal actual"
    business_goal = str(payload.get("business_goal", "")).strip() or "mejorar la calidad de conversion"
    dominant_objection = str(payload.get("dominant_objection", "")).strip()
    alternatives: list[dict] = []
    alternatives.append(
        {
            "alternative_id": "focus-wedge",
            "label": "Ruta de foco comercial",
            "thesis": (
                f"Entrar por {channel_name} con una propuesta acotada de {service_name.lower()} "
                f"para mejorar {business_goal.lower()} sin dispersar recursos en demasiadas apuestas."
            ),
            "route_type": "where_to_play",
            "why_this_route": f"Concentra el aprendizaje en {channel_name} y evita dispersar el caso en demasiadas apuestas paralelas.",
            "criteria_fit": criteria[0] if criteria else "",
            "key_bets": [
                f"{channel_name} puede generar senal suficiente sin sobredimensionar el esfuerzo inicial.",
                "La oferta puede volverse concreta lo bastante rapido para sostener una primera recomendacion.",
            ],
            "key_risks": [
                "La ruta puede terminar pareciendo una tactica aislada si no se conecta con una tesis mas amplia.",
                "Una mala lectura del canal puede sesgar la recomendacion demasiado pronto.",
            ],
            "what_must_be_true": [
                "El canal inicial debe producir evidencia util, no solo actividad.",
                "El mensaje debe responder mejor que hoy a la principal objecion del comprador.",
            ],
            "recommended": True,
        }
    )

    alternatives.append(
        {
            "alternative_id": "proof-first",
            "label": "Ruta de prueba y credibilidad",
            "thesis": (
                f"Reforzar primero la prueba visible, los entregables y la credibilidad de {service_name.lower()} "
                "antes de exigirle mas volumen al sistema comercial."
            ),
            "route_type": "how_to_win",
            "why_this_route": "Prioriza credibilidad y reduccion de escepticismo antes de ampliar volumen comercial.",
            "criteria_fit": criteria[min(1, len(criteria) - 1)] if criteria else "",
            "key_bets": [
                "Una prueba mejor articulada puede aumentar conversion incluso sin cambiar de canal.",
                "La confianza del comprador esta mas limitada por especificidad que por awareness.",
            ],
            "key_risks": [
                "Puede retrasar demasiado el aprendizaje si se convierte en perfeccionismo de materiales.",
            ],
            "what_must_be_true": [
                "La falta de prueba visible es realmente un cuello de botella central.",
            ],
            "recommended": False,
        }
    )

    alternatives.append(
        {
            "alternative_id": "narrow-offer",
            "label": "Ruta de oferta acotada",
            "thesis": f"Reducir el alcance inicial de {service_name.lower()} para bajar friccion de compra y subir velocidad de validacion.",
            "route_type": "how_to_win",
            "why_this_route": "Busca una entrada mas facil de comprar antes de vender la version completa.",
            "criteria_fit": criteria[min(2, len(criteria) - 1)] if criteria else "",
            "key_bets": [
                "Una oferta mas pequena puede abrir la puerta a casos mas grandes despues.",
            ],
            "key_risks": [
                "Reducir demasiado el alcance puede destruir la diferenciacion o la economia del caso.",
            ],
            "what_must_be_true": [
                "El comprador valora una primera compra de bajo riesgo mas que una solucion integral desde el inicio.",
            ],
            "recommended": False,
        }
    )

    if readiness["status"] == "ready":
        alternatives.append(
            {
                "alternative_id": "relationship-led",
                "label": "Ruta de relacion y referidos",
                "thesis": "Usar relaciones existentes o referidos como entrada mientras se fortalece la tesis comercial principal.",
                "route_type": "right_to_win",
                "why_this_route": "Reduce riesgo de canal frio y aprovecha confianza previa para aprender mas rapido.",
                "criteria_fit": criteria[min(3, len(criteria) - 1)] if criteria else "",
                "key_bets": [
                    "La confianza previa puede compensar una tesis comercial todavia inmadura.",
                ],
                "key_risks": [
                    "Puede ocultar que la propuesta todavia no gana sola en mercado abierto.",
                ],
                "what_must_be_true": [
                    "Existe una red suficientemente fuerte como para producir aprendizaje util y no solo ruido anecdotal.",
                ],
                "recommended": False,
            }
        )

    if dominant_objection:
        alternatives[0]["key_bets"].append(f"La objecion dominante '{dominant_objection}' puede atacarse mejor desde una ruta enfocada.")

    return alternatives[:4]


def strategic_stack(payload: dict, readiness: dict, actions: list[str], criteria: list[str]) -> dict:
    alternatives = strategic_alternatives(payload, readiness, actions, criteria)
    recommended = next((item for item in alternatives if item.get("recommended")), alternatives[0] if alternatives else {})
    what_must_be_true = []
    for item in alternatives:
        if item.get("recommended"):
            what_must_be_true.extend(item.get("what_must_be_true", []))
    no_regret_moves = unique_preserve(actions[:2] + [
        "Separar hechos, inferencias y supuestos antes de escalar la recomendacion.",
        "Definir una senal temprana que invalide o refuerce la ruta elegida.",
    ])
    return {
        "problem_statement": strategic_problem_statement(payload, readiness),
        "case_for_change": strategic_case_for_change(payload, readiness),
        "where_to_play": strategic_where_to_play(payload),
        "how_to_win": strategic_how_to_win(payload),
        "right_to_win": strategic_right_to_win(payload, readiness),
        "strategic_alternatives": alternatives,
        "what_must_be_true": unique_preserve(what_must_be_true),
        "no_regret_moves": no_regret_moves,
        "recommended_route": {
            "alternative_id": recommended.get("alternative_id", ""),
            "label": recommended.get("label", ""),
            "thesis": recommended.get("thesis", ""),
            "why_this_route_wins": recommended.get("why_this_route", ""),
            "invalidation_conditions": unique_preserve(recommended.get("key_risks", [])),
        },
    }


def option_label(action: str, fallback: str) -> str:
    lowered = action.lower()
    if "precio" in lowered:
        return "Opcion enfocada en precio"
    if "med" in lowered or "conversion" in lowered:
        return "Opcion enfocada en medicion"
    if "evidencia" in lowered or "valid" in lowered:
        return "Opcion enfocada en validacion"
    if "canal" in lowered or "prueba" in lowered or "lanz" in lowered:
        return "Opcion enfocada en ejecucion"
    return fallback


def readiness_check(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    evidence_count = int(payload.get("evidence_count", 0) or 0)
    source_count = int(payload.get("source_count", 0) or 0)
    has_icp = bool(payload.get("has_icp", False))
    has_offer = bool(payload.get("has_offer", False))
    market_confidence = float(payload.get("market_confidence", 0) or 0)
    pricing_confidence = float(payload.get("pricing_confidence", 0) or 0)
    channel_confidence = float(payload.get("channel_confidence", 0) or 0)

    minimum_evidence_met = evidence_count >= 5
    source_diversity_met = source_count >= 2
    service_defined = has_offer
    icp_defined = has_icp
    channel_defined = channel_confidence >= 0.6
    insight_density = (market_confidence + pricing_confidence + channel_confidence) / 3 >= 0.6

    blockers = []
    if not minimum_evidence_met:
        blockers.append("Agrega al menos 5 evidencias antes de tomar una decision importante.")
    if not source_diversity_met:
        blockers.append("Agrega al menos 2 fuentes distintas para subir la confianza de lectura.")
    if not service_defined:
        blockers.append("Aclara mejor la oferta antes de recomendar ejecucion.")
    if not icp_defined:
        blockers.append("Define mejor a quien compras antes de elegir canal o precio.")
    if not channel_defined:
        blockers.append("Fortalece la confianza en el canal antes de ejecutar.")
    if not insight_density:
        blockers.append("La confianza en mercado, precio y canal sigue siendo demasiado baja.")

    score = round(
        (
            (1 if minimum_evidence_met else 0)
            + (1 if source_diversity_met else 0)
            + (1 if service_defined else 0)
            + (1 if icp_defined else 0)
            + (1 if channel_defined else 0)
            + (1 if insight_density else 0)
        )
        / 6,
        2,
    )
    return {
        "company_id": company_id,
        "score": score,
        "status": "ready" if not blockers else "blocked",
        "minimum_evidence_met": minimum_evidence_met,
        "source_diversity_met": source_diversity_met,
        "service_defined": service_defined,
        "icp_defined": icp_defined,
        "channel_defined": channel_defined,
        "insight_density": insight_density,
        "fact_base": [
            f"Evidencias disponibles: {evidence_count}.",
            f"Fuentes distintas disponibles: {source_count}.",
            f"Comprador principal definido: {'si' if has_icp else 'no'}.",
            f"Oferta definida: {'si' if has_offer else 'no'}.",
        ],
        "assumptions": [
            f"Confianza en mercado estimada en {market_confidence:.0%}.",
            f"Confianza en precio estimada en {pricing_confidence:.0%}.",
            f"Confianza en canal estimada en {channel_confidence:.0%}.",
        ],
        "blocking_reasons": blockers,
    }


def rank_next_actions(payload: dict, readiness: dict) -> list[str]:
    business_goal = str(payload.get("business_goal", "")).strip() or "mejorar la calidad de conversion"
    channel_name = str(payload.get("primary_channel", "")).strip() or "el canal con mejor senal actual"
    service_name = str(payload.get("offer_name", "") or payload.get("service_name", "")).strip() or "la oferta principal"
    country_name = str(payload.get("country_name", "")).strip() or "Mexico"
    dominant_objection = str(payload.get("dominant_objection", "")).strip()
    actions = []
    if readiness["blocking_reasons"]:
        if not readiness["minimum_evidence_met"]:
            actions.append("Recolecta mas evidencia de compradores antes de comprometer ejecucion o gasto.")
        if not readiness["icp_defined"]:
            actions.append("Valida mejor quien compra, como compra y que objecion aparece primero.")
        if not readiness["service_defined"]:
            actions.append("Aterriza mejor la oferta y explica con claridad como se entrega el servicio.")
        if not readiness["channel_defined"]:
            actions.append(f"Confirma con evidencia real si {channel_name} es el primer canal que conviene trabajar.")
        if not readiness["insight_density"]:
            actions.append("Fortalece la confianza en mercado y precio antes de pasar a una prueba mas ambiciosa.")
        return actions

    if dominant_objection:
        actions.append(
            f"Lanza una primera prueba comercial en {channel_name} para mejorar {business_goal.lower()} "
            f"y responder de frente a la objecion '{dominant_objection}'."
        )
    else:
        actions.append(
            f"Lanza una primera prueba comercial en {channel_name} para {service_name.lower()} "
            f"y mejorar {business_goal.lower()} en {country_name}."
        )
    actions.append("Prueba el rango de precio objetivo con alcance explicito, entregables visibles y prueba concreta.")
    actions.append("Mide calidad de conversion durante 30 dias, no solo volumen de leads o reuniones.")
    return actions


def build_decision_memo(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    readiness = readiness_check(payload)
    actions = rank_next_actions(payload, readiness)
    confidence = round(
        min(
            0.95,
            0.35
            + float(payload.get("market_confidence", 0) or 0) * 0.2
            + float(payload.get("pricing_confidence", 0) or 0) * 0.2
            + float(payload.get("channel_confidence", 0) or 0) * 0.2,
        ),
        2,
    )
    timestamp = now_iso()
    business_goal = str(payload.get("business_goal", "")).strip() or "Reducir incertidumbre y elegir el siguiente movimiento mas util."
    criteria = decision_criteria(payload)
    question = decision_question(payload)
    fact_base = list(readiness["fact_base"])
    assumptions = list(readiness["assumptions"])
    fact_base.extend(str(item).strip() for item in payload.get("validated_fact_lines", []) if str(item).strip())
    assumptions.extend(str(item).strip() for item in payload.get("assumption_lines", []) if str(item).strip())
    if web_only_payload(payload):
        public_claims = [str(item).strip() for item in payload.get("public_claims", []) if str(item).strip()]
        known_unknowns = [str(item).strip() for item in payload.get("known_unknowns", []) if str(item).strip()]
        offer_anchor = first_non_empty(payload.get("offer_anchor", ""))
        if offer_anchor:
            fact_base.append(offer_anchor)
        for claim in public_claims:
            fact_base.append(f"Claim publico visible: {claim}.")
        assumptions.extend(known_unknowns)
    fact_base = unique_preserve(fact_base)
    assumptions = unique_preserve(assumptions)

    if readiness["status"] == "blocked":
        decision_type = "viability"
        recommended_action = actions[0] if actions else "Resuelve primero el bloqueo con mayor impacto sobre la decision."
        why_now = "Todavia no hay suficiente contexto validado para recomendar ejecucion con seguridad."
        risks = readiness["blocking_reasons"]
        validation_gaps = list(readiness["blocking_reasons"])
    else:
        decision_type = "go_to_market"
        recommended_action = ""
        why_now = "El sistema ya tiene evidencia y confianza suficientes para proponer un siguiente movimiento enfocado."
        risks = [
            "La ejecucion puede fallar si la oferta sigue sonando mas abstracta que concreta.",
            "La hipotesis de canal todavia debe validarse con datos tempranos de conversion.",
        ]
        validation_gaps = list(risks)

    strategic_model = strategic_stack(payload, readiness, actions, criteria)
    if readiness["status"] == "ready":
        recommended_action = strategic_model["recommended_route"]["thesis"]
        why_now = strategic_model["recommended_route"]["why_this_route_wins"]
        risks = unique_preserve(
            strategic_model["recommended_route"]["invalidation_conditions"]
            + risks
        )
        validation_gaps = unique_preserve(
            strategic_model["what_must_be_true"] + validation_gaps
        )

    options = []
    for alternative in strategic_model.get("strategic_alternatives", []):
        options.append(
            {
                "label": alternative.get("label", "Opcion estrategica"),
                "summary": alternative.get("thesis", ""),
                "recommended": bool(alternative.get("recommended")),
                "criteria_fit": alternative.get("criteria_fit", ""),
            }
        )

    return {
        "decision_id": f"{company_id}-{slugify_id(decision_type)}-memo",
        "company_id": company_id,
        "decision_type": decision_type,
        "decision_question": question,
        "recommended_action": recommended_action,
        "decision_summary": business_goal,
        "why_now": why_now,
        "decision_criteria": criteria,
        "fact_base": fact_base,
        "assumptions": assumptions,
        "strategic_stack": strategic_model,
        "options": options,
        "alternative_actions": [
            item.get("thesis", "")
            for item in strategic_model.get("strategic_alternatives", [])
            if not item.get("recommended") and item.get("thesis")
        ],
        "key_risks": risks,
        "implementation_risks": list(risks),
        "validation_gaps": validation_gaps,
        "next_steps": unique_preserve(strategic_model.get("no_regret_moves", []) + actions),
        "status": "inferred" if readiness["status"] == "ready" else "needs_validation",
        "confidence": confidence,
        "source_origin": "decision_engine",
        "evidence_refs": [str(item).strip() for item in payload.get("evidence_refs", []) if str(item).strip()],
        "source_refs": [str(item).strip() for item in payload.get("source_refs", []) if str(item).strip()],
        "assumption_refs": [f"{company_id}-decision-assumption-readiness"],
        "finding_refs": [],
        "validated_fact_refs": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def persist_decision_memo(root: Path, payload: dict) -> Path:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    memo = build_decision_memo(payload)
    path = layout.record_path("decisions", company_id, memo["decision_id"])
    layout.write_json_atomic(path, memo)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and persist a decision memo from JSON.")
    parser.add_argument("input", help="JSON fixture path")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()
    print(persist_decision_memo(Path(args.root).resolve(), json.loads(Path(args.input).read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
