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
    timestamp = now_iso()

    milestones = [
        {
            "milestone_id": "day-30",
            "name": next_steps[0] if len(next_steps) >= 1 else "Lanzar el primer experimento validado.",
            "timeframe": "Dias 1-30",
            "owner": "Fundador",
            "dependencies": [decision_id] if decision_id else [],
            "success_metric": "Primera ejecucion lanzada con mensaje claro y seguimiento activo.",
            "learning_goal": "Aprender si el movimiento de entrada recomendado produce senal creible del comprador con rapidez.",
            "risk_watchouts": validation_gaps[:1] or risks[:1],
        },
        {
            "milestone_id": "day-60",
            "name": next_steps[1] if len(next_steps) >= 2 else "Refinar precio y oferta con base en datos tempranos.",
            "timeframe": "Dias 31-60",
            "owner": "Fundador",
            "dependencies": ["day-30"],
            "success_metric": "Oferta, precio y objeciones actualizados con retroalimentacion real.",
            "learning_goal": "Usar objeciones y primeras victorias para afinar alcance, prueba y logica de precio.",
            "risk_watchouts": validation_gaps[1:2] or risks[1:2],
        },
        {
            "milestone_id": "day-90",
            "name": next_steps[2] if len(next_steps) >= 3 else "Consolidar una guia operativa repetible.",
            "timeframe": "Dias 61-90",
            "owner": "Fundador",
            "dependencies": ["day-60"],
            "success_metric": "Calidad de conversion medida y siguiente decision de canal documentada.",
            "learning_goal": "Decidir si conviene escalar, refinar o descartar la jugada actual.",
            "risk_watchouts": validation_gaps[2:3] or risks[:1],
        }
    ]
    workstreams = [
        {
            "name": "Validacion de demanda",
            "focus": milestones[0]["name"],
            "owner": "Fundador",
        },
        {
            "name": "Refinamiento de oferta y precio",
            "focus": milestones[1]["name"],
            "owner": "Fundador",
        },
        {
            "name": "Revision de decision",
            "focus": milestones[2]["name"],
            "owner": "Fundador",
        },
    ]
    sequence_rationale = [
        "Empieza por la accion de mayor confianza antes de ampliar alcance.",
        "Usa retroalimentacion real del mercado para afinar precio y promesa de entrega.",
        "Escala solo cuando entiendas la calidad de conversion y la friccion de implementacion.",
    ]

    return {
        "plan_id": f"{company_id}-{slugify_id('30-60-90-plan')}",
        "company_id": company_id,
        "plan_horizon": "30-60-90",
        "objective": objective,
        "milestones": milestones,
        "workstreams": workstreams,
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
