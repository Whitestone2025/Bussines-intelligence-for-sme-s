#!/usr/bin/env python3
"""Render consulting-grade markdown deliverables from canonical objects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workspace import WorkspaceLayout, slugify_id


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- Sin dato"


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


def normalize_public_text(text: str) -> str:
    normalized = str(text or "")
    replacements = [
        ("founder", "fundador"),
        ("Founder", "Fundador"),
        ("economics", "economia"),
        ("Economics", "Economia"),
        ("open source", "codigo abierto"),
        ("Open source", "Codigo abierto"),
        ("venture hybrid", "hibrido de venture capital"),
        ("Venture hybrid", "Hibrido de venture capital"),
        ("right to win", "derecho a ganar"),
        ("Right to win", "Derecho a ganar"),
        ("go-to-market", "salida al mercado"),
        ("Go-to-market", "Salida al mercado"),
        ("buyer problem", "problema del comprador"),
        ("Buyer problem", "Problema del comprador"),
        ("unit economics", "economia unitaria"),
        ("Unit economics", "Economia unitaria"),
        ("proof", "prueba"),
        ("Proof", "Prueba"),
    ]
    for old, new in replacements:
        normalized = normalized.replace(old, new)
    return normalized


def document_purpose(document_id: str) -> str:
    purposes = {
        "executive-memo": "Te sirve para entender la tesis actual del caso en una sola lectura y decidir si vale la pena profundizar, corregir o pausar la ruta recomendada.",
        "business-diagnosis": "Te sirve para separar lo que hoy sabemos del negocio, lo que seguimos infiriendo y lo que todavia necesita validacion antes de mover recursos.",
        "problem-structuring-memo": "Te sirve para ordenar el caso antes de discutir tacticas, dejando claro cual es el problema central, que tension lo explica y que preguntas siguen abiertas.",
        "strategic-options-memo": "Te sirve para comparar rutas reales entre si y evitar que el caso colapse demasiado pronto en una sola accion.",
        "decision-document": "Te sirve para documentar la decision provisional, por que gana hoy y bajo que condiciones deberia cambiarse.",
        "initiative-roadmap": "Te sirve para convertir la tesis elegida en una secuencia de gates, indicadores y riesgos, no solo en una lista de tareas.",
        "founder-narrative": "Te sirve para explicar el caso sin sobreprometer, manteniendo coherencia entre problema, ruta elegida y lo que todavia no esta probado.",
        "deck-outline": "Te sirve para estructurar una conversacion ejecutiva o una presentacion sin perder la logica del caso.",
        "risk-memo": "Te sirve para revisar donde el caso puede fallar y que senales deberian disparar una correccion de rumbo.",
    }
    return purposes.get(document_id, "Te sirve para leer el caso con una logica mas util para decidir.")


def evidence_limits(bundle: dict) -> list[str]:
    company = bundle.get("company", {})
    decision = bundle.get("decision_memo", {})
    limits = [str(item).strip() for item in company.get("known_constraints", []) if str(item).strip()]
    for item in decision.get("validation_gaps", []):
        normalized = str(item).strip()
        if normalized and (
            normalized.lower().startswith("agrega")
            or normalized.lower().startswith("aclara")
            or normalized.lower().startswith("define")
            or normalized.lower().startswith("fortalece")
            or "confianza" in normalized.lower()
        ):
            limits.append(normalized)
    if not limits:
        limits.append("La evidencia actual sigue siendo insuficiente para convertir esta lectura en una verdad cerrada.")
    return unique_preserve(limits)


def decision_question(bundle: dict) -> str:
    company = bundle["company"]
    offer = bundle["offer"]
    decision = bundle["decision_memo"]
    return first_non_empty(
        bundle.get("decision_question", ""),
        decision.get("decision_summary", ""),
        f"Cual es el siguiente movimiento de mayor confianza para que {company['name']} valide y haga crecer la oferta {offer['name']} en Mexico?",
    )


def current_thesis(bundle: dict) -> str:
    company = bundle["company"]
    icp = bundle["icp"]
    offer = bundle["offer"]
    decision = bundle["decision_memo"]
    stack = canonical_strategic_stack(bundle)
    route = stack.get("recommended_route", {})
    return first_non_empty(
        bundle.get("current_thesis", ""),
        route.get("thesis", ""),
        (
            f"{company['name']} debe liderar con {offer['name']} para {icp['label']} porque los compradores responden a "
            "claridad, una entrega transparente y un primer experimento de adquisicion enfocado."
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
    facts.extend(str(item).strip() for item in decision.get("fact_base", []) if str(item).strip())
    facts = unique_preserve(facts)
    if facts:
        return facts
    facts.extend(
        [
            company.get("seed_summary", ""),
            f"ICP principal: {icp['label']}.",
            f"Oferta en foco: {offer['name']} con la promesa '{offer['core_promise']}'.",
            f"Estimacion combinada de mercado para {market['segment_name']}: {money(market['currency_code'], market['blended_value'])}.",
            f"El precio objetivo hoy apunta a {money(pricing['currency_code'], pricing['price_target'])}.",
        ]
    )
    for proof_point in offer.get("proof_points", []):
        facts.append(f"Prueba visible: {proof_point}.")
    for evidence_ref in decision.get("evidence_refs", []):
        facts.append(f"Referencia de evidencia disponible: {evidence_ref}.")
    return unique_preserve(facts)


def assumptions(bundle: dict) -> list[str]:
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    decision = bundle["decision_memo"]
    assumption_lines = [str(item).strip() for item in bundle.get("assumptions", []) if str(item).strip()]
    assumption_lines.extend(str(item).strip() for item in decision.get("assumptions", []) if str(item).strip())
    assumption_lines.extend(str(item).strip() for item in market.get("key_assumptions", []) if str(item).strip())
    assumption_lines.extend(str(item).strip() for item in pricing.get("margin_assumptions", []) if str(item).strip())
    if not assumption_lines:
        assumption_lines.append("La recomendacion actual asume que el primer canal elegido puede validarse rapido con ejecucion liderada por el fundador.")
    return unique_preserve(assumption_lines)


def decision_criteria(bundle: dict) -> list[str]:
    criteria = [str(item).strip() for item in bundle.get("decision_criteria", []) if str(item).strip()]
    if criteria:
        return unique_preserve(criteria)
    return [
        "Velocidad para obtener una senal real de mercado en Mexico.",
        "Ajuste de confianza para compradores de servicios liderados por el fundador.",
        "Economia que proteja margen sin romper la credibilidad de la oferta.",
        "Simplicidad de ejecucion para un fundador con ancho de banda limitado.",
    ]


def contrary_evidence(bundle: dict) -> list[str]:
    decision = bundle["decision_memo"]
    items = [str(item).strip() for item in bundle.get("contrary_evidence", []) if str(item).strip()]
    items.extend(str(item).strip() for item in decision.get("key_risks", []) if str(item).strip())
    return unique_preserve(items)


def canonical_strategic_stack(bundle: dict) -> dict:
    decision = bundle["decision_memo"]
    stack = decision.get("strategic_stack", {})
    if stack:
        return stack
    return {
        "problem_statement": {
            "headline": decision_question(bundle),
            "situation": bundle["company"].get("seed_summary", ""),
            "complication": first_non_empty(*decision.get("validation_gaps", [])),
            "decision_tension": decision.get("why_now", ""),
            "key_question": decision_question(bundle),
        },
        "case_for_change": {
            "why_change": decision.get("why_now", ""),
            "cost_of_inaction": first_non_empty(*contrary_evidence(bundle)),
            "transformation_story": "El caso necesita una recomendacion mas clara que una simple lista de tareas.",
        },
        "where_to_play": {
            "primary_segment": bundle["icp"].get("label", ""),
            "primary_channel": bundle.get("channel", {}).get("name", ""),
            "geographic_focus": bundle["company"].get("primary_country", "Mexico"),
        },
        "how_to_win": {
            "value_thesis": bundle["offer"].get("core_promise", ""),
            "differentiation": bundle["offer"].get("mechanism", ""),
            "proof": first_non_empty(*bundle["offer"].get("proof_points", [])),
        },
        "right_to_win": unique_preserve(bundle["offer"].get("proof_points", []) + bundle["icp"].get("desired_outcomes", []))[:4],
        "strategic_alternatives": build_options(bundle),
        "what_must_be_true": unique_preserve(validation_gaps(bundle))[:4],
        "no_regret_moves": unique_preserve(decision.get("next_steps", []))[:3],
        "recommended_route": {
            "label": "Ruta recomendada",
            "thesis": decision.get("recommended_action", ""),
        },
    }


def strategic_alternative_lines(bundle: dict) -> list[str]:
    lines: list[str] = []
    for option in canonical_strategic_stack(bundle).get("strategic_alternatives", []):
        label = option.get("label", "Alternativa")
        thesis = option.get("thesis") or option.get("summary", "")
        prefix = "Recomendada" if option.get("recommended") else "Alternativa"
        lines.append(f"{prefix}: {label} -> {thesis}")
        for item in option.get("what_must_be_true", [])[:2]:
            lines.append(f"  Debe ser cierto: {item}")
        for item in option.get("key_risks", [])[:2]:
            lines.append(f"  Riesgo: {item}")
    return lines


def validation_gaps(bundle: dict) -> list[str]:
    items = [str(item).strip() for item in bundle.get("validation_gaps", []) if str(item).strip()]
    items.extend(contrary_evidence(bundle))
    if not items:
        items.append("Valida primero la calidad de conversion antes de escalar gasto en canal o alcance de entrega.")
    return unique_preserve(items)


def problem_structuring_map(bundle: dict) -> dict:
    stack = canonical_strategic_stack(bundle)
    problem = stack.get("problem_statement", {})
    case_for_change = stack.get("case_for_change", {})
    route = stack.get("recommended_route", {})
    recommendation = first_non_empty(route.get("thesis", ""), bundle["decision_memo"].get("recommended_action", ""))
    return {
        "problem_headline": first_non_empty(problem.get("headline", ""), decision_question(bundle)),
        "facts": fact_base(bundle),
        "inferences": inferred_points(bundle),
        "assumptions": assumptions(bundle),
        "contrary_evidence": contrary_evidence(bundle),
        "recommendation": recommendation,
        "what_must_be_true": unique_preserve(
            stack.get("what_must_be_true", []) + validation_gaps(bundle)
        )[:6],
        "case_for_change": [
            f"Por que cambiar: {case_for_change.get('why_change', '')}",
            f"Costo de no hacer nada: {case_for_change.get('cost_of_inaction', '')}",
        ],
    }


def route_thesis(bundle: dict) -> str:
    stack = canonical_strategic_stack(bundle)
    route = stack.get("recommended_route", {})
    return first_non_empty(route.get("thesis", ""), bundle["decision_memo"].get("recommended_action", ""))


def route_rationale(bundle: dict) -> str:
    stack = canonical_strategic_stack(bundle)
    route = stack.get("recommended_route", {})
    return first_non_empty(route.get("why_this_route_wins", ""), bundle["decision_memo"].get("why_now", ""))


def next_validation_step(bundle: dict) -> str:
    decision = bundle["decision_memo"]
    route_text = route_thesis(bundle)
    for item in decision.get("next_steps", []):
        normalized = str(item).strip()
        if normalized and normalized != route_text:
            return normalized
    return first_non_empty(*decision.get("validation_gaps", []))


def inferred_points(bundle: dict) -> list[str]:
    decision = bundle["decision_memo"]
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    inferences = [str(item).strip() for item in bundle.get("inferences", []) if str(item).strip()]
    if inferences:
        return unique_preserve(inferences)
    inferences.extend(
        [
            f"El mercado parece suficientemente atractivo para probarse porque el modelo actual estima {money(market['currency_code'], market['blended_value'])} de valor combinado.",
            f"El corredor de precio viable hoy se mueve entre {money(pricing['currency_code'], pricing['price_floor'])} y {money(pricing['currency_code'], pricing['price_ceiling'])}.",
            f"La recomendacion actual sigue siendo una hipotesis viva con {decision.get('confidence', 0):.0%} de confianza.",
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
            "El fundador es el responsable por defecto durante los primeros 90 dias, asi que el plan debe mantenerse ligero y secuencial.",
            "Cada hito depende del aprendizaje del paso anterior antes de ampliar alcance o gasto.",
        ]
    )
    for milestone in plan.get("milestones", []):
        owner = str(milestone.get("owner", "Fundador")).strip() or "Fundador"
        realities.append(f"{milestone['timeframe']}: {owner} debe lograr '{milestone['success_metric']}'.")
    return unique_preserve(realities)


def build_options(bundle: dict) -> list[dict]:
    provided = bundle.get("options", [])
    if provided:
        normalized = []
        for index, option in enumerate(provided, start=1):
            normalized.append(
                {
                    "label": first_non_empty(option.get("label", ""), f"Opcion {index}"),
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
            "label": "Ruta recomendada",
            "summary": decision["recommended_action"],
            "pros": [
                f"Mejor ajuste contra el criterio principal actual: {criteria[0]}",
                f"Respaldada por la logica actual del por que ahora: {decision['why_now']}",
            ],
            "cons": contrary_evidence(bundle)[:2],
            "recommended": True,
        }
    ]
    for index, action in enumerate(decision.get("alternative_actions", []), start=1):
        options.append(
            {
                "label": f"Alternativa {index}",
                "summary": action,
                "pros": [
                    "Crea una via creible de respaldo si el experimento principal rinde por debajo de lo esperado.",
                ],
                "cons": [
                    "Es una via mas lenta para obtener senal que el movimiento recomendado.",
                ],
                "recommended": False,
            }
        )
    return options


def roadmap_lines(bundle: dict) -> list[str]:
    plan = bundle["execution_plan"]
    lines: list[str] = []
    for initiative in plan.get("initiative_roadmap", []):
        lines.append(f"{initiative['stage_gate']}: {initiative['name']} -> {initiative['objective']}")
        lines.append(f"  Indicador lider: {initiative.get('leading_indicator', '')}")
        lines.append(f"  Indicador rezagado: {initiative.get('lagging_indicator', '')}")
        lines.append(f"  Trigger de decision: {initiative.get('decision_trigger', '')}")
    return lines


def option_lines(bundle: dict) -> list[str]:
    lines: list[str] = []
    for option in build_options(bundle):
        prefix = "Recomendada" if option["recommended"] else "Alternativa"
        lines.append(f"{prefix}: {option['label']} -> {option['summary']}")
        for item in option.get("pros", []):
            lines.append(f"  Ventaja: {item}")
        for item in option.get("cons", []):
            lines.append(f"  Compromiso: {item}")
    return lines


def traceability_lines(bundle: dict) -> list[str]:
    decision = bundle["decision_memo"]
    market = bundle["market_model"]
    pricing = bundle["pricing_model"]
    refs = []
    refs.extend(f"Evidencia: {item}" for item in decision.get("evidence_refs", []))
    refs.extend(f"Supuesto: {item}" for item in market.get("assumption_refs", []))
    refs.extend(f"Supuesto: {item}" for item in pricing.get("assumption_refs", []))
    refs.extend(f"Supuesto de decision: {item}" for item in decision.get("assumption_refs", []))
    return unique_preserve(refs)


def problem_structuring_memo(bundle: dict) -> str:
    stack = canonical_strategic_stack(bundle)
    problem = stack.get("problem_statement", {})
    structuring = problem_structuring_map(bundle)
    return "\n".join(
        [
            "# Memo de Problema Estructurado",
            "",
            "## Para que sirve este documento",
            "",
            document_purpose("problem-structuring-memo"),
            "",
            "## Pregunta que estamos resolviendo",
            "",
            decision_question(bundle),
            "",
            "## Problema central",
            "",
            structuring["problem_headline"],
            "",
            "## Situacion",
            "",
            problem.get("situation", "Sin situacion."),
            "",
            "## Complicacion",
            "",
            problem.get("complication", "Sin complicacion."),
            "",
            "## Tension de decision",
            "",
            problem.get("decision_tension", "Sin tension de decision."),
            "",
            "## Hechos validados",
            "",
            bullet_lines(structuring["facts"]),
            "",
            "## Inferencias principales",
            "",
            bullet_lines(structuring["inferences"]),
            "",
            "## Supuestos de trabajo",
            "",
            bullet_lines(structuring["assumptions"]),
            "",
            "## Lo que tendria que ser cierto",
            "",
            bullet_lines(structuring["what_must_be_true"]),
            "",
            "## Limites de evidencia hoy",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
        ]
    )


def strategic_options_memo(bundle: dict) -> str:
    stack = canonical_strategic_stack(bundle)
    recommended_id = stack.get("recommended_route", {}).get("alternative_id", "")
    lines = [
        "# Memo de Opciones Estrategicas",
        "",
        "## Para que sirve este documento",
        "",
        document_purpose("strategic-options-memo"),
        "",
        "## Criterios de decision",
        "",
        bullet_lines(decision_criteria(bundle)),
        "",
    ]
    for option in stack.get("strategic_alternatives", []):
        is_recommended = bool(option.get("recommended")) or (
            recommended_id and option.get("alternative_id") == recommended_id
        )
        label = option.get("label", "Alternativa")
        prefix = f"## Ruta recomendada - {label}" if is_recommended else f"## {label}"
        lines.extend(
            [
                prefix,
                "",
                option.get("thesis", ""),
                "",
                "### Por que considerar esta ruta",
                "",
                option.get("why_this_route", ""),
                "",
                "### Apuestas clave",
                "",
                bullet_lines(option.get("key_bets", [])),
                "",
                "### Riesgos clave",
                "",
                bullet_lines(option.get("key_risks", [])),
                "",
                "### Lo que tendria que ser cierto",
                "",
                bullet_lines(option.get("what_must_be_true", [])),
                "",
            ]
        )
    lines.extend(
        [
            "## Limites de evidencia hoy",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
        ]
    )
    return "\n".join(lines)


def initiative_roadmap_memo(bundle: dict) -> str:
    plan = bundle["execution_plan"]
    lines = [
        "# Roadmap de Iniciativas",
        "",
        "## Para que sirve este documento",
        "",
        document_purpose("initiative-roadmap"),
        "",
        "## Objetivo del roadmap",
        "",
        plan.get("objective", "Sin objetivo."),
        "",
        "## Checkpoints de decision",
        "",
        bullet_lines(plan.get("decision_checkpoints", [])),
        "",
    ]
    for initiative in plan.get("initiative_roadmap", []):
        lines.extend(
            [
                f"## {initiative.get('stage_gate', 'Gate')} - {initiative.get('name', 'Iniciativa')}",
                "",
                initiative.get("objective", ""),
                "",
                "### Workstream y dependencias",
                "",
                bullet_lines(
                    [
                        f"Workstream: {initiative.get('workstream', '')}",
                        f"Owner: {initiative.get('owner', '')}",
                        f"Timeframe: {initiative.get('timeframe', '')}",
                    ]
                    + [f"Dependency: {item}" for item in initiative.get("dependencies", [])]
                ),
                "",
                "### Indicadores y gates",
                "",
                bullet_lines(
                    [
                        f"Indicador lider: {initiative.get('leading_indicator', '')}",
                        f"Indicador rezagado: {initiative.get('lagging_indicator', '')}",
                        f"Stage gate question: {initiative.get('stage_gate_question', '')}",
                        f"Decision trigger: {initiative.get('decision_trigger', '')}",
                        f"Exit criteria: {initiative.get('exit_criteria', '')}",
                    ]
                ),
                "",
                "### Riesgos y mitigacion",
                "",
                bullet_lines(initiative.get("key_risks", []) + initiative.get("risk_mitigation", [])),
                "",
            ]
        )
    lines.extend(
        [
            "## Limites de evidencia hoy",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
        ]
    )
    return "\n".join(lines)


def founder_narrative(bundle: dict) -> str:
    company = bundle["company"]
    offer = bundle["offer"]
    stack = canonical_strategic_stack(bundle)
    route = stack.get("recommended_route", {})
    route_message = route.get("thesis", bundle["decision_memo"].get("recommended_action", ""))
    route_reason = route.get("why_this_route_wins", bundle["decision_memo"].get("why_now", ""))
    return "\n".join(
        [
            "# Narrativa del Founder",
            "",
            "## Para que sirve este documento",
            "",
            document_purpose("founder-narrative"),
            "",
            "## Como explicar el problema",
            "",
            f"Hoy en {company['name']} estamos resolviendo este problema: {stack.get('problem_statement', {}).get('headline', decision_question(bundle))}",
            "",
            "## Como explicar la ruta elegida",
            "",
            f"La ruta que estamos recomendando es esta: {route_message}",
            "",
            "## Por que esta ruta y no otra",
            "",
            route_reason,
            "",
            "## Que decir en conversaciones",
            "",
            bullet_lines(
                [
                    f"No presentamos {offer['name']} como una verdad cerrada; la usamos para validar si {offer.get('core_promise', '').lower()}.",
                    "La prioridad no es escalar rapido sino encontrar la ruta con mejor aprendizaje y mejor economia.",
                    "Si una condicion clave no se cumple, cambiamos de ruta en lugar de forzar la narrativa.",
                ]
            ),
            "",
            "## Que no sobreprometer",
            "",
            bullet_lines(
                [
                    "No presentar la recomendacion como verdad final si todavia depende de supuestos importantes.",
                    "No vender escala antes de demostrar conversion, economia y capacidad de entrega.",
                    "No esconder los riesgos principales cuando el comprador necesita entender el proceso.",
                ]
            ),
            "",
            "## La siguiente conversacion correcta",
            "",
            bullet_lines(bundle["execution_plan"].get("decision_checkpoints", [])[:3]),
            "",
            "## Lo que todavia no podemos prometer",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
        ]
    )


def decision_document(bundle: dict) -> str:
    stack = canonical_strategic_stack(bundle)
    route = stack.get("recommended_route", {})
    return "\n".join(
        [
            "# Documento de Decision",
            "",
            "## Para que sirve este documento",
            "",
            document_purpose("decision-document"),
            "",
            "## Decision central",
            "",
            route.get("thesis", bundle["decision_memo"].get("recommended_action", "")),
            "",
            "## Por que gana esta ruta",
            "",
            route.get("why_this_route_wins", bundle["decision_memo"].get("why_now", "")),
            "",
            "## Condiciones de invalidez",
            "",
            bullet_lines(route.get("invalidation_conditions", bundle["decision_memo"].get("key_risks", []))),
            "",
            "## Opciones descartadas por ahora",
            "",
            bullet_lines([item.get("thesis", "") for item in stack.get("strategic_alternatives", []) if not item.get("recommended")]),
            "",
            "## Proximo gate",
            "",
            first_non_empty(*bundle["execution_plan"].get("decision_checkpoints", [])),
            "",
            "## Limites de evidencia hoy",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
        ]
    )


def executive_memo(bundle: dict) -> str:
    company = bundle["company"]
    decision = bundle["decision_memo"]
    stack = canonical_strategic_stack(bundle)
    problem = stack.get("problem_statement", {})
    case_for_change = stack.get("case_for_change", {})
    where_to_play = stack.get("where_to_play", {})
    how_to_win = stack.get("how_to_win", {})
    structuring = problem_structuring_map(bundle)
    return "\n".join(
        [
            "# Memo Ejecutivo",
            "",
            "## Para que sirve este documento",
            "",
            document_purpose("executive-memo"),
            "",
            "## Empresa",
            "",
            company["name"],
            "",
            "## Pregunta de decision",
            "",
            decision_question(bundle),
            "",
            "## Problema estructurado",
            "",
            structuring["problem_headline"],
            "",
            bullet_lines(
                [
                    f"Situacion: {problem.get('situation', '')}",
                    f"Complicacion: {problem.get('complication', '')}",
                    f"Tension de decision: {problem.get('decision_tension', '')}",
                ]
            ),
            "",
            "## Hechos validados",
            "",
            bullet_lines(structuring["facts"]),
            "",
            "## Inferencias principales",
            "",
            bullet_lines(structuring["inferences"]),
            "",
            "## Supuestos de trabajo",
            "",
            bullet_lines(structuring["assumptions"]),
            "",
            "## Caso para cambiar",
            "",
            bullet_lines(
                structuring["case_for_change"]
                + [f"Historia del cambio: {case_for_change.get('transformation_story', '')}"]
            ),
            "",
            "## Opciones consideradas",
            "",
            bullet_lines(strategic_alternative_lines(bundle)),
            "",
            "## Donde jugar y como ganar",
            "",
            bullet_lines(
                [
                    f"Donde jugar: {where_to_play.get('primary_segment', '')} via {where_to_play.get('primary_channel', '')} en {where_to_play.get('geographic_focus', '')}.",
                    f"Como ganar: {how_to_win.get('value_thesis', '')}",
                    f"Derecho a ganar: {first_non_empty(*stack.get('right_to_win', []))}",
                ]
            ),
            "",
            "## Criterios de recomendacion",
            "",
            bullet_lines(decision_criteria(bundle)),
            "",
            "## Ruta provisional recomendada",
            "",
            route_thesis(bundle),
            "",
            "## Por que gana hoy esta ruta",
            "",
            route_rationale(bundle),
            "",
            "## Siguiente validacion necesaria",
            "",
            next_validation_step(bundle),
            "",
            "## Riesgos y evidencia en contra",
            "",
            bullet_lines(contrary_evidence(bundle)),
            "",
            "## Lo que tendria que ser cierto",
            "",
            bullet_lines(structuring["what_must_be_true"]),
            "",
            "## Movimientos sin arrepentimiento",
            "",
            bullet_lines(stack.get("no_regret_moves", [])),
            "",
            "## Trazabilidad",
            "",
            bullet_lines(traceability_lines(bundle)),
            "",
            "## Limites de evidencia hoy",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
            "## Siguientes acciones inmediatas",
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
    stack = canonical_strategic_stack(bundle)
    problem = stack.get("problem_statement", {})
    structuring = problem_structuring_map(bundle)
    return "\n".join(
        [
            "# Diagnostico de Negocio",
            "",
            "## Para que sirve este documento",
            "",
            document_purpose("business-diagnosis"),
            "",
            "## Problema central",
            "",
            structuring["problem_headline"],
            "",
            bullet_lines(
                [
                    f"Situacion: {problem.get('situation', company['seed_summary'])}",
                    f"Complicacion: {problem.get('complication', '')}",
                    f"Pregunta clave: {problem.get('key_question', decision_question(bundle))}",
                ]
            ),
            "",
            "## Tesis actual",
            "",
            current_thesis(bundle),
            "",
            "## Lo que sabemos",
            "",
            bullet_lines(structuring["facts"]),
            "",
            "## Lo que inferimos",
            "",
            bullet_lines(structuring["inferences"]),
            "",
            "## Supuestos de trabajo",
            "",
            bullet_lines(structuring["assumptions"]),
            "",
            "## Lo que aun necesita validacion",
            "",
            bullet_lines(validation_gaps(bundle)),
            "",
            "## ICP",
            "",
            icp["label"],
            "",
            "## Oferta",
            "",
            f"{offer['name']}: {offer['core_promise']}",
            "",
            "## Mercado",
            "",
            f"{market['segment_name']} con tamano combinado estimado de {market['currency_code']} {market['blended_value']:,.2f}",
            "",
            "## Precio",
            "",
            f"Precio objetivo: {pricing['currency_code']} {pricing['price_target']:,.2f}",
            "",
            "## Opciones estrategicas",
            "",
            bullet_lines(strategic_alternative_lines(bundle)),
            "",
            "## Recomendacion actual",
            "",
            structuring["recommendation"],
            "",
            "## Lo que tendria que ser cierto",
            "",
            bullet_lines(structuring["what_must_be_true"]),
            "",
            "## Realidades de ejecucion",
            "",
            bullet_lines(execution_realities(bundle)),
            "",
            "## Riesgos",
            "",
            bullet_lines(decision.get("key_risks", [])),
            "",
            "## Limites de evidencia hoy",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
        ]
    )


def deck_outline(bundle: dict) -> str:
    plan = bundle["execution_plan"]
    lines = [
        "# Estructura de Presentacion",
        "",
        "## Para que sirve este documento",
        "",
        document_purpose("deck-outline"),
        "",
        "1. Tesis y pregunta de decision",
        "2. Problema central y restricciones",
        "3. Base de hechos",
        "4. Tamano y atractivo del mercado",
        "5. Logica de precio y economia",
        "6. Opciones consideradas",
        "7. Criterios de recomendacion",
        "8. Recomendacion y riesgos",
        "9. Plan 30/60/90",
        "10. Agenda de validacion",
        "",
        "## Hitos 30/60/90",
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
        risk_lines.append(f"Riesgo: {risk}")
        risk_lines.append("  Responsable: Fundador")
        risk_lines.append("  Senal temprana: observa objeciones, baja calidad de conversion o incapacidad de explicar alcance con rapidez.")
    mitigations = unique_preserve(
        [
            "Usa lenguaje respaldado por evidencia y prueba visible.",
            "Valida canales con experimentos de bajo costo antes de escalar.",
            "Revisa precio y objeciones cada 30 dias.",
            *validation_gaps(bundle),
        ]
    )
    return "\n".join(
        [
            "# Memo de Riesgos",
            "",
            "## Para que sirve este documento",
            "",
            document_purpose("risk-memo"),
            "",
            "## Evidencia en contra y alertas",
            "",
            bullet_lines(contrary_evidence(bundle)),
            "",
            "## Registro de riesgos",
            "",
            bullet_lines(risk_lines),
            "",
            "## Plan de mitigacion",
            "",
            bullet_lines(mitigations),
            "",
            "## Limites de evidencia hoy",
            "",
            bullet_lines(evidence_limits(bundle)),
            "",
        ]
    )


def render_bundle(bundle: dict) -> dict[str, str]:
    rendered = {
        "executive-memo": executive_memo(bundle),
        "business-diagnosis": business_diagnosis(bundle),
        "problem-structuring-memo": problem_structuring_memo(bundle),
        "strategic-options-memo": strategic_options_memo(bundle),
        "decision-document": decision_document(bundle),
        "initiative-roadmap": initiative_roadmap_memo(bundle),
        "founder-narrative": founder_narrative(bundle),
        "deck-outline": deck_outline(bundle),
        "risk-memo": risk_memo(bundle),
    }
    return {key: normalize_public_text(value) for key, value in rendered.items()}


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
