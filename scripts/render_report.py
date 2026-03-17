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
    return first_non_empty(
        bundle.get("current_thesis", ""),
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
    if facts:
        return unique_preserve(facts)
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
    assumption_lines = [str(item).strip() for item in bundle.get("assumptions", []) if str(item).strip()]
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


def validation_gaps(bundle: dict) -> list[str]:
    items = [str(item).strip() for item in bundle.get("validation_gaps", []) if str(item).strip()]
    items.extend(contrary_evidence(bundle))
    if not items:
        items.append("Valida primero la calidad de conversion antes de escalar gasto en canal o alcance de entrega.")
    return unique_preserve(items)


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


def executive_memo(bundle: dict) -> str:
    company = bundle["company"]
    decision = bundle["decision_memo"]
    return "\n".join(
        [
            "# Memo Ejecutivo",
            "",
            "## Empresa",
            "",
            company["name"],
            "",
            "## Pregunta de decision",
            "",
            decision_question(bundle),
            "",
            "## Tesis actual",
            "",
            current_thesis(bundle),
            "",
            "## Base de hechos",
            "",
            bullet_lines(fact_base(bundle)),
            "",
            "## Supuestos clave",
            "",
            bullet_lines(assumptions(bundle)),
            "",
            "## Opciones consideradas",
            "",
            bullet_lines(option_lines(bundle)),
            "",
            "## Criterios de recomendacion",
            "",
            bullet_lines(decision_criteria(bundle)),
            "",
            "## Recomendacion",
            "",
            decision["recommended_action"],
            "",
            "## Por que importa",
            "",
            decision["why_now"],
            "",
            "## Riesgos y evidencia en contra",
            "",
            bullet_lines(contrary_evidence(bundle)),
            "",
            "## Traceability",
            "",
            bullet_lines(traceability_lines(bundle)),
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
    return "\n".join(
        [
            "# Diagnostico de Negocio",
            "",
            "## Problema central",
            "",
            company["seed_summary"],
            "",
            "## Tesis actual",
            "",
            current_thesis(bundle),
            "",
            "## Lo que sabemos",
            "",
            bullet_lines(fact_base(bundle)),
            "",
            "## Lo que inferimos",
            "",
            bullet_lines(inferred_points(bundle)),
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
            bullet_lines(option_lines(bundle)),
            "",
            "## Realidades de ejecucion",
            "",
            bullet_lines(execution_realities(bundle)),
            "",
            "## Riesgos",
            "",
            bullet_lines(decision.get("key_risks", [])),
            "",
        ]
    )


def deck_outline(bundle: dict) -> str:
    plan = bundle["execution_plan"]
    lines = [
        "# Estructura de Presentacion",
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
        ]
    )


def render_bundle(bundle: dict) -> dict[str, str]:
    return {
        "executive-memo": executive_memo(bundle),
        "business-diagnosis": business_diagnosis(bundle),
        "deck-outline": deck_outline(bundle),
        "risk-memo": risk_memo(bundle),
    }


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
