#!/usr/bin/env python3
"""30/60/90 execution planner for Codex Business OS MX."""

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


def summarize_milestone(
    milestone_id: str,
    timeframe: str,
    initiatives: list[dict],
    default_name: str,
    default_goal: str,
    fallback_risks: list[str],
) -> dict:
    active = [item for item in initiatives if item.get("timeframe") == timeframe]
    first = active[0] if active else {}
    owner = first.get("owner", "Fundador")
    dependencies = unique_preserve([dependency for item in active for dependency in item.get("dependencies", [])])
    success_metric = " / ".join(item.get("success_metric", "") for item in active if item.get("success_metric")) or default_goal
    learning_goal = " / ".join(item.get("decision_trigger", "") for item in active if item.get("decision_trigger")) or default_goal
    risk_watchouts = unique_preserve([risk for item in active for risk in item.get("key_risks", [])])[:2] or fallback_risks[:2]
    name = " + ".join(item.get("name", "") for item in active if item.get("name")) or default_name
    return {
        "milestone_id": milestone_id,
        "name": name,
        "timeframe": timeframe,
        "owner": owner,
        "dependencies": dependencies,
        "success_metric": success_metric,
        "learning_goal": learning_goal,
        "risk_watchouts": risk_watchouts,
    }


def build_execution_plan(payload: dict) -> dict:
    company_id = str(payload.get("company_id", "")).strip()
    if not company_id:
        raise ValueError("company_id is required")

    decision_memo = payload.get("decision_memo", {})
    decision_id = str(decision_memo.get("decision_id", "")).strip()
    objective = str(decision_memo.get("decision_summary", "")).strip() or "Ejecutar el siguiente movimiento validado con mejor perfil."
    next_steps = [str(item).strip() for item in decision_memo.get("next_steps", []) if str(item).strip()]
    risks = [str(item).strip() for item in decision_memo.get("key_risks", []) if str(item).strip()]
    validation_gaps = [str(item).strip() for item in decision_memo.get("validation_gaps", []) if str(item).strip()]
    options = decision_memo.get("options", [])
    strategic_stack = decision_memo.get("strategic_stack", {})
    no_regret_moves = [str(item).strip() for item in strategic_stack.get("no_regret_moves", []) if str(item).strip()]
    strategic_alternatives = strategic_stack.get("strategic_alternatives", [])
    recommended_route = strategic_stack.get("recommended_route", {})
    route_label = str(recommended_route.get("label", "")).strip() or "Ruta recomendada"
    route_thesis = str(recommended_route.get("thesis", "")).strip() or "Definir una ruta recomendada con mejor perfil de aprendizaje."
    route_win = str(recommended_route.get("why_this_route_wins", "")).strip() or "La ruta elegida debe ganar por velocidad de aprendizaje y ajuste con capacidad real."
    invalidation_conditions = [
        str(item).strip()
        for item in recommended_route.get("invalidation_conditions", [])
        if str(item).strip()
    ]
    what_must_be_true = [str(item).strip() for item in strategic_stack.get("what_must_be_true", []) if str(item).strip()]
    timestamp = now_iso()
    initiative_roadmap = [
        {
            "initiative_id": "initiative-problem-structuring",
            "name": f"Alinear problema, tesis y alcance de {route_label.lower()}",
            "workstream": "Alineacion estrategica",
            "objective": "Traducir la recomendacion a una tesis operativa entendible por el fundador y por el comprador.",
            "owner": "Fundador",
            "timeframe": "Dias 1-30",
            "dependencies": [decision_id] if decision_id else [],
            "leading_indicator": "Narrativa comercial y criterios de decision entendidos por el fundador sin contradicciones internas.",
            "lagging_indicator": "Oferta, objeciones y entregables sintetizados en una sola lectura ejecutiva consistente.",
            "success_metric": "Tesis, problema del comprador y propuesta de entrada alineados en un solo memo ejecutivo.",
            "stage_gate": "Gate 1",
            "stage_gate_question": "La ruta elegida esta lo bastante clara como para probarse sin interpretaciones distintas dentro del equipo?",
            "key_risks": unique_preserve(validation_gaps[:1] + invalidation_conditions[:1]),
            "risk_mitigation": unique_preserve(no_regret_moves[:2] + ["Separar hechos, inferencias y supuestos antes de mover recursos."])[:3],
            "decision_trigger": "Si la tesis sigue cambiando en cada conversacion, el caso aun no esta listo para ir al mercado.",
            "exit_criteria": "Existe una lectura unica del problema, de la oferta de entrada y de la senal que confirmaria o invalidaria la ruta.",
        },
        {
            "initiative_id": "initiative-route-validation",
            "name": f"Validar la {route_label.lower()} en el mercado",
            "workstream": "Validacion de demanda",
            "objective": route_thesis,
            "owner": "Fundador",
            "timeframe": "Dias 1-30",
            "dependencies": ["initiative-problem-structuring"],
            "leading_indicator": "Senales tempranas de respuesta calificada en el canal escogido.",
            "lagging_indicator": "Conversaciones comerciales con una objecion dominante mas clara y menos friccion de entrada.",
            "success_metric": "La ruta elegida genera una senal mas fuerte que al menos una alternativa en velocidad y calidad de aprendizaje.",
            "stage_gate": "Gate 2",
            "stage_gate_question": "La ruta recomendada ya demuestra una ventaja real frente a las rutas alternativas?",
            "key_risks": unique_preserve(invalidation_conditions[:2] + risks[:1]),
            "risk_mitigation": unique_preserve(no_regret_moves + next_steps[:1])[:4],
            "decision_trigger": route_win,
            "exit_criteria": "Existe evidencia suficiente para sostener que el canal y la entrada elegidos merecen una segunda ronda de inversion operativa.",
        },
        {
            "initiative_id": "initiative-economics-proof",
            "name": "Defender economia, precio y condiciones de conversion",
            "workstream": "Economia y propuesta",
            "objective": "Confirmar que la ruta recomendada puede sostener margen, credibilidad y una entrega repetible.",
            "owner": "Fundador",
            "timeframe": "Dias 31-60",
            "dependencies": ["initiative-route-validation"],
            "leading_indicator": "Objeciones de precio y alcance se vuelven mas especificas y menos frecuentes.",
            "lagging_indicator": "Rango de precio defendible y criterios de cierre mejoran sin erosionar margen.",
            "success_metric": "Precio, alcance y prueba visible quedan defendibles frente al comprador real.",
            "stage_gate": "Gate 3",
            "stage_gate_question": "La economia del caso ya aguanta escalar esta ruta sin destruir margen o credibilidad?",
            "key_risks": unique_preserve(risks[:2] + validation_gaps[1:2]),
            "risk_mitigation": unique_preserve(next_steps[1:3] + ["Revisar riesgos y senales lider al cierre de cada ciclo de feedback."])[:4],
            "decision_trigger": "Si precio y prueba no se sostienen juntos, la ruta debe refinarse antes de escalar.",
            "exit_criteria": "Existe una combinacion defendible de precio, alcance, narrativa y prueba para sostener la oferta.",
        },
        {
            "initiative_id": "initiative-scale-or-pivot",
            "name": "Decidir escala, ajuste o cambio de ruta",
            "workstream": "Gobierno de decision",
            "objective": "Usar la evidencia de los primeros 90 dias para sostener, refinar o reemplazar la ruta elegida.",
            "owner": "Fundador",
            "timeframe": "Dias 61-90",
            "dependencies": ["initiative-economics-proof"],
            "leading_indicator": "Los indicadores lider y las condiciones what-must-be-true evolucionan a favor de la tesis.",
            "lagging_indicator": "La ruta mantiene conversion, economia y facilidad de ejecucion mejores que sus alternativas.",
            "success_metric": "Existe una decision documentada de escalar, ajustar o redirigir basada en evidencia comparada.",
            "stage_gate": "Gate 4",
            "stage_gate_question": "La evidencia acumulada confirma la tesis o obliga a cambiar de ruta?",
            "key_risks": unique_preserve(invalidation_conditions + risks),
            "risk_mitigation": unique_preserve(
                ["Comparar la ruta recomendada contra las alternativas con los mismos criterios de decision."]
                + no_regret_moves
            )[:4],
            "decision_trigger": "Si las condiciones what-must-be-true no se cumplen, la siguiente decision no es escalar sino reencuadrar.",
            "exit_criteria": "La empresa sabe que ruta sostener, que ruta descartar y que aprendizaje se incorpora al siguiente ciclo.",
        },
    ]

    milestones = [
        summarize_milestone(
            "day-30",
            "Dias 1-30",
            initiative_roadmap,
            next_steps[0] if len(next_steps) >= 1 else "Alinear tesis y validar la primera ruta.",
            "Validar si la ruta recomendada genera senal creible de mercado.",
            validation_gaps or risks,
        ),
        summarize_milestone(
            "day-60",
            "Dias 31-60",
            initiative_roadmap,
            next_steps[1] if len(next_steps) >= 2 else "Defender economia y precio de la ruta.",
            "Confirmar si precio, alcance y prueba sostienen la ruta elegida.",
            risks,
        ),
        summarize_milestone(
            "day-90",
            "Dias 61-90",
            initiative_roadmap,
            next_steps[2] if len(next_steps) >= 3 else "Decidir si conviene escalar o redirigir la ruta.",
            "Tomar una decision de escala o cambio con evidencia comparada.",
            invalidation_conditions or risks,
        ),
    ]
    workstreams = [
        {
            "name": "Alineacion estrategica",
            "focus": initiative_roadmap[0]["name"],
            "owner": "Fundador",
        },
        {
            "name": "Validacion de demanda",
            "focus": initiative_roadmap[1]["name"],
            "owner": "Fundador",
        },
        {
            "name": "Economia y propuesta",
            "focus": initiative_roadmap[2]["name"],
            "owner": "Fundador",
        },
        {
            "name": "Gobierno de decision",
            "focus": initiative_roadmap[3]["name"],
            "owner": "Fundador",
        },
    ]
    sequence_rationale = [
        "Primero se alinea la tesis y se traduce a una lectura operativa comun para evitar ejecucion incoherente.",
        "Despues se valida la ruta elegida en mercado antes de invertir en ajustes mas profundos de economia.",
        "Luego se defiende precio, alcance y prueba para que la ruta tenga soporte economico y comercial.",
        "Solo al final se decide si conviene escalar, ajustar o cambiar de ruta con base en evidencia comparada.",
    ]

    decision_checkpoints = [
        "Comprobar si la ruta recomendada sigue ganando frente a las alternativas en calidad de aprendizaje y capacidad de ejecucion.",
        "Revisar periodicamente si los riesgos de invalidacion siguen siendo tolerables o ya cambiaron la tesis.",
        "No escalar hasta que precio, prueba y conversion se sostengan al mismo tiempo.",
        "Cerrar cada gate con una decision explicita: sostener, ajustar o redirigir la ruta.",
    ]

    return {
        "plan_id": f"{company_id}-{slugify_id('30-60-90-plan')}",
        "company_id": company_id,
        "plan_horizon": "30-60-90",
        "objective": objective,
        "milestones": milestones,
        "workstreams": workstreams,
        "initiative_roadmap": initiative_roadmap,
        "decision_checkpoints": decision_checkpoints,
        "no_regret_moves": unique_preserve(no_regret_moves),
        "strategic_alternatives": strategic_alternatives,
        "validation_agenda": unique_preserve(validation_gaps or risks),
        "sequence_rationale": sequence_rationale,
        "options_considered": options,
        "decision_refs": [decision_id] if decision_id else [],
        "risk_refs": [f"{company_id}-risk-{index + 1}" for index, _ in enumerate(risks)],
        "status": "inferred",
        "confidence": 0.72,
        "source_origin": "planner",
        "evidence_refs": [],
        "source_refs": [],
        "created_at": timestamp,
        "updated_at": timestamp
    }


def persist_execution_plan(root: Path, payload: dict) -> Path:
    layout = WorkspaceLayout(root=root)
    company_id = str(payload.get("company_id", "")).strip()
    layout.ensure_company_workspace(company_id)
    plan = build_execution_plan(payload)
    path = layout.record_path("plans", company_id, plan["plan_id"])
    layout.write_json_atomic(path, plan)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and persist a 30/60/90 execution plan from JSON.")
    parser.add_argument("input", help="JSON fixture path")
    parser.add_argument("--root", default=".", help="Project root for persistence")
    args = parser.parse_args()
    print(persist_execution_plan(Path(args.root).resolve(), json.loads(Path(args.input).read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
